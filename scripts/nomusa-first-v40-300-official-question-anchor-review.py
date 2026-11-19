#!/usr/bin/env python3
"""V40 · 2020/21 A-form official-PDF question-location REVIEW pipeline.

Produces a 300-item visual-inspection packet, NOT a graded question bank.
Existing V38 OCR page guesses are evidence candidates, never approvals.
Original 4 Q-Net PDFs must match the fixed V61 SHA-256 before any inspection.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import fitz
import pytesseract
import requests
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "study-hub/legacy-first-v61-sources.js"
EXISTING = ROOT / "review/NOMUSA_FIRST_V38_88_NATIVE_PAGE_SOURCE_20261118.json"
OUTPUT = ROOT / "review-artifacts/NOMUSA_FIRST_V40"
CROPS = OUTPUT / "source_question_location_previews"
EXPECTED = ("2020-A-management", "2020-A-economics",
            "2021-A-management", "2021-A-economics")
ID_RE = re.compile(r"^legacy1-(2020|2021)-A-[a-z0-9]+-(\d{3})$")
NUM_RE = re.compile(r"^(\d{1,3})[.)．]$")
HEAD_RE = re.compile(r"^\s*(\d{1,3})\s*[.．)]")
HOLD_FIELDS = {
    "exactQuestionTextMatched": False,
    "optionSequenceVisuallyMatched": False,
    "formulaOrGraphicVerified": False,
    "officialAnswerKeyIndependentlyApproved": False,
    "legalBasisIndependentlyApproved": False,
    "readyForQDATAImport": False,
    "scoringApproved": False,
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_ledger():
    src = INDEX.read_text(encoding="utf-8")
    return json.loads(src[src.index("{"):src.rfind(";")])


def native_anchors(page):
    """Use original PDF text first, without OCR when usable."""
    anchors = []
    for block in page.get_text("dict")["blocks"]:
        for line in block.get("lines", []):
            spans = line.get("spans", [])
            if not spans:
                continue
            txt = "".join(s.get("text", "") for s in spans).strip()
            m = HEAD_RE.match(txt)
            if not m:
                continue
            no = int(m.group(1))
            x, y = float(line["bbox"][0]), float(line["bbox"][1])
            if 1 <= no <= 125 and 20 < y < page.rect.height - 25 and 15 < x < 0.38 * page.rect.width:
                anchors.append({"number": no, "x": round(x, 1), "y": round(y, 1),
                                "kind": "PDF_NATIVE_TEXT", "sample": txt[:65]})
    return anchors


def ocr_anchors(page):
    """Image-based numeric heading localization, never answer/OCR transcription."""
    scale = 2.0
    pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale),
                          colorspace=fitz.csGRAY, alpha=False)
    image = Image.open(io.BytesIO(pix.tobytes("png")))
    data = pytesseract.image_to_data(
        image, lang="kor+eng", config="--oem 1 --psm 11",
        output_type=pytesseract.Output.DICT
    )
    anchors = []
    for i, token in enumerate(data["text"]):
        m = NUM_RE.match(token.strip())
        if not m or int(data["conf"][i]) < 30:
            continue
        no = int(m.group(1))
        x = data["left"][i] / scale
        y = data["top"][i] / scale
        if not (1 <= no <= 125 and 20 < y < page.rect.height - 25
                and 15 < x < 0.38 * page.rect.width):
            continue
        anchors.append({"number": no, "x": round(x, 1), "y": round(y, 1),
                        "kind": "OCR_NUMBER_GUESS", "ocrConfidence": round(float(data["conf"][i]), 1)})
    return anchors


def anchors_for_page(page):
    native = native_anchors(page)
    if len({a["number"] for a in native}) >= 2:
        return native, "PDF_NATIVE_TEXT"
    guessed = ocr_anchors(page)
    return (guessed, "OCR_NUMBER_GUESS") if guessed else (native, "PDF_NATIVE_TEXT_WEAK")


def crop_for_review(doc, pdf_page, anchor, page_anchors, name):
    """Produce a provisional visual crop; spanning-page questions remain HOLD."""
    p = doc[pdf_page - 1]
    y = anchor["y"]
    following = [a["y"] for a in page_anchors
                 if a["y"] > y + 20 and abs(a["x"] - anchor["x"]) < 40]
    bottom = min(following) - 6 if following else p.rect.height - 30
    bottom = min(p.rect.height - 15, max(bottom, y + 65))
    box = fitz.Rect(20, max(0, y - 10), p.rect.width - 20, bottom)
    if box.height < 55:
        return None
    pix = p.get_pixmap(matrix=fitz.Matrix(1.85, 1.85), clip=box,
                        colorspace=fitz.csRGB, alpha=False)
    blob = pix.tobytes("jpeg", jpg_quality=82)
    path = CROPS / (name + ".jpg")
    path.write_bytes(blob)
    return {"file": path.name, "jpegSHA256": sha256(blob),
            "cropPDFPoints": [round(v, 2) for v in box],
            "note": "CROP_IS_ONLY_FOR_VISUAL_REVIEW_MAY_CROSS_PAGE_OR_CONTAIN_UNVERIFIED_OPTIONS"}


def main():
    ledger = read_ledger()
    manifest = json.loads(EXISTING.read_text(encoding="utf-8"))
    assert manifest["OCRPageCandidates"] == 274
    assert manifest["bookletOnlyHOLD"] == 26
    assert manifest["uniqueImagePages"] == 88
    groups = defaultdict(list)
    for key, rec in ledger["records"].items():
        m = ID_RE.match(key)
        if m:
            groups[rec["source"]].append((key, int(m.group(2)), rec))
    assert set(groups) == set(EXPECTED)
    assert sum(map(len, groups.values())) == 300

    OUTPUT.mkdir(parents=True, exist_ok=True)
    CROPS.mkdir(parents=True, exist_ok=True)
    docs = {x["key"]: x for x in manifest["sourceDocuments"]}
    assert set(docs) == set(EXPECTED)
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0",
                            "Referer": "https://www.q-net.or.kr/"})
    rows, coverage = [], []
    for source in EXPECTED:
        spec = ledger["documents"][source]
        resp = session.get(spec["download"], timeout=100)
        resp.raise_for_status()
        binary = resp.content
        assert binary.startswith(b"%PDF"), source + "_NON_PDF"
        assert sha256(binary) == spec["sha256"] == docs[source]["pdfSHA256"], source + "_PDF_SHA_CHANGED"
        doc = fitz.open(stream=binary, filetype="pdf")
        assert len(doc) == spec["pdfPages"] == docs[source]["pageCount"]
        # Verify each of the 88 existing rendered original pages against the V38 manifest.
        page_images = {x["page"]: x for x in docs[source]["images"]}
        for page_no, info in page_images.items():
            path = ROOT / "study-hub/first-v38-qnet-pages-2020-2021" / info["image"]
            assert path.exists(), "V38_ORIGINAL_JPEG_NOT_FOUND_" + path.name
            assert sha256(path.read_bytes()) == info["sha256"], "V38_JPEG_SHA_CHANGED_" + path.name
        anchors = {}
        methods = {}
        for page_no in range(1, len(doc) + 1):
            a, method = anchors_for_page(doc[page_no - 1])
            anchors[page_no] = a
            methods[page_no] = method
        source_rows = []
        for item_id, number, rec in groups[source]:
            candidate_page = rec.get("pdfPage") if rec["status"] == "OCR_PAGE_CANDIDATE" else None
            if candidate_page is not None:
                assert candidate_page in page_images, item_id + "_NO_V38_PAGE"
            matches = [(p, a) for p, found in anchors.items() for a in found if a["number"] == number]
            on_page = [(p, a) for p, a in matches if p == candidate_page]
            page_set = sorted(set(p for p, _ in matches))
            if candidate_page and len(on_page) == 1:
                state = "SINGLE_NUMBER_ANCHOR_ON_CANDIDATE_PAGE_REVIEW"
            elif candidate_page and len(on_page) > 1:
                state = "MULTIPLE_SAME_NUMBER_ANCHORS_REVIEW"
            elif matches:
                state = "PAGE_CONFLICT_OR_UNLOCATED_REVIEW"
            else:
                state = "NUMBER_ANCHOR_NOT_DETECTED_HOLD"
            crop = None
            if candidate_page and len(on_page) == 1:
                crop = crop_for_review(doc, candidate_page, on_page[0][1],
                                       anchors[candidate_page], item_id)
            record = {
                "id": item_id, "year": int(item_id.split("-")[1]),
                "questionNumber": number, "form": "A", "source": source,
                "originalPdfSHA256": spec["sha256"],
                "officialSourceURL": spec["download"],
                "v38OcrCandidatePage": candidate_page,
                "numberAnchorReviewState": state,
                "anchorMethodForCandidatePage": methods.get(candidate_page),
                "allDetectedNumberPageCandidates": page_set,
                "onV38CandidatePageAnchors": [a for _, a in on_page],
                "provisionalQuestionVisualCrop": crop,
                "independentHumanReview": "HOLD",
                **HOLD_FIELDS
            }
            source_rows.append(record)
        rows.extend(source_rows)
        coverage.append({
            "source": source, "sourceSHA256": spec["sha256"], "pdfPages": len(doc),
            "count": len(source_rows),
            "v38PageCandidates": sum(x["v38OcrCandidatePage"] is not None for x in source_rows),
            "numberAnchorOnCandidatePage": sum(x["numberAnchorReviewState"] == "SINGLE_NUMBER_ANCHOR_ON_CANDIDATE_PAGE_REVIEW" for x in source_rows),
            "locationHOLD": sum(x["v38OcrCandidatePage"] is None for x in source_rows),
            "croppedForReview": sum(x["provisionalQuestionVisualCrop"] is not None for x in source_rows)
        })
        doc.close()

    assert len(rows) == len({r["id"] for r in rows}) == 300
    assert sum(r["v38OcrCandidatePage"] is not None for r in rows) == 274
    assert sum(r["v38OcrCandidatePage"] is None for r in rows) == 26
    assert all(not r["readyForQDATAImport"] and not r["scoringApproved"] for r in rows)
    report = {
        "schema": "NOMUSA_FIRST_V40_2020_21_ANCHOR_REVIEW/1",
        "status": "PASS_SOURCE_INTEGRITY_REVIEW_PACKET_ONLY",
        "description": "OCR/numeric anchors are hints, NOT individually verified full five-option questions",
        "totalCandidates": 300, "v38PageCandidates": 274,
        "v38UnlocatedHOLD": 26, "sourcePDFSHAValidated": 4,
        "sourceJPEG_SHAValidated": 88,
        "numberAnchorMatchesAwaitingVisualCheck": sum(
            r["numberAnchorReviewState"] == "SINGLE_NUMBER_ANCHOR_ON_CANDIDATE_PAGE_REVIEW" for r in rows),
        "provisionalCrops": sum(r["provisionalQuestionVisualCrop"] is not None for r in rows),
        "officialQuestionTextIndependentlyApproved": 0,
        "officialAnswerKeyIndependentlyApproved": 0,
        "readyForQDATAImport": 0, "actuallyImportedToMainQDATA": 0,
        "scoringApproved": 0,
        "existing2279MainBankPreserved": True,
        "mainProductionModified": False, "coverage": coverage, "rows": rows
    }
    target = OUTPUT / "NOMUSA_FIRST_V40_300_ANCHOR_REVIEW.json"
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (OUTPUT / "NOMUSA_FIRST_V40_300_VISUAL_REVIEW_QUEUE.csv").open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(("id", "year", "questionNumber", "source", "v38Page",
                    "reviewState", "detectedNumberPages", "cropFile",
                    "fullOriginalStemOptionsReview", "gradingApproval"))
        for r in rows:
            w.writerow((r["id"], r["year"], r["questionNumber"], r["source"],
                        r["v38OcrCandidatePage"] or "",
                        r["numberAnchorReviewState"],
                        "|".join(map(str, r["allDetectedNumberPageCandidates"])),
                        (r["provisionalQuestionVisualCrop"] or {}).get("file", ""),
                        "HOLD", "HOLD"))
    print(json.dumps({k: v for k, v in report.items() if k not in ("rows",)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())

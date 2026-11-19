#!/usr/bin/env python3
"""V43/V46 conservative scanned-official-source batch examination.

V43: inspect all 103 V41 source images (priority lane).
V46: inventory the other 686 of 789 missing A-form IDs and inspect any SHA-proven
      source crops (e.g., V40 additional candidates, V42 two legal-law holds).

OCR is an untrusted transcription proposal, NEVER independent proof of five
choices, legal citations, answer grids, mathematical formulas, or publication.
"""
import argparse
import csv
import hashlib
import io
import json
from collections import Counter
from pathlib import Path

from PIL import Image
import pytesseract

ROOT = Path(__file__).resolve().parents[1]
V34 = ROOT / "review-artifacts/NOMUSA_FIRST_V34/NOMUSA_FIRST_V34_791_SOURCE_TARGETS.json"
V41 = ROOT / "review/NOMUSA_FIRST_V41_103_CROP_SHA_20261118.json"
V42 = ROOT / "review/NOMUSA_FIRST_V42_FOUR_MANUAL_CROP_REPAIRS_20261118.json"
PILOT = {"legacy1-2020-A-management-101", "legacy1-2021-A-management-110"}
PDF_DIR = ROOT / "review-artifacts/NOMUSA_FIRST_V42_OFFICIAL"
V40_DIR = ROOT / "review-artifacts/NOMUSA_FIRST_V40_IMPORTED"


def digest(buf):
    return hashlib.sha256(buf).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def official_references():
    original = load(PDF_DIR / "six-source-sha-manifest.json")
    assert original["officialSHA256Validated"] == 6
    by_sha, keys = {}, {}
    for source in original["pdfs"]:
        path = PDF_DIR / (source["key"] + ".pdf")
        assert path.is_file() and path.read_bytes().startswith(b"%PDF")
        assert digest(path.read_bytes()) == source["sha256"]
        assert source["pages"] > 0
        by_sha[source["sha256"]] = source
        keys[source["key"]] = source
    assert len(keys) == 6
    return by_sha, keys


def image_evidence(path, expected_sha):
    if not path.is_file():
        raise AssertionError(f"Missing image: {path}")
    blob = path.read_bytes()
    assert digest(blob) == expected_sha, f"Original JPEG changed {path}"
    im = Image.open(io.BytesIO(blob))
    im.verify()
    im = Image.open(io.BytesIO(blob))
    assert im.width >= 600 and im.height >= 70, f"Unreadable image {path}"
    return im, len(blob)


def ocr_review(im):
    try:
        text = pytesseract.image_to_string(im, lang="kor+eng", config="--oem 1 --psm 6")
        text = " ".join(text.replace("\r", "\n").split())
        return {
            "transcriptCandidate": text[:8000],
            "ocrCharacters": len(text),
            "ocrCircledMarkers": {x: text.count(x) for x in "①②③④⑤"},
            "ocrQuality": "UNVERIFIED_IMAGE_TRANSCRIPTION_ONLY",
            "exactQuestionAndOptionsVerified": False,
            "formulaTableOrGraphicVerified": False
        }
    except Exception as exc:
        return {"transcriptCandidate": "", "ocrCharacters": 0, "ocrQuality": "OCR_ERROR_REVIEW_REQUIRED",
                "ocrError": type(exc).__name__ + ": " + str(exc)[:140],
                "ocrCircledMarkers": {}, "exactQuestionAndOptionsVerified": False,
                "formulaTableOrGraphicVerified": False}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", choices=("v43", "v46"), required=True)
    args = ap.parse_args()
    queue = load(V34)
    assert queue["summary"]["totalTargets"] == 791
    assert queue["summary"]["existingQDATA"] == 2279
    queued = queue["rows"]
    assert len(queued) == len({r["id"] for r in queued}) == 791
    official_by_sha, official_keys = official_references()

    m41 = load(V41)
    records41 = {r["id"]: r for r in m41["files"]}
    assert len(records41) == 103 and m41["sourceCropsStagedForFurtherIndependentReview"] == 103
    assert len(set(records41) & PILOT) == 0

    fixes = {r["id"]: r for r in load(V42)["records"]}
    assert len(fixes) == 4 and PILOT.issubset(fixes.keys())
    v40_file = V40_DIR / "NOMUSA_FIRST_V40_300_ANCHOR_REVIEW.json"
    # V40 workflow artifact downloads can intermittently return GitHub "Bad credentials".
    # Never discard the 103 repo-preserved SHA-proven images for this optional source.
    v40rows = {}
    if v40_file.is_file():
        v40 = load(v40_file)
        assert v40["totalCandidates"] == 300 and v40["sourcePDFSHAValidated"] == 4
        v40rows = {r["id"]: r for r in v40["rows"]}
        assert len(v40rows) == 300

    missing = [r for r in queued if r["id"] not in PILOT]
    assert len(missing) == 789
    p43 = [r for r in missing if r["id"] in records41]
    p46 = [r for r in missing if r["id"] not in records41]
    assert len(p43) == 103 and len(p46) == 686
    wanted = p43 if args.phase == "v43" else p46
    result = []
    for r in wanted:
        qid = r["id"]
        assert qid not in PILOT
        image = None
        proof = None
        if qid in records41:
            rec = records41[qid]
            image = ROOT / rec["image"]
            proof = {"image": rec["image"], "sha256": rec["jpegSHA256"],
                     "officialPdfSHA256": rec["officialPdfSHA256"],
                     "pdfPage": rec["officialPDFPageCandidate"],
                     "origin": "V41_103_SHA_PROVEN_PRELIMINARY"}
        elif qid in fixes:
            rec = fixes[qid]
            image = ROOT / rec["originalQuestionImage"]
            proof = {"image": rec["originalQuestionImage"], "sha256": rec["sha256"],
                     "officialPdfSHA256": rec["sourcePdfSHA256"],
                     "pdfPage": rec["page"], "origin": "V42_MANUAL_CROP_REPAIRED_LAW_HOLD"}
        elif qid in v40rows:
            crop = v40rows[qid].get("provisionalQuestionVisualCrop")
            if crop and crop.get("file"):
                image = V40_DIR / "source_question_location_previews" / crop["file"]
                proof = {"image": str(image.relative_to(ROOT)),
                         "sha256": crop["jpegSHA256"],
                         "officialPdfSHA256": v40rows[qid]["originalPdfSHA256"],
                         "pdfPage": v40rows[qid]["v38OcrCandidatePage"],
                         "origin": "V40_UNTRIAGED_NUMBER_ANCHOR_HOLD"}
        if proof:
            assert proof["officialPdfSHA256"] == r["sourceDocumentSHA256"], "SOURCE_PDF_MISMATCH_" + qid
            assert proof["officialPdfSHA256"] in official_by_sha, "UNVERIFIED_QNET_PDF_" + qid
            im, size = image_evidence(image, proof["sha256"])
            review = ocr_review(im)
            review.update({"imageWidth": im.width, "imageHeight": im.height, "imageBytes": size})
            status = "OCR_REVIEW_REQUIRED_NOT_APPROVED"
        else:
            review = {"transcriptCandidate": "", "ocrCharacters": 0,
                      "ocrQuality": "NO_SHA_PROVEN_SINGLE_QUESTION_IMAGE",
                      "exactQuestionAndOptionsVerified": False,
                      "formulaTableOrGraphicVerified": False}
            status = ("QNET_PDF_LINKED_NO_SINGLE_QUESTION_CROP_HOLD" if r.get("sourceDocumentSHA256") in official_by_sha
                      else "OFFICIAL_QNET_NOTICE_ONLY_HOLD" if r.get("originalURL")
                      else "NO_SOURCE_LINK_HOLD")
        answer_pdf = official_keys.get(str(r["year"]) + "-AB-official-final-answers")
        result.append({
            "id": qid, "year": r["year"], "subject": r["subject"],
            "questionNumber": r["number"], "candidateAnswers": r["candidateAnswers"],
            "officialQuestionSource": r.get("originalURL"),
            "sourceAuthority": r["sourceAuthority"], "sourceStatus": r["sourceStatus"],
            "originalSourceImage": proof,
            "officialFinalAnswerSheetSHA256": answer_pdf["sha256"] if answer_pdf else None,
            "answerGridIndividualQuestionVisuallyApproved": False,
            "examDateLawOrTheoryBasisApproved": False,
            "allFiveOptionsAndMathVerified": False,
            "independentHumanContentApproval": False,
            "readyForQDATAImport": False, "scoringApproved": False,
            "status": status, "ocrEvidence": review
        })
    assert len(result) == (103 if args.phase == "v43" else 686)
    assert len({r["id"] for r in result}) == len(result)
    assert all(not row["scoringApproved"] and not row["readyForQDATAImport"] for row in result)
    out = ROOT / ("review-artifacts/NOMUSA_FIRST_V43" if args.phase == "v43"
                  else "review-artifacts/NOMUSA_FIRST_V46")
    out.mkdir(parents=True, exist_ok=True)
    statuses = Counter(x["status"] for x in result)
    by_year = Counter(str(x["year"]) for x in result)
    overview = {
        "schema": "NOMUSA_FIRST_" + args.phase.upper() + "_SCAN_REVIEW/1",
        "phase": args.phase, "targetCount": len(result),
        "priority103": 103, "other686": 686, "remainingOriginalMissing": 789,
        "sourceSixOfficialPDFShaPass": 6,
        "optionalV40RawArtifactAvailable": bool(v40rows),
        "optionalV40ArtifactAvailabilityDoesNotAffectSourceApprovals": True,
        "shaProvenImageCandidates": sum(bool(x["originalSourceImage"]) for x in result),
        "ocrReviewCandidateImages": sum(x["status"] == "OCR_REVIEW_REQUIRED_NOT_APPROVED" for x in result),
        "officialAnswerPDFFor2020_2021": sum(bool(x["officialFinalAnswerSheetSHA256"]) for x in result),
        "contentIndependentlyApproved": 0, "automaticNewQDATAApproval": 0,
        "status": "PASS_INTEGRITY_HOLD_CONTENT_PENDING",
        "byStatus": dict(sorted(statuses.items())), "byYear": dict(sorted(by_year.items())),
        "rows": result
    }
    dest = out / ("NOMUSA_FIRST_" + args.phase.upper() + "_SOURCE_REVIEW.json")
    dest.write_text(json.dumps(overview, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (out / ("NOMUSA_FIRST_" + args.phase.upper() + "_REVIEW_QUEUE.csv")).open(
            "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "year", "subject", "number", "source", "image", "sourceSHA",
                    "officialKeySheetSHA", "reviewStatus", "fullText", "fiveOptions",
                    "mathGraphic", "finalKey", "explanation", "scoring"])
        for q in result:
            ev = q["originalSourceImage"] or {}
            w.writerow([q["id"], q["year"], q["subject"], q["questionNumber"],
                        q["officialQuestionSource"] or "", ev.get("image", ""),
                        ev.get("officialPdfSHA256", ""), q["officialFinalAnswerSheetSHA256"] or "",
                        q["status"], "HOLD", "HOLD", "HOLD", "HOLD", "HOLD", "HOLD"])
    print(json.dumps({k: v for k,v in overview.items() if k != "rows"}, ensure_ascii=False))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""V48: advance 686 missing historical A-form questions only as far as sources allow.

- 193: four SHA-validated original 2020/21 Q-Net A PDFs, original-page image
  + conditional numbered crop (stored *only* as provisional reviewer evidence).
- 2: SHA-validated V42 legal-only repaired crops, no score approval.
- 314 notice-only / 177 no official source: explicit provenance HOLD, no text fabrication.
- Never turn candidate answer, OCR, source JPG, academic title or old ledger into
  independently reviewed original stem, verified A-form final key or grading.
Outputs one stable 686-row review manifest, CSV and conditional review-only JPG.
No app data, 1st/2nd answer files, V44 approval or production code is modified.
"""
from __future__ import annotations
import csv
import hashlib
import io
import json
import os
import re
from collections import Counter, defaultdict
from pathlib import Path

import fitz
from PIL import Image
import pytesseract

os.environ["OMP_THREAD_LIMIT"]="1"
ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "study-hub/legacy-first-v61-sources.js"
V34 = ROOT / "review-artifacts/NOMUSA_FIRST_V34/NOMUSA_FIRST_V34_791_SOURCE_TARGETS.json"
V41 = ROOT / "review/NOMUSA_FIRST_V41_103_CROP_SHA_20261118.json"
V42 = ROOT / "review/NOMUSA_FIRST_V42_FOUR_MANUAL_CROP_REPAIRS_20261118.json"
V38 = ROOT / "review/NOMUSA_FIRST_V38_88_NATIVE_PAGE_SOURCE_20261118.json"
OFFICIAL = ROOT / "review-artifacts/NOMUSA_FIRST_V42_OFFICIAL"
OUT = ROOT / "review-artifacts/NOMUSA_FIRST_V48"
CROPS = ROOT / "review/first-v48-provisional-crops"
HEAD_RE = re.compile(r"^\s*(\d{1,3})\s*[.)．)]")
NUM_RE = re.compile(r"^(\d{1,3})[.)．]$")
PILOTS = {"legacy1-2020-A-management-101","legacy1-2021-A-management-110"}

def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def digest(blob: bytes):
    return hashlib.sha256(blob).hexdigest()

def require(ok: bool, detail: str):
    if not ok:
        raise AssertionError("HOLD_V48_"+detail)

def native_heads(page):
    found=[]
    for b in page.get_text("dict")["blocks"]:
        for line in b.get("lines",[]):
            text="".join(s.get("text","") for s in line.get("spans",[])).strip()
            m=HEAD_RE.match(text)
            if m:
                number=int(m.group(1))
                x,y=line["bbox"][:2]
                if 1<=number<=125 and 15<x<page.rect.width*.40 and 20<y<page.rect.height-25:
                    found.append({"number":number,"x":round(x,1),"y":round(y,1),"method":"NATIVE_PDF_TEXT"})
    return found

def image_heads(im, source_page):
    # The image is the SHA-locked 1.85x original page from V38. Use OCR only
    # for candidate question-heading coordinates, not legal/text confirmation.
    try:
        data=pytesseract.image_to_data(
            im,lang="kor+eng",config="--oem 1 --psm 11",
            output_type=pytesseract.Output.DICT, timeout=22)
    except Exception as e:
        return [],type(e).__name__
    found=[]
    sx=source_page.rect.width/im.width
    sy=source_page.rect.height/im.height
    for i,t in enumerate(data["text"]):
        m=NUM_RE.match(t.strip())
        if not m:continue
        no=int(m.group(1))
        try:confidence=float(data["conf"][i])
        except (ValueError,TypeError):continue
        x=float(data["left"][i])*sx
        y=float(data["top"][i])*sy
        if confidence<35 or not (1<=no<=125 and 15<x<source_page.rect.width*.40 and 20<y<source_page.rect.height-25):
            continue
        found.append({"number":no,"x":round(x,1),"y":round(y,1),
                      "method":"OCR_HEADING_GUESS","confidence":round(confidence,1)})
    return found,None

def crop_review(doc, page_no, number, anchors, src_sha, name):
    page=doc[page_no-1]
    hits=[a for a in anchors if a["number"]==number]
    if len(hits)!=1:return None,"NUMBER_ANCHOR_NOT_UNIQUE_OR_MISSING"
    a=hits[0]; y=a["y"]
    after=[b["y"] for b in anchors if b["y"]>y+25 and abs(b["x"]-a["x"])<50]
    bottom=min(after)-8 if after else page.rect.height-24
    bottom=min(page.rect.height-15,max(y+58,bottom))
    rect=fitz.Rect(17,max(0,y-9),page.rect.width-17,bottom)
    if rect.height<55:return None,"BOUNDARY_TOO_SHORT"
    pix=page.get_pixmap(matrix=fitz.Matrix(1.7,1.7),clip=rect,colorspace=fitz.csRGB,alpha=False)
    blob=pix.tobytes("jpeg",jpg_quality=78)
    if len(blob)<2000:return None,"EMPTY_JPEG"
    CROPS.mkdir(parents=True,exist_ok=True)
    dest=CROPS/(name+".jpg")
    dest.write_bytes(blob)
    # This code intentionally never marks text/options as correct or complete.
    return {"file":str(dest.relative_to(ROOT)),"sha256":digest(blob),
            "bytes":len(blob),"sourcePDFSHA256":src_sha,"sourcePDFPage":page_no,
            "rectPDFPoints":[round(z,2) for z in rect],
            "questionHeadingCandidate":a,
            "reviewOnly":"MAY_CONTAIN_ADJACENT_QUESTION_OR_MISSING_FIVE_OPTIONS",
            "independentlyVerified":False},"PROVISIONAL_CROP_REQUIRES_NATIVE_PDF_REVIEW"

def main():
    queue=load(V34)
    require(queue["summary"]["totalTargets"]==791,"V34_TARGET_COUNT")
    original=queue["rows"]
    require(len(original)==791 and len({r["id"] for r in original})==791,"V34_UNIQUE")
    earlier=load(V41)
    require(len(earlier["files"])==103,"V41_103")
    excluded={r["id"] for r in earlier["files"]}|PILOTS
    require(len(excluded)==105,"EXCLUDE_103_AND_TWO_PILOTS")
    remaining=[r for r in original if r["id"] not in excluded]
    require(len(remaining)==686,"REMAINING_686")
    repairs={r["id"]:r for r in load(V42)["records"]}
    require(len(repairs)==4 and len(set(repairs)-excluded)==2,"TWO_REPAIRED_LEGAL_HOLDS")
    v38=load(V38)
    require(v38["uniqueImagePages"]==88 and len(v38["sourceDocuments"])==4,"V38_SHA_LOCKED")
    page_lookup={}
    for d in v38["sourceDocuments"]:
        for img in d["images"]:
            image_path=ROOT/"study-hub/first-v38-qnet-pages-2020-2021"/img["image"]
            require(image_path.is_file(),"V38_IMAGE_NOT_PRESENT_"+img["image"])
            require(digest(image_path.read_bytes())==img["sha256"],"V38_IMAGE_HASH_"+img["image"])
            page_lookup[(d["key"],img["page"])]=(image_path,img)
    require(len(page_lookup)==88,"V38_88_IMAGE_HASHES")
    ledger_txt=SOURCE.read_text(encoding="utf-8")
    ledger=json.loads(ledger_txt[ledger_txt.index("{"):ledger_txt.rfind(";")])
    official=load(OFFICIAL/"six-source-sha-manifest.json")
    require(official["officialSHA256Validated"]==6 and len(official["pdfs"])==6,"SIX_OFFICIAL_PDFS")
    docs={}
    for item in official["pdfs"]:
        p=OFFICIAL/(item["key"]+".pdf")
        require(p.is_file() and p.read_bytes().startswith(b"%PDF"),"OFFICIAL_PDF_NOT_FOUND_"+item["key"])
        require(digest(p.read_bytes())==item["sha256"],"OFFICIAL_PDF_SHA_"+item["key"])
        docs[item["key"]]=fitz.open(p)
        require(len(docs[item["key"]])==item["pages"],"OFFICIAL_PDF_PAGES_"+item["key"])
    page_targets=defaultdict(list)
    for q in remaining:
        if q["sourceDocumentSHA256"] and q["id"] not in repairs:
            s=ledger["records"].get(q["id"])
            if s and s.get("pdfPage"):
                page_targets[(s["source"],s["pdfPage"])].append(q)
    anchors={}
    page_ocr_errors={}
    for key in sorted(page_targets):
        source,page_no=key
        if key not in page_lookup:
            page_ocr_errors[str(key)]="V38_PAGE_NOT_SHA_LOCKED"
            continue
        p=docs[source][page_no-1]
        native=native_heads(p)
        if len({x["number"] for x in native})>=2:
            anchors[key]=native
        else:
            img_path,_=page_lookup[key]
            with Image.open(img_path) as im:
                guesses,err=image_heads(im,p)
            anchors[key]=guesses if guesses else native
            if err:page_ocr_errors[str(key)]=err
    rows=[]
    output_counts=Counter()
    for q in remaining:
        id=q["id"]
        candidate=q.get("candidateAnswers") or []
        require(isinstance(candidate,list) and len(candidate)>=1,"NO_ANSWER_CANDIDATE_"+id)
        entry={"id":id,"year":q["year"],"subject":q["subject"],
               "questionNumber":q["number"],"form":"A",
               "legacyAnswerCandidate":candidate,
               "officialFinalAnswerIndividualCellHumanConfirmed":False,
               "sourceNoticeOrPdfUrl":q.get("originalURL"),
               "sourceDocumentSHA256":q.get("sourceDocumentSHA256"),
               "historicalLegalOrTheoryFullVerification":False,
               "originalStemAndFiveOptionsIndependentlyVerified":False,
               "originalEquationGraphicVisuallyVerified":False,
               "fiveOptionExplanationsFullyVerified":False,
               "independentHumanSecondProofread":False,
               "approvedForLearningScoring":False,
               "readyForV44":False,"scoringApproved":False,
               "originalSourceProof":None,
               "priorityForNativeReviewer":None,
               "sourceStatus":None}
        if id in repairs:
            rec=repairs[id];p=ROOT/rec["originalQuestionImage"]
            require(p.is_file() and digest(p.read_bytes())==rec["sha256"],"REPAIRED_CROP_SHA_"+id)
            require(rec["sourcePdfSHA256"]==q["sourceDocumentSHA256"],"REPAIRED_PDF_MISMATCH_"+id)
            entry["sourceStatus"]="V42_SHA_PROVEN_IMAGE_2_LAW_HOLD"
            entry["originalSourceProof"]={"file":rec["originalQuestionImage"],
                "sha256":rec["sha256"],"sourcePDFSHA256":rec["sourcePdfSHA256"],
                "sourcePDFPage":rec["page"],"independentlyVerified":False}
            entry["priorityForNativeReviewer"]="HISTORICAL_LEGAL_FULL_TEXT_PRECEDENT_REQUIRED"
        elif q["sourceDocumentSHA256"]:
            s=ledger["records"].get(id)
            require(s is not None,"MISSING_QNET_ITEM_SOURCE_"+id)
            source=s["source"]; candidate_page=s.get("pdfPage")
            require(source in docs and docs[source][0] is not None,"OFFICIAL_PDF_SOURCE_"+id)
            require(ledger["documents"][source]["sha256"]==q["sourceDocumentSHA256"],"QUESTION_SHA_"+id)
            entry["officialPdfSourceGroup"]=source
            entry["v38PageCandidate"]=candidate_page
            if not candidate_page:
                entry["sourceStatus"]="OFFICIAL_QNET_PDF_SHA_MATCH_PAGE_UNLOCATED"
                entry["priorityForNativeReviewer"]="QUESTION_NUMBER_AND_PAGE_DISCOVERY"
            else:
                key=(source,candidate_page)
                entry["originalSourceProof"]={"file":str(page_lookup[key][0].relative_to(ROOT)),
                    "sha256":page_lookup[key][1]["sha256"],
                    "sourcePDFSHA256":q["sourceDocumentSHA256"],
                    "sourcePDFPage":candidate_page,
                    "independentlyVerified":False} if key in page_lookup else None
                proof,stage=(crop_review(docs[source],candidate_page,
                                  q["number"],anchors.get(key,[]),
                                  q["sourceDocumentSHA256"],id)
                             if key in anchors else (None,"MISSING_PAGE_SHA"))
                if proof:
                    entry["originalSourceProof"]=proof
                    entry["sourceStatus"]="PROVISIONAL_CROP_NUMBER_ANCHOR_NEEDS_ALL_FIVE_OPTIONS_CHECK"
                    entry["priorityForNativeReviewer"]="CROP_BOUNDARY_STEM_OPTIONS_GRAPHIC_CHECK"
                else:
                    entry["sourceStatus"]="OFFICIAL_QNET_PDF_SHA_MATCH_PAGE_ONLY_"+stage
                    entry["priorityForNativeReviewer"]="QUESTION_NUMBER_AND_FULL_PAGE_VISUAL_CHECK"
        elif q.get("originalURL"):
            entry["sourceStatus"]="QNET_NOTICE_ONLY_ATTACHMENT_AND_PDF_SHA_NOT_OBTAINED"
            entry["priorityForNativeReviewer"]="DOWNLOAD_ACTUAL_OFFICIAL_QUESTION_ATTACHMENT"
        else:
            entry["sourceStatus"]="NO_OFFICIAL_QUESTION_SOURCE_RECORDED"
            entry["priorityForNativeReviewer"]="LOCATE_ORIGINAL_A_FORM_QUESTION_PDF_HWP"
        output_counts[entry["sourceStatus"]]+=1
        rows.append(entry)
    for doc in docs.values():doc.close()
    require(len(rows)==686 and len({r["id"] for r in rows})==686,"OUTPUT_SIZE")
    byYear=dict(sorted(Counter(str(q["year"]) for q in rows).items()))
    qnet_groups={
        "v42TwoLawCrops":sum(q["sourceStatus"].startswith("V42_") for q in rows),
        "originalPdfConnectedOther":sum(q["sourceDocumentSHA256"] is not None and not q["sourceStatus"].startswith("V42_") for q in rows),
        "noticeOnly":sum(q["sourceStatus"]=="QNET_NOTICE_ONLY_ATTACHMENT_AND_PDF_SHA_NOT_OBTAINED" for q in rows),
        "noRecordedSource":sum(q["sourceStatus"]=="NO_OFFICIAL_QUESTION_SOURCE_RECORDED" for q in rows),
    }
    require(qnet_groups=={"v42TwoLawCrops":2,"originalPdfConnectedOther":193,"noticeOnly":314,"noRecordedSource":177},
            "BASELINE_BUCKETS_"+str(qnet_groups))
    summary={"schema":"NOMUSA_FIRST_V48_686_SOURCE_RECOVERY/1",
             "asOfKST":"2026-11-18",
             "yearBaseline":byYear,
             "targetCount":686,"prior103Excluded":103,"twoV42PilotScoringIdsExcluded":2,
             "sourceGroups":qnet_groups,"statusBreakdown":dict(sorted(output_counts.items())),
             "officialSixQnetPdfSHAValidated":6,"native88QnetPagesJPEG_SHAValidated":88,
             "pageAnchorOCRFailures":page_ocr_errors,
             "generatedProvisionalCrops":sum(x["sourceStatus"].startswith("PROVISIONAL_CROP") for x in rows),
             "genuineNewOriginalStemAndFiveOptionsIndependentlyApproved":0,
             "newHistoricalLawTheoryIndependentApproval":0,
             "newScoringApprovals":0,"newAppDataImports":0,
             "approvalStatus":"HOLD_EXTERNAL_PRIMARY_SOURCE_AND_INDEPENDENT_PROOFREAD",
             "meaning":"686 source candidates classified, official PDF/hash/page images reused for 193 and 2 existing law crops. OCR heading crops are provisional and not complete official question transcriptions; 491 missing official attachments cannot be fully content-reviewed.",
             "rows":rows}
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"NOMUSA_FIRST_V48_686_FULL_SOURCE_QUEUE.json").write_text(
        json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    with (OUT/"NOMUSA_FIRST_V48_686_REVIEW_QUEUE.csv").open("w",newline="",encoding="utf-8-sig") as f:
        w=csv.writer(f)
        w.writerow(["id","year","subject","number","sourceStatus","qnetPageCandidate",
                    "sourceImageOrPage","imageSHA256","answerCandidate","nextManualTask","grading"])
        for q in rows:
            p=q["originalSourceProof"] or {}
            w.writerow([q["id"],q["year"],q["subject"],q["questionNumber"],q["sourceStatus"],
                q.get("v38PageCandidate") or p.get("sourcePDFPage") or "",
                p.get("file") or "",p.get("sha256") or "",
                "|".join(map(str,q["legacyAnswerCandidate"])),q["priorityForNativeReviewer"],"HOLD"])
    compact={"schema":summary["schema"],"asOfKST":summary["asOfKST"],"targetCount":686,
             "sourceGroups":qnet_groups,"statusBreakdown":summary["statusBreakdown"],
             "byYear":byYear,"generatedProvisionalCrops":summary["generatedProvisionalCrops"],
             "officialSixQnetPdfSHAValidated":6,"native88QnetPagesJPEG_SHAValidated":88,
             "newScoringApprovals":0,"newAppDataImports":0,
             "independentSourceContentApprovals":0,
             "fullQueueInRunArtifact":"review-artifacts/NOMUSA_FIRST_V48/NOMUSA_FIRST_V48_686_FULL_SOURCE_QUEUE.json",
             "caveat":"Only source and candidate crop triage, NOT 686 validated original full texts, correct answers, complete explanations or scoring."}
    (ROOT/"review/NOMUSA_FIRST_V48_686_SOURCE_RECOVERY_SUMMARY_20261118.json").write_text(
        json.dumps(compact,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in summary.items() if k!="rows"},ensure_ascii=False))
if __name__=="__main__":
    main()

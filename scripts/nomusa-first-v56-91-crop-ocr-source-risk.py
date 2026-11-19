#!/usr/bin/env python3
"""V56: read-only OCR and source-risk queue for 91 *new* V55 provisional crops.

Every image is a provisional extraction from SHA-verified Q-Net 2016
management A PDF. OCR text is NOT an independently checked original question,
not the five options, not the final answer cell, and not an approved
explanation. Do not import any OCR text to the scoring app.
"""
from __future__ import annotations
import csv
import hashlib
import json
import os
import re
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

os.environ["OMP_THREAD_LIMIT"]="1"
import pytesseract
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
V55=ROOT/"review-artifacts/NOMUSA_FIRST_V55/NOMUSA_FIRST_V55_125_QUESTION_PAGE_AND_CROP_REVIEW.json"
CROPS=ROOT/"review-artifacts/NOMUSA_FIRST_V55"
OUT=ROOT/"review-artifacts/NOMUSA_FIRST_V56"
SUMMARY=ROOT/"review/NOMUSA_FIRST_V56_91_ORIGINAL_CROP_OCR_RISK_SUMMARY_20261118.json"
SHA_2016="328d2a7e12623abfb958b3cbfb2ac094688da295f644c502e22ea575c2a4554a"
OPTIONS=("①","②","③","④","⑤")
NUMHEAD=re.compile(r"(?m)^\s*(\d{1,3})\s*[.)．]\s*")
ALT_NUMBERS=re.compile(r"(?<!\d)(?:\(\s*([1-5])\s*\)|([1-5])\s*[.)．])")
def digest(b): return hashlib.sha256(b).hexdigest()
def check(cond,label):
    if not cond:raise AssertionError("HOLD_V56_"+label)
def j(path):return json.loads(path.read_text(encoding="utf8"))

def analyze(row):
    source=row["provisionalImage"]
    im_path=CROPS/source["image"]
    check(im_path.is_file(),"IMAGE_MISSING_"+row["id"])
    blob=im_path.read_bytes()
    check(digest(blob)==source["sha256"],"IMAGE_HASH_CHANGED_"+row["id"])
    check(row["sourcePDFSHA256"]==source["sourcePdfSHA256"]==SHA_2016,"SOURCE_PDF_MISMATCH_"+row["id"])
    try:
        with Image.open(im_path) as im:
            w,h=im.size
            check(w>=550 and h>=75,"IMAGE_TOO_SMALL_"+row["id"])
            text=pytesseract.image_to_string(im,lang="kor+eng",
                  config="--oem 1 --psm 6",timeout=16)
        error=None
    except Exception as exc:
        text=""
        error=type(exc).__name__+":"+str(exc)[:180]
        with Image.open(im_path) as im:w,h=im.size
    clean=" ".join(text.split())
    circled={c:clean.count(c) for c in OPTIONS}
    alt=[a or b for a,b in ALT_NUMBERS.findall(clean)]
    numbered=sorted(set(alt))
    headings=[int(x) for x in NUMHEAD.findall(text) if 1<=int(x)<=125]
    flags=["ORIGINAL_FIVE_CHOICES_VISUAL_COMPARE_HOLD",
           "INDEPENDENT_EXAM_DATE_LAW_AND_THEORY_REVIEW_HOLD",
           "OFFICIAL_FINAL_ANSWER_KEY_CELL_NOT_APPROVED",
           "QUESTION_CROP_BOUNDARY_VISUAL_COMPARE_HOLD"]
    if error:flags.append("OCR_TIMEOUT_OR_PROCESSING_ERROR")
    if len(clean)<60:flags.append("OCR_OUTPUT_SHORT_OR_BLANK")
    if sum(n>0 for n in circled.values())<5:flags.append("CIRCLED_FIVE_CHOICES_NOT_FULLY_RECOGNIZED")
    if len(numbered)<5:flags.append("ASCII_FIVE_CHOICES_NOT_FULLY_RECOGNIZED")
    if len(set(headings))>1:flags.append("MULTIPLE_QUESTION_HEADINGS_POSSIBLE_ADJACENT_TEXT")
    if any(n>1 for n in circled.values()):flags.append("DUPLICATE_CIRCLED_MARKER_POSSIBLE_BOUNDARY")
    if row["id"].split("-")[3]=="economics":
        flags.append("ECONOMIC_FORMULA_GRAPH_UNVERIFIED")
    elif row["id"].split("-")[3] in ("labor1","labor2","civil","social"):
        flags.append("LAW_EFFECTIVE_DATE_AMENDMENTS_CASES_UNVERIFIED")
    else:flags.append("MANAGEMENT_ACADEMIC_THEORY_UNVERIFIED")
    return {
        "id":row["id"],"year":2016,"subject":row["subject"],"number":row["number"],
        "originalSourcePDFSHA256":SHA_2016,
        "candidateImage":source["image"],"imageSHA256":source["sha256"],
        "candidateSourcePdfPage":source["officialQnetPdfPageCandidate"],
        "imageDimensions":[w,h],
        "ocrTextUnreviewedDraft":text[:6000],"ocrTextCharacters":len(clean),
        "ocrCircledMarkers":circled,"ocrAsciiOptionCandidates":numbered,
        "ocrQuestionHeadingNumbers":headings[:20],"ocrError":error,
        "legacyAFormAnswerCandidateUnapproved":row["legacyAnswerCandidateNumbersUnapproved"],
        "flags":sorted(set(flags)),
        "originalStemAndFiveOptionsVerified":False,
        "officialFinalKeyCellApproved":False,
        "legalStatutePrecedentOrTheoryApproved":False,
        "independentSecondProofreaderApproved":False,
        "readyForV44":False,"scoringApproved":False,
        "state":"OCR_TRANSCRIPTION_CANDIDATE_ONLY_REVIEW_REQUIRED"
    }

def main():
    data=j(V55)
    check(data["2016ManagementATargets"]==125,"V55_TOTAL")
    check(data["officialQnetPDFSHAValidated"] is True,"V55_SHA")
    targets=[x for x in data["rows"] if x["provisionalImage"]]
    check(len(targets)==91 and len({x["id"] for x in targets})==91,"V55_PROVISIONAL_91")
    rows=[]
    with ThreadPoolExecutor(max_workers=4) as ex:
        tasks=[ex.submit(analyze,x) for x in targets]
        for t in as_completed(tasks):rows.append(t.result())
    rows.sort(key=lambda x:x["number"])
    counts=Counter(flag for q in rows for flag in q["flags"])
    check(len(rows)==91 and all(x["scoringApproved"] is False for x in rows),"NO_GRADING")
    result={"schema":"NOMUSA_FIRST_V56_91_ORIGINAL_CROP_OCR_RISK/1",
            "asOfKST":"2026-11-18","newV55CropsOCRRequested":91,
            "ocrCandidatesGenerated":len(rows),"uniqueIds":len({q["id"] for q in rows}),
            "sourcePDFSHA256":SHA_2016,"imageSha256Passed":91,
            "ocrSuccessCount":sum(q["ocrError"] is None for q in rows),
            "potentialAdjacentQuestionHeadings":sum("MULTIPLE_QUESTION_HEADINGS_POSSIBLE_ADJACENT_TEXT" in q["flags"] for q in rows),
            "ocrCircledChoiceCountLessThanFive":sum("CIRCLED_FIVE_CHOICES_NOT_FULLY_RECOGNIZED" in q["flags"] for q in rows),
            "riskCounts":dict(sorted(counts.items())),
            "independentOriginalStemFiveOptionsApprovals":0,
            "examDateLawTheoryApprovals":0,"officialKeyCellApprovals":0,
            "newQDATAImports":0,"newScoringApprovals":0,
            "status":"PASS_91_OCR_SOURCE_DRAFTS_NOT_CONTENT_APPROVAL",
            "warning":"No OCR string, apparent option count or source crop is independent original text, official key, or legal/theory approval.",
            "rows":rows}
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"NOMUSA_FIRST_V56_91_UNAPPROVED_OCR_TEXT_AND_RISK.json").write_text(
        json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    with (OUT/"NOMUSA_FIRST_V56_91_RISK_QUEUE.csv").open("w",encoding="utf-8-sig",newline="") as f:
        wr=csv.writer(f);wr.writerow(["id","year","subject","number","image","PDFPage","ocrChars","flags","scoring"])
        for q in rows:wr.writerow([q["id"],q["year"],q["subject"],q["number"],q["candidateImage"],
                q["candidateSourcePdfPage"],q["ocrTextCharacters"],"|".join(q["flags"]),"HOLD"])
    summary={k:v for k,v in result.items() if k!="rows"}
    summary["full91ReviewEvidenceArtifact"]="review-artifacts/NOMUSA_FIRST_V56/NOMUSA_FIRST_V56_91_UNAPPROVED_OCR_TEXT_AND_RISK.json"
    SUMMARY.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps(summary,ensure_ascii=False))
if __name__=="__main__":main()

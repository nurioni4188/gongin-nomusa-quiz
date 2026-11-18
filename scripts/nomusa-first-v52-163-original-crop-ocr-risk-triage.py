#!/usr/bin/env python3
"""V52: OCR candidate text and full five-choice risk flags for 163 provisional
2016/18 and 2020/21 SHA-origin crops, without importing OCR or grading answers.

A Q-Net-original-derived provisional crop and a candidate A-form key are NOT
independent proof of stem/options/formula, or official final answer cell. None
of this output is approved exam content. Keep every content/approval flag HOLD.
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
from PIL import Image
import pytesseract

ROOT=Path(__file__).resolve().parents[1]
V51=ROOT/"review-artifacts/NOMUSA_FIRST_V51/NOMUSA_FIRST_V51_175_QUESTION_LOCATOR.json"
V34=ROOT/"review-artifacts/NOMUSA_FIRST_V34/NOMUSA_FIRST_V34_791_SOURCE_TARGETS.json"
OLD=ROOT/"review/first-v48-provisional-crops"
OUT=ROOT/"review-artifacts/NOMUSA_FIRST_V52"
NUM_HEAD=re.compile(r"^\s*(\d{1,3})\s*[.)．]\s*\S",re.M)
NUMERALS=re.compile(r"\d+(?:\.\d+)?")
CIRCLED="①②③④⑤"

def read(path):return json.loads(path.read_text(encoding="utf-8"))
def sha(b):return hashlib.sha256(b).hexdigest()
def assert_ok(ok,msg):
    if not ok:raise AssertionError("HOLD_V52_"+msg)

def process(q):
    image=ROOT/q["image"]
    blob=image.read_bytes()
    assert_ok(sha(blob)==q["sha256"],"CROP_SHA_CHANGED_"+q["id"])
    with Image.open(image) as im:
        w,h=im.size
        assert_ok(w>=500 and h>=65,"SOURCE_CROP_UNREADABLE_"+q["id"])
        try:
            text=pytesseract.image_to_string(
                im,lang="kor+eng",config="--oem 1 --psm 6",timeout=14)
            error=None
        except Exception as exc:
            text=""
            error=type(exc).__name__+":"+str(exc)[:150]
    compact=" ".join(text.split())
    markers={c:compact.count(c) for c in CIRCLED}
    count=sum(n>0 for n in markers.values())
    heading=[int(n) for n in NUM_HEAD.findall(text)]
    untrusted=set()
    if error:untrusted.add("OCR_ENGINE_ERROR")
    if len(compact)<60:untrusted.add("LOW_OCR_TRANSCRIPT_LENGTH")
    if count<5:untrusted.add("ONE_OR_MORE_FIVE_OPTIONS_NOT_RECOGNIZED_BY_OCR")
    if any(n>1 for n in markers.values()):untrusted.add("REPEATED_CIRCLED_OPTION_MARKERS_CROP_BOUNDARY_SUSPECT")
    if len(set(heading))>1:untrusted.add("ADJACENT_QUESTION_NUMBER_CANDIDATE")
    if q["year"]<=2018:untrusted.add("SCANNED_PDF_NUMBER_CROP_BOUNDARY_NOT_INDEPENDENTLY_PROOFREAD")
    if q["id"].split("-")[3] in ("labor1","labor2","civil","social"):
        untrusted.add("EXAM_DATE_STATUTE_AMENDMENTS_PRECEDENTS_NOT_APPROVED")
    elif q["id"].split("-")[3]=="economics":
        untrusted.add("EQUATIONS_GRAPHS_CALCULATIONS_NOT_INDEPENDENTLY_CHECKED")
    else:
        untrusted.add("ACADEMIC_THEORY_AND_ALL_FIVE_CHOICES_NOT_INDEPENDENTLY_APPROVED")
    # No candidate text is complete; even all circled markers in OCR is not proof.
    untrusted.add("OCR_DRAFT_UNVERIFIED_NO_SCORING")
    return {
        "id":q["id"],"year":q["year"],"subject":q["subject"],"number":q["number"],
        "originalOfficialSourcePdfSHA256":q["sourcePdfSHA256"],
        "originalImage":q["image"],"originalImageSHA256":q["sha256"],
        "cropSourceStage":q["origin"],"dimensions":[w,h],
        "untrustedOCRTextCandidate":text[:5000],
        "ocrChars":len(compact),"ocrCircledOptionMarkers":markers,
        "circledOptionMarkersRecognized":count,
        "candidateQuestionNumbersSeen":heading[:12],
        "historicalAFormAnswerCandidatesFromLedgerNotOfficiallyApproved":q["candidateAnswers"],
        "officialFinalAFormKeyCellIndependentlyChecked":False,
        "nativePDFOriginalStemAndAllOptionsIndependentlyProofread":False,
        "mathGraphicTableVerified":False,
        "examDateStatutePrecedentsOrTheoryValidated":False,
        "independentReviewerSignoff":False,
        "approvedForScoring":False,
        "readyForV44":False,
        "scoringApproved":False,
        "qaFlags":sorted(untrusted),"ocrError":error,
        "status":"OCR_ONLY_RISK_TRIAGE_HUMAN_ORIGINAL_VERIFICATION_HOLD",
    }

def main():
    v51=read(V51)
    assert_ok(v51["targetQuestionIds"]==175 and v51["provisionalIndividualCrops"]==96,"V51_CROP_COUNT")
    v34=read(V34)
    ledger={q["id"]:q for q in v34["rows"]}
    assert_ok(len(ledger)==791,"V34_791")
    old=list(sorted(OLD.glob("*.jpg")))
    assert_ok(len(old)==67,"V48_67_CROPS_"+str(len(old)))
    entries=[]
    for file in old:
        id=file.stem
        q=ledger.get(id)
        assert_ok(q is not None and q["year"] in (2020,2021),"UNEXPECTED_V48_ID_"+id)
        entries.append({
            "id":id,"year":q["year"],"subject":q["subject"],"number":q["number"],
            "image":str(file.relative_to(ROOT)),"sha256":sha(file.read_bytes()),
            "sourcePdfSHA256":q["sourceDocumentSHA256"],
            "candidateAnswers":q["candidateAnswers"],
            "origin":"V48_SHA_QNET_PDF_NUMBER_CROP_PROVISIONAL"})
    for q in v51["rows"]:
        if not q["crop"]:continue
        image=ROOT/"review-artifacts/NOMUSA_FIRST_V51"/q["crop"]["file"]
        assert_ok(image.is_file(),"V51_CROP_MISSING_"+q["id"])
        source=ledger.get(q["id"])
        assert_ok(source is not None and source["year"] in (2016,2018),"UNEXPECTED_V51_ID_"+q["id"])
        entries.append({
            "id":q["id"],"year":q["year"],"subject":q["subject"],"number":q["questionNumber"],
            "image":str(image.relative_to(ROOT)), "sha256":q["crop"]["sha256"],
            "sourcePdfSHA256":q["officialSourcePdfSHA256"],
            "candidateAnswers":source["candidateAnswers"],
            "origin":"V51_SHA_QNET_A_FORM_NUMBER_CROP_PROVISIONAL"})
    assert_ok(len(entries)==163 and len({q["id"] for q in entries})==163,"163_UNIQUE_CROPS")
    result=[]
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures=[pool.submit(process,q) for q in entries]
        for future in as_completed(futures):result.append(future.result())
    result.sort(key=lambda q:(q["year"],q["subject"],q["number"]))
    flagged=Counter(t for q in result for t in q["qaFlags"])
    byYear=Counter(str(q["year"]) for q in result)
    status={
        "schema":"NOMUSA_FIRST_V52_163_PROVISIONAL_SOURCE_OCR_DRAFT_AND_RISK/1",
        "asOfKST":"2026-11-18",
        "qnetPDFSHAOriginPrelimCrops":163,
        "v48Crops":67,"v51Crops":96,
        "uniqueQuestionIds":163,
        "byYear":dict(sorted(byYear.items())),
        "ocrWorkedCount":sum(q["ocrError"] is None for q in result),
        "ocrSourceDiffCandidates":sum(q["circledOptionMarkersRecognized"]<5 for q in result),
        "ocrFlagCounts":dict(sorted(flagged.items())),
        "independentFullQuestionTextProofread":0,
        "fiveOptionsVisuallyProven":0,
        "examDateLawPrecedentTheoreticalApproved":0,
        "independentExpertSignoffs":0,
        "newScoringApproved":0,"newAppSourceImports":0,
        "status":"PASS_163_CROP_OCR_SOURCE_PROVENANCE_HOLD_163_ORIGINAL_CONTENT_EXPERT_VERIFICATION",
        "warning":"These 163 text blobs come from OCR of provisional images; they are not full Q-Net original texts, authoritative A-form answers, five-option checked explanations or independent proofreading.",
        "rows":result,
    }
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"NOMUSA_FIRST_V52_163_OCR_SOURCE_RISK_REVIEW.json").write_text(
        json.dumps(status,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    with (OUT/"NOMUSA_FIRST_V52_163_REVIEW_QUEUE.csv").open("w",encoding="utf-8-sig",newline="") as f:
        w=csv.writer(f)
        w.writerow(["id","year","subject","number","image","sourcePdfSHA","recognizedOptionMarkers",
                    "ocrChars","untrustedOCRTranscriptSnippet","flags","independentContent","score"])
        for q in result:
            w.writerow([q["id"],q["year"],q["subject"],q["number"],q["originalImage"],
                 q["originalOfficialSourcePdfSHA256"],q["circledOptionMarkersRecognized"],q["ocrChars"],
                 " ".join(q["untrustedOCRTextCandidate"].split())[:200],
                 "|".join(q["qaFlags"]),"HOLD","HOLD"])
    summary={k:v for k,v in status.items() if k!="rows"}
    summary["full163ReviewArtifact"]="review-artifacts/NOMUSA_FIRST_V52/NOMUSA_FIRST_V52_163_OCR_SOURCE_RISK_REVIEW.json"
    (ROOT/"review/NOMUSA_FIRST_V52_163_CROPS_OCR_RISK_SUMMARY_20261118.json").write_text(
        json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False))
if __name__=="__main__":main()

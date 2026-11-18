#!/usr/bin/env python3
"""V47 second OCR engine/pagination hint, NOT an independent human proofread.

Read all 103 SHA-checked original Q-Net crops directly from current review
branch. Run two alternate OCR segmentations and rank source-text discrepancies
for later original-image manual verification. No answer keys or approvals are
changed. OCR similarity MUST NOT be presented as substantive content approval.
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import Counter
from difflib import SequenceMatcher
import hashlib, json, re
import pytesseract
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
SOURCE_FILES=[
"review/NOMUSA_FIRST_V43_21_SOURCE_READ_ANSWER_DRAFTS_20261118.json",
"review/NOMUSA_FIRST_V43_REMAINING_17_MANAGEMENT_STEM_5OPTIONS_ANSWERS_20261118.json",
"review/NOMUSA_FIRST_V43_2021_ECONOMICS_5_SOURCE_READ_20261118.json",
"review/NOMUSA_FIRST_V43_2020_ECONOMICS_16_SOURCE_READ_CALCULATIONS_20261118.json",
"review/NOMUSA_FIRST_V43_2021_ECONOMICS_REMAINING_19_CALC_GRAPH_20261118.json",
"review/NOMUSA_FIRST_V43_TEN_2020_2021_LABOR_LAW_SOURCE_AND_DRAFTS_20261118.json",
"review/NOMUSA_FIRST_V43_SEVEN_2021_CIVIL_ORIGINAL_STATUTE_DRAFTS_20261118.json",
"review/NOMUSA_FIRST_V43_EIGHT_2021_SOCIAL_ORIGINAL_EXAM_LAW_DRAFTS_20261118.json"]

def load(path): return json.loads((ROOT/path).read_text(encoding="utf-8"))
def normalize(value): return re.sub(r"[^a-zA-Z0-9가-힣]", "", value or "").lower()
def numbers(value): return Counter(re.findall(r"\d+(?:\.\d+)?", value or ""))
def record(q):
    return {
        "id":q["id"],
        "image":q.get("originalImagePath") or q.get("originalImage") or q.get("sourceImage") or q.get("imagePath") or q.get("sourceCropImage"),
        "sha256":q.get("originalImageSHA256") or q.get("sourceImageSHA256") or q.get("imageSHA256") or q.get("sourceCropSHA256"),
        "stem":q.get("question") or q.get("exactOriginalStemDraft") or q.get("sourceStemDraft") or q.get("exactStemFromImageDraft"),
        "options":q.get("options") or q.get("optionTexts") or q.get("originalFiveOptionsDraft") or q.get("sourceFiveOptionsDraft") or q.get("allFiveOptionsFromImageDraft")
    }

def check_one(q):
    path=ROOT/q["image"]
    assert path.is_file(), "MISSING_IMAGE:"+q["id"]
    assert hashlib.sha256(path.read_bytes()).hexdigest()==q["sha256"], "SOURCE_HASH_CHANGED:"+q["id"]
    expected=q["stem"]+"\n"+"\n".join(q["options"])
    try:
        with Image.open(path) as im:
            # PSM 6 and 11 are two independent layout hypotheses, NOT independent source readings.
            a=pytesseract.image_to_string(im, lang="kor+eng", config="--oem 1 --psm 6")
            b=pytesseract.image_to_string(im, lang="kor+eng", config="--oem 1 --psm 11")
        measures=[SequenceMatcher(None,normalize(expected),normalize(x),autojunk=False).ratio() for x in (a,b)]
        best=a if measures[0]>=measures[1] else b
        missing=list((numbers(expected)-numbers(best)).elements())
        flags=[]
        if len(normalize(best))<20:flags.append("LOW_OCR_OUTPUT")
        if max(measures)<0.55:flags.append("SOURCE_OCR_TEXT_DIFFERENCE_PRIORITY")
        if missing:flags.append("NUMBER_FORMULA_VISUAL_REVIEW")
        return {"id":q["id"],"image":q["image"],"sha256Matched":True,
            "psm6Score":round(measures[0],3),"psm11Score":round(measures[1],3),
            "bestOCRCharacters":len(normalize(best)),
            "sourceNumeralsNotSeenInBestOCR":missing[:25],
            "flags":flags or ["REQUIRES_VISUAL_CROSSCHECK_EVEN_IF_OCR_MATCHES"],
            "independentNativeImageHumanProofread":False,
            "examDateLegalApproval":False,"scoringApproved":False}
    except Exception as exc:
        return {"id":q["id"],"image":q["image"],"sha256Matched":True,
            "flags":["OCR_FAILED_MANUAL_IMAGE_REVIEW_REQUIRED"],
            "ocrError":type(exc).__name__+":"+str(exc)[:150],
            "independentNativeImageHumanProofread":False,
            "examDateLegalApproval":False,"scoringApproved":False}

def main():
    rows=[record(q) for path in SOURCE_FILES for q in (load(path).get("rows") or load(path).get("records"))]
    assert len(rows)==103 and len({q["id"] for q in rows})==103
    assert all(q["image"] and len(q["options"])==5 and q["stem"] and q["sha256"] for q in rows)
    results=[]
    with ThreadPoolExecutor(max_workers=4) as ex:
        tasks=[ex.submit(check_one,q) for q in rows]
        for future in as_completed(tasks):results.append(future.result())
    results.sort(key=lambda x:(x.get("psm6Score",0)+x.get("psm11Score",0),x["id"]))
    assert len(results)==103 and all(q["sha256Matched"] for q in results)
    byflag=Counter(flag for q in results for flag in q["flags"])
    out={"schema":"NOMUSA_FIRST_V47_SECOND_OCR_PREDEPLOY_CANDIDATES/1",
        "sourceCroppingFiles":103,"sha256Matched":103,
        "twoSegmentationsPerImage":2,
        "independentNativeImageHumanProofreadCompleted":0,
        "independentExamDateLawApproved":0,
        "newScoringApproved":0,
        "meaning":"Two OCR layouts used to PRIORITIZE manual source proofreading. Not two independent experts. No auto-approval.",
        "status":"HOLD_103_HUMAN_NATIVE_PDF_WORD_FOR_WORD_REVIEW",
        "issueCounts":dict(byflag),"rows":results}
    dest=ROOT/"review-artifacts/NOMUSA_FIRST_V47"
    dest.mkdir(parents=True,exist_ok=True)
    (dest/"NOMUSA_FIRST_V47_103_DUAL_OCR_CANDIDATES.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":out["status"],"images":103,"shaMatch":103,"flagged":dict(byflag)},ensure_ascii=False))
if __name__=="__main__":main()

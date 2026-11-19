#!/usr/bin/env python3
"""V64: visually re-render and compare all 254 original Q-Net source crops.

Compare actual provisional crop content to the SHA-locked Q-Net original PDF
at its independently recorded crop rectangle; inspect image edges, OCR risk
flags and produce reviewer-friendly annotated ORIGINAL page excerpts.
This is real source-image geometric quality control, NOT independent proof
of a full stem, all choices, correct answers or legal explanations.
Never change study-hub QDATA, historical answer keys, V44 approvals or deploy.
"""
from __future__ import annotations
import csv, hashlib, io, json, os
from collections import Counter
from pathlib import Path

os.environ["OMP_THREAD_LIMIT"]="1"
import fitz, requests
from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageStat

ROOT=Path(__file__).resolve().parents[1]
V48=ROOT/"review-artifacts/NOMUSA_FIRST_V48/NOMUSA_FIRST_V48_686_FULL_SOURCE_QUEUE.json"
V51=ROOT/"review-artifacts/NOMUSA_FIRST_V51/NOMUSA_FIRST_V51_175_QUESTION_LOCATOR.json"
V55=ROOT/"review-artifacts/NOMUSA_FIRST_V55/NOMUSA_FIRST_V55_125_QUESTION_PAGE_AND_CROP_REVIEW.json"
V52=ROOT/"review-artifacts/NOMUSA_FIRST_V52/NOMUSA_FIRST_V52_163_OCR_SOURCE_RISK_REVIEW.json"
V56=ROOT/"review-artifacts/NOMUSA_FIRST_V56/NOMUSA_FIRST_V56_91_UNAPPROVED_OCR_TEXT_AND_RISK.json"
V50=ROOT/"review-artifacts/NOMUSA_FIRST_V50/NOMUSA_FIRST_V50_686_ENRICHED_SOURCE_QUEUE.json"
OFFICIAL=ROOT/"review-artifacts/NOMUSA_FIRST_V42_OFFICIAL"
OUT=ROOT/"review-artifacts/NOMUSA_FIRST_V64"
PANELS=OUT/"annotated_original_page_review"
SUMMARY=ROOT/"review/NOMUSA_FIRST_V64_254_OFFICIAL_CROP_GEOMETRY_QA_20261119.json"
PANELS.mkdir(parents=True,exist_ok=True)
MAGICS={"sourceDraftsAreUnapproved":True,"scoringApproved":False,"readyForV44":False}

def load(p):return json.loads(p.read_text(encoding="utf8"))
def digest(b):return hashlib.sha256(b).hexdigest()
def require(v,m):
    if not v:raise AssertionError("HOLD_V64_"+m)
def path_and_verify(name,expected):
    p=ROOT/name
    require(p.is_file(),"MISSING_SOURCE_CROP_"+name)
    require(digest(p.read_bytes())==expected,"CROP_SHA_MISMATCH_"+name)
    return p

def get_docs():
    original=load(OFFICIAL/"six-source-sha-manifest.json")
    require(original["officialSHA256Validated"]==6 and len(original["pdfs"])==6,"V42_SIX_PDFS")
    docs={}
    for spec in original["pdfs"]:
        file=OFFICIAL/(spec["key"]+".pdf")
        require(file.is_file() and digest(file.read_bytes())==spec["sha256"],
                "V42_OFFICIAL_SOURCE_SHA_"+spec["key"])
        docs[spec["sha256"]]=(fitz.open(file),spec["key"])
    stage=load(V50)
    require(stage["newOfficialAFormBookletSHAConnections"]==175,"V50_175")
    for k,doc in stage["officialDocuments"].items():
        file=ROOT/"review-artifacts/NOMUSA_FIRST_V50"/doc["file"]
        require(file.is_file() and digest(file.read_bytes())==doc["sha256"],"V50_PDF_SHA_"+k)
        docs[doc["sha256"]]=(fitz.open(file),k)
    s=load(ROOT/"review/NOMUSA_FIRST_V53_2016_MANAGEMENT_QNET_SOURCE_SUMMARY_20261118.json")["source"]
    require(s["sourcePDFSHA256"]=="328d2a7e12623abfb958b3cbfb2ac094688da295f644c502e22ea575c2a4554a","V53_PIN")
    resp=requests.get(s["officialSourceURL"],headers={"User-Agent":"Mozilla/5.0","Referer":"https://www.q-net.or.kr/"},timeout=(12,110))
    resp.raise_for_status()
    blob=resp.content
    require(blob.startswith(b"%PDF") and digest(blob)==s["sourcePDFSHA256"],"V53_ORIGINAL_SHA_DRIFT")
    docs[s["sourcePDFSHA256"]]=(fitz.open(stream=blob,filetype="pdf"),"2016_management_A")
    return docs

def original_review_records():
    v48,v51,v55=load(V48),load(V51),load(V55)
    require(v48["targetCount"]==686 and v48["generatedProvisionalCrops"]==67,"V48_67")
    require(v51["targetQuestionIds"]==175 and v51["provisionalIndividualCrops"]==96,"V51_96")
    require(v55["2016ManagementATargets"]==125 and v55["provisionalCropFiles"]==91,"V55_91")
    rows=[]
    for v in v48["rows"]:
        p=v.get("originalSourceProof") or {}
        if not str(p.get("file","")).startswith("review/first-v48-provisional-crops/"):continue
        rows.append({"id":v["id"],"year":v["year"],"subject":v["subject"],
            "questionNumber":v["questionNumber"],"stage":"V48",
            "cropPath":p["file"],"cropSHA256":p["sha256"],
            "pdfSHA256":p["sourcePDFSHA256"],"pdfPage":p["sourcePDFPage"],
            "sourceRectPDFPoints":p["rectPDFPoints"],"originalImageSource":"QNET_OFFICIAL_PDF_SHA"})
    for v in v51["rows"]:
        if not v["crop"]:continue
        p=v["crop"]
        rows.append({"id":v["id"],"year":v["year"],"subject":v["subject"],
            "questionNumber":v["questionNumber"],"stage":"V51",
            "cropPath":"review-artifacts/NOMUSA_FIRST_V51/"+p["file"],
            "cropSHA256":p["sha256"],"pdfSHA256":v["officialSourcePdfSHA256"],
            "pdfPage":p["sourcePdfPage"],"sourceRectPDFPoints":p["cropRectPoints"],
            "originalImageSource":"QNET_OFFICIAL_PDF_SHA"})
    for v in v55["rows"]:
        if not v["provisionalImage"]:continue
        p=v["provisionalImage"]
        rows.append({"id":v["id"],"year":2016,"subject":v["subject"],
            "questionNumber":v["number"],"stage":"V55",
            "cropPath":"review-artifacts/NOMUSA_FIRST_V55/"+p["image"],
            "cropSHA256":p["sha256"],"pdfSHA256":p["sourcePdfSHA256"],
            "pdfPage":p["officialQnetPdfPageCandidate"],
            "sourceRectPDFPoints":p["sourceRectPDFPoints"],
            "originalImageSource":"QNET_OFFICIAL_PDF_SHA"})
    stages=Counter(x["stage"] for x in rows)
    require(dict(stages)=={"V48":67,"V51":96,"V55":91},"STAGE_COUNTS_"+str(stages))
    require(len({x["id"] for x in rows})==254,"254_ID_COLLISION")
    return rows

def ocr_records():
    v52,v56=load(V52),load(V56)
    require(len(v52["rows"])==163 and v52["ocrWorkedCount"]==163,"V52_163")
    require(len(v56["rows"])==91 and v56["ocrSuccessCount"]==91,"V56_91")
    m={}
    for x in v52["rows"]:
        require(x["id"] not in m,"V52_DUPLICATE_ID")
        m[x["id"]]={"untrustedOCRText":x["untrustedOCRTextCandidate"],
                    "ocrFlags":x["qaFlags"],"ocrChars":x["ocrChars"],
                    "ocrAdjacentHeadings":x["candidateQuestionNumbersSeen"],
                    "ocrCandidateChoiceCount":x["circledOptionMarkersRecognized"]}
    for x in v56["rows"]:
        require(x["id"] not in m,"V56_DUPLICATE_ID")
        m[x["id"]]={"untrustedOCRText":x["ocrTextUnreviewedDraft"],
                    "ocrFlags":x["flags"],"ocrChars":x["ocrTextCharacters"],
                    "ocrAdjacentHeadings":x["ocrQuestionHeadingNumbers"],
                    "ocrCandidateChoiceCount":sum(v>0 for v in x["ocrCircledMarkers"].values())}
    require(len(m)==254,"OCR_254_JOIN")
    return m

def pixel_metric(crop,expected):
    # Separate PIL downsampling uses a few blur pixels to avoid tiny rounded
    # rectangle coordinate differences producing misleading hard failures.
    def normalized(im):
        return im.convert("L").resize((256,256),Image.Resampling.BILINEAR)
    a,b=normalized(crop),normalized(expected)
    return round(ImageStat.Stat(ImageChops.difference(a,b)).mean[0]/255,5)

def panel(doc,page_num,rectangle,id,flags):
    page=doc[page_num-1]
    pix=page.get_pixmap(matrix=fitz.Matrix(1.1,1.1),colorspace=fitz.csRGB,alpha=False)
    im=Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")
    painter=ImageDraw.Draw(im)
    xy=[int(q*1.1) for q in rectangle]
    painter.rectangle(xy,outline=(225,40,42),width=5)
    painter.text((12,8),id+" • "+",".join(flags[:2]),fill=(20,20,20))
    target=PANELS/(id+".jpg")
    im.save(target,"JPEG",quality=75)
    return {"path":str(target.relative_to(OUT)),"sha256":digest(target.read_bytes()),
            "originalOfficialPageWithCropRectangle":True}

def main():
    rows=original_review_records()
    ocr=ocr_records()
    docs=get_docs()
    data=[];classes=Counter();stages=Counter()
    for rec in rows:
        id=rec["id"];sha_pdf=rec["pdfSHA256"]
        require(sha_pdf in docs,"QNET_SOURCE_PDF_NOT_SHA_VERIFIED_"+id)
        doc,docName=docs[sha_pdf]
        idx=rec["pdfPage"]-1
        require(0<=idx<len(doc),"PAGE_OUTSIDE_OFFICIAL_PDF_"+id)
        rect=fitz.Rect(rec["sourceRectPDFPoints"])
        p=doc[idx]
        require(rect.x0>=0 and rect.y0>=0 and rect.x1<=p.rect.width+1 and
            rect.y1<=p.rect.height+1 and rect.width>35 and rect.height>30,
            "ORIGINAL_PDF_RECT_INVALID_"+id)
        cp=path_and_verify(rec["cropPath"],rec["cropSHA256"])
        with Image.open(cp) as im:
            img=im.convert("RGB")
        rendered=p.get_pixmap(matrix=fitz.Matrix(1.65,1.65),clip=rect,colorspace=fitz.csRGB,alpha=False)
        other=Image.open(io.BytesIO(rendered.tobytes("png"))).convert("RGB")
        score=pixel_metric(img,other)
        frac=rect.height/p.rect.height
        # This is a pixel / bounding-box comparison, NOT a five-choice check.
        if score<=.08:
            visual="SOURCE_RECTANGLE_IMAGE_SIMILAR_CANDIDATE"
        elif score<=.20:
            visual="SOURCE_RECTANGLE_IMAGE_NEEDS_VISUAL_RECHECK"
        else:
            visual="SOURCE_RECTANGLE_PIXEL_MISMATCH_HOLD"
        flags=[]
        if score>.08:flags.append("RENDERED_QNET_SOURCE_REGION_DIFF")
        if frac<.15:flags.append("CROP_HEIGHT_UNDER_15_PERCENT_OF_PAGE")
        if frac>.92:flags.append("CROP_MAY_INCLUDE_NEIGHBORING_QUESTIONS")
        if rect.y1>p.rect.height-35:flags.append("CROP_ENDS_NEAR_PAGE_FOOTER_CHECK_CONTINUATION")
        if rect.y0<38:flags.append("CROP_STARTS_NEAR_PAGE_HEADER")
        o=ocr[id]
        if o["ocrCandidateChoiceCount"]<5:flags.append("OCR_CIRCLED_OPTIONS_NOT_FULLY_DETECTED")
        if len(set(n for n in o["ocrAdjacentHeadings"] if n!=rec["questionNumber"]))>0:
            flags.append("OCR_SAW_DIFFERENT_QUESTION_NUMBER")
        if o["ocrChars"]<60:flags.append("OCR_SOURCE_TEXT_CANDIDATE_TOO_SHORT")
        # All provisional crop texts remain unverified after pixel matching.
        flags.append("EXACT_STEM_FIVE_CHOICES_MATH_GRAPH_OR_SHARED_TEXT_REVIEW_HOLD")
        source_checks={
            "id":id,"year":rec["year"],"subject":rec["subject"],
            "questionNumber":rec["questionNumber"],"stage":rec["stage"],
            "officialQNetPdfSha256":sha_pdf,"sourcePdfGroup":docName,
            "sourcePdfPage":rec["pdfPage"],
            "originalCandidateImage":rec["cropPath"],"candidateImageSHA256":rec["cropSHA256"],
            "pdfCropRectanglePoints":rec["sourceRectPDFPoints"],
            "sourcePageHeight":round(p.rect.height,2),
            "cropHeightAsFractionOfSourcePage":round(frac,4),
            "sourceRenderedVsCandidateNormalizedMeanAbsolutePixelDiff":score,
            "renderedOriginalRegionVisualState":visual,
            "previousOCRCandidateLength":o["ocrChars"],
            "previousOCRCircledChoicesCount":o["ocrCandidateChoiceCount"],
            "originalContentRiskFlags":sorted(set(flags)),
            "independentFullQNetStemAndFiveOptionsVerified":False,
            "independentOfficialAFormAnswerCellVerified":False,
            "historicalExamDateStatutesAndPrecedentsVerified":False,
            "independentAcademicTheoryAndFormulaReviewed":False,
            "independentHumanSecondProofreaderApproval":False,
            "approvedForLearningScoring":False,
            "readyForV44":False,"scoringApproved":False,
            "status":"IMAGE_TO_OFFICIAL_QNET_REGION_COMPARE_ONLY_CONTENT_APPROVAL_HOLD"}
        data.append(source_checks)
        classes[visual]+=1
        stages[rec["stage"]]+=1
    # Annotate worst source-image differences and suspiciously short crops
    top=sorted(data,key=lambda q:(
        0 if q["renderedOriginalRegionVisualState"]=="SOURCE_RECTANGLE_PIXEL_MISMATCH_HOLD" else
        1 if q["renderedOriginalRegionVisualState"]=="SOURCE_RECTANGLE_IMAGE_NEEDS_VISUAL_RECHECK" else 2,
        -q["sourceRenderedVsCandidateNormalizedMeanAbsolutePixelDiff"],
        q["cropHeightAsFractionOfSourcePage"]))[:24]
    for item in top:
        doc,_=docs[item["officialQNetPdfSha256"]]
        item["annotatedOriginalPage"]=panel(doc,item["sourcePdfPage"],
           item["pdfCropRectanglePoints"],item["id"],item["originalContentRiskFlags"])
    for doc,_ in docs.values():doc.close()
    require(len(data)==254 and len({q["id"] for q in data})==254,"254_UNIQUE_QNET_SOURCE_IMAGES")
    require(dict(stages)=={"V48":67,"V51":96,"V55":91},"254_STAGES")
    require(all(not q["approvedForLearningScoring"] and not q["readyForV44"] and not q["scoringApproved"] for q in data),
        "NO_SCORING_APPROVAL")
    result={"schema":"NOMUSA_FIRST_V64_254_OFFICIAL_QNET_ORIGINAL_RECTANGLE_IMAGE_QA/1",
        "asOfKST":"2026-11-19",
        "targetProvisionalCropImages":254,
        "sourceGroupImages":dict(sorted(stages.items())),
        "originalSourcePdfSHAMatchedForAllCrops":254,
        "candidateCropFileSHA256Matched":254,
        "candidateImageComparedToRenderedOriginalRectangle":254,
        "rectangleImageSimilarityStates":dict(sorted(classes.items())),
        "top24OriginalPageAnnotationsForExpertReview":len(top),
        "independentOriginalStemAndFiveOptionsApproved":0,
        "officialFinalAFormAnswerCellsApproved":0,
        "historicalLawAndAcademicTheoryContentApproved":0,
        "independentHumanReviewApprovals":0,
        "newScoringApproved":0,"newAppImports":0,
        "status":"PASS_254_QNET_SOURCE_RECTANGLE_IMAGE_AUDIT_HOLD_EXACT_ORIGINAL_TEXT_AND_GRADING",
        "warning":"Crop pixel similarity proves only that a candidate JPEG resembles the corresponding Q-Net PDF rectangle. No claim of complete original question or five choices, correct key or expert approval.",
        "rows":data}
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"NOMUSA_FIRST_V64_254_ORIGINAL_REGION_IMAGE_QA.json").write_text(
        json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    with (OUT/"NOMUSA_FIRST_V64_254_REVIEW_QUEUE.csv").open("w",encoding="utf-8-sig",newline="") as f:
        w=csv.writer(f)
        w.writerow(["id","year","subject","number","officialSourcePDF","page","image","cropFraction","pixelDifference",
                    "sourceImageState","risks","independentContentProof","grading"])
        for q in data:
            w.writerow([q["id"],q["year"],q["subject"],q["questionNumber"],q["officialQNetPdfSha256"],
                q["sourcePdfPage"],q["originalCandidateImage"],q["cropHeightAsFractionOfSourcePage"],
                q["sourceRenderedVsCandidateNormalizedMeanAbsolutePixelDiff"],q["renderedOriginalRegionVisualState"],
                "|".join(q["originalContentRiskFlags"]),"HOLD","HOLD"])
    compact={k:v for k,v in result.items() if k!="rows"}
    compact["full254QueueInArtifact"]="review-artifacts/NOMUSA_FIRST_V64/NOMUSA_FIRST_V64_254_ORIGINAL_REGION_IMAGE_QA.json"
    SUMMARY.write_text(json.dumps(compact,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps(compact,ensure_ascii=False))
if __name__=="__main__":main()

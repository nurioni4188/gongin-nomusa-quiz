#!/usr/bin/env python3
"""V65: protect ALL 254 incomplete cropped originals with full-page Q-Net
reference images and per-question reviewer evidence, without inventing choices.

Read V64 SHA-verified crop rectangle ledger. Render the entire ORIGINAL
Q-Net PDF page for each ID, highlight the provisional region (red), compare
neighboring crop geometry on same PDF page, and score potential text in the
uncovered gap between candidate crops using original PDF raster ink
coverage and native text where available.

Full page is a *safe reference* for human proofreading; it is not a verified
self-contained item. No QDATA import, independent human approval or grading.
"""
from __future__ import annotations
import base64
import csv
import hashlib
import html
import io
import json
from collections import defaultdict, Counter
from pathlib import Path
from PIL import Image, ImageDraw
import fitz

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"review-artifacts/NOMUSA_FIRST_V65"
PAGES=OUT/"full_original_page_with_item_box"
SUMMARY=ROOT/"review/NOMUSA_FIRST_V65_254_QNET_FULLPAGE_SAFE_REFERENCE_SUMMARY_20261119.json"
V64=ROOT/"review-artifacts/NOMUSA_FIRST_V64/NOMUSA_FIRST_V64_254_ORIGINAL_REGION_IMAGE_QA.json"

def require(v,s):
    if not v:raise AssertionError("HOLD_V65_"+s)
def read(p):return json.loads(p.read_text(encoding="utf-8"))
def sha(b):return hashlib.sha256(b).hexdigest()
def unique_full_page(doc,page_number,rect,id):
    page=doc[page_number-1]
    pix=page.get_pixmap(matrix=fitz.Matrix(1.1,1.1),colorspace=fitz.csRGB,alpha=False)
    im=Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")
    d=ImageDraw.Draw(im)
    xy=tuple(round(x*1.1) for x in rect)
    d.rectangle(xy,outline=(226,42,42),width=5)
    d.rectangle((0,0,min(im.width,300),34),fill=(255,255,255))
    d.text((7,8),f"QNet source p.{page_number} — {id}",fill=(0,0,0))
    p=PAGES/(id+".jpg")
    im.save(p,"JPEG",quality=70,optimize=True)
    blob=p.read_bytes()
    return {"file":str(p.relative_to(OUT)),"sha256":sha(blob),
            "bytes":len(blob),"originalFullPageVisible":True,
            "highlightedRectInOriginalPdfPoints":[round(x,1) for x in rect],
            "notIndependentlyProofread":True}

def gap_ink_heuristic(page,rect,next_rect):
    # Inspect original PDF raster BELOW the crop to the next candidate
    # heading. Presence of ink does not prove the gap belongs to same item.
    if next_rect is None:return None
    below=max(rect.y1,rect.y0+2)
    bottom=min(next_rect.y0-7,page.rect.height-20)
    if bottom-below<14:return {"gapPoints":round(max(0,bottom-below),1),
        "contentDetected":False,"method":"INSUFFICIENT_GAP"}
    box=fitz.Rect(18,below,page.rect.width-18,bottom)
    if box.height<14 or box.width<30:return None
    pix=page.get_pixmap(matrix=fitz.Matrix(1.0,1.0),clip=box,colorspace=fitz.csGRAY,alpha=False)
    image=Image.open(io.BytesIO(pix.tobytes("png"))).convert("L")
    # White paper JPEG anti-alias can appear below 255; count dark pixels.
    dark=sum(1 for x in image.getdata() if x<145)
    share=dark/max(1,image.width*image.height)
    native=page.get_text("text",clip=box,sort=True)
    return {"gapPoints":round(box.height,2),"darkPixelRatio":round(share,5),
        "nativeTextCharacterCount":len("".join(native.split())),
        "contentDetected":bool(share>.012 or len(native.strip())>=30),
        "method":"ORIGINAL_PDF_PIXEL_INK_AND_NATIVE_TEXT_HEURISTIC",
        "interpretation":"Risk clue only: gap may contain next item, diagram, footer, or omitted choices."}

def make_report(records):
    parts=['<!doctype html><html lang="ko"><head><meta charset="utf-8">',
           '<meta name="viewport" content="width=device-width, initial-scale=1">',
           '<title>공인노무사 원본 검토 V65 — 254문항</title>',
           '<style>body{font-family:system-ui,sans-serif;background:#fafafa;color:#222;margin:20px;max-width:1260px}',
           'h1{font-size:1.4rem}p{line-height:1.6}.warn{color:#8a3c12}section{background:white;padding:16px;margin:16px 0;border:1px solid #ddd;border-radius:12px}',
           '.pict{max-width:100%;height:auto;border:1px solid #bbb}.tag{display:inline-block;padding:4px 8px;margin:4px;background:#eee;border-radius:4px}',
           'details{margin-top:12px}summary{cursor:pointer}.tight{color:#b34a15}</style></head><body>',
           '<h1>V65 — Q-Net 공식 원본 전체 페이지 검토 (254개)</h1>',
           '<p class="warn">아래 빨간 사각형은 자동 추출한 잠정 문항 영역입니다. 전체 페이지는 출처 확인용입니다. 보기가 모두 포함되었다는 뜻이 아니며, 법령·판례·공식 정답 검증 및 독립 내용승인은 0건입니다.</p>',
           f'<p>총 {len(records)}문항. 현재 모든 문항은 채점 및 배포 HOLD입니다.</p>']
    for q in records:
        src=q["originalFullPageReviewImage"]["file"].replace("full_original_page_with_item_box/","")
        # HTML sits in OUT parent, so path is relative artifact folder.
        tags=" ".join(f'<span class="tag">{html.escape(s)}</span>' for s in q["reviewRiskFlags"])
        title=html.escape(q["id"])
        parts.append(f'<section id="{title}"><h2>{title}</h2>'
                     f'<p>시험연도 {q["year"]}, 과목 {html.escape(q["subject"])}, '
                     f'원본 PDF {q["originalSourcePdfPage"]}쪽 / 후보영역 높이 {q["cropHeightRatio"]*100:.1f}%</p>'
                     f'{tags}<details><summary>공식 PDF 원본 페이지와 빨간 테두리 확인</summary>'
                     f'<p><img class="pict" loading="lazy" src="full_original_page_with_item_box/{html.escape(src)}" alt="Q-Net 원본페이지에서 추출영역 표시"></p></details>'
                     '<p class="warn">원본 문구·①~⑤·수식·정답표 독립 검증 HOLD</p></section>')
    parts.append('</body></html>')
    (OUT/"NOMUSA_FIRST_V65_254_SOURCE_REVIEW_GALLERY.html").write_text(
       "".join(parts),encoding="utf-8")
def main():
    v=read(V64)
    require(v["targetProvisionalCropImages"]==254 and len(v["rows"])==254,"V64_254")
    # Reuse the exact source-document checker from the preceding PASS V64
    import importlib.util
    script=ROOT/"scripts/nomusa-first-v64-254-official-crop-geometry-content-gate.py"
    spec=importlib.util.spec_from_file_location("v64source",script)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    docs=module.get_docs()
    rows=v["rows"]
    perPage=defaultdict(list)
    for r in rows:
        require(r["officialQNetPdfSha256"] in docs,"SOURCE_SHA_UNKNOWN_"+r["id"])
        key=(r["officialQNetPdfSha256"],r["sourcePdfPage"])
        perPage[key].append(r)
    PAGES.mkdir(parents=True,exist_ok=True)
    review=[]
    flagged=Counter();sourceStages=Counter();states=Counter()
    for r in rows:
        src=r["officialQNetPdfSha256"]
        num=r["sourcePdfPage"]
        page=docs[src][0][num-1]
        rect=fitz.Rect(r["pdfCropRectanglePoints"])
        group=perPage[(src,num)]
        nextItems=[a for a in group
              if a["id"]!=r["id"] and a["pdfCropRectanglePoints"][1]>rect.y0+15]
        nextItem=min(nextItems,key=lambda a:a["pdfCropRectanglePoints"][1]) if nextItems else None
        nextRect=fitz.Rect(nextItem["pdfCropRectanglePoints"]) if nextItem else None
        flags=list(r["originalContentRiskFlags"])
        risk="FULL_ORIGINAL_PAGE_REVIEW_REQUIRED"
        if rect.y1>=page.rect.height-40:flags.append("CROP_NEAR_PAGE_BOTTOM_CONTINUATION_CHECK")
        if rect.height/page.rect.height<.16:flags.append("SHORT_CROP_MAY_OMIT_CHOICES")
        if nextRect is not None and rect.y1>nextRect.y0+7:
            flags.append("CANDIDATE_OVERLAPS_NEXT_NUMBERED_QUESTION")
            risk="OVERLAPPING_CANDIDATE_CROPS_REVIEW"
        gap=gap_ink_heuristic(page,rect,nextRect)
        if gap and gap.get("contentDetected"):
            flags.append("INK_OR_TEXT_BETWEEN_CURRENT_CROP_END_AND_NEXT_QUESTION")
            risk="SUSPECT_GAP_CONTAINS_SOURCE_CONTENT_REVIEW"
        full=unique_full_page(docs[src][0],num,rect,r["id"])
        cleanFlags=sorted(set(flags))
        for flag in cleanFlags:flagged[flag]+=1
        states[risk]+=1;sourceStages[r["stage"]]+=1
        review.append({
            "id":r["id"],"year":r["year"],"subject":r["subject"],
            "questionNumber":r["questionNumber"],"sourceStage":r["stage"],
            "originalSourcePdfSHA256":src,"originalSourcePdfPage":num,
            "candidateCropImage":r["originalCandidateImage"],
            "candidateCropImageSHA256":r["candidateImageSHA256"],
            "originalFullPageReviewImage":full,
            "cropHeightRatio":r["cropHeightAsFractionOfSourcePage"],
            "nearestOtherCandidateQuestionId":nextItem["id"] if nextItem else None,
            "nearestOtherCandidateQuestionCropStart":round(nextRect.y0,2) if nextRect else None,
            "originalPdfGapAfterCropBeforeNextHeading":gap,
            "reviewRiskFlags":cleanFlags,
            "state":risk,
            "fullStemAndFiveOptionsIndependentApproval":False,
            "officialFinalAnswerCellIndependentApproval":False,
            "historicalLawCasesAndAcademicEvidenceApproval":False,
            "independentReviewerApproval":False,"readyForV44":False,
            "scoringApproved":False})
    for doc,_ in docs.values():doc.close()
    require(len(review)==254 and len({x["id"] for x in review})==254,"254_UNIQUE")
    require(sum(sourceStages.values())==254,"STAGE_TOTAL")
    require(all(not r["scoringApproved"] for r in review),"NO_SCORING")
    result={"schema":"NOMUSA_FIRST_V65_254_FULL_ORIGINAL_PAGE_SAFEGUARD_AND_CROP_RISK/1",
        "asOfKST":"2026-11-19",
        "targetUniqueSourceCropIds":254,
        "originalOfficialQNetFullPageReviewerImagesGenerated":len(review),
        "originalPageSHAValidated":254,
        "sourceStages":dict(sorted(sourceStages.items())),
        "geometryRiskStateCounts":dict(sorted(states.items())),
        "individualIssueFlagCounts":dict(sorted(flagged.items())),
        "independentOriginalFiveOptionContentApproved":0,
        "independentOfficialAnswerCellApproved":0,
        "independentHistoricalLegalAcademicContentApproved":0,
        "newAppImports":0,"newScoringApproved":0,
        "status":"PASS_254_UNTRUNCATED_ORIGINAL_PAGE_REFERENCES_WITH_SOURCE_RISK_FLAGS_HOLD_SCORING",
        "warning":"Full-page original references prevent hiding content from reviewers. They do not prove the crop is the complete original exam question or permit grading without independent review.",
        "rows":review}
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"NOMUSA_FIRST_V65_254_FULLPAGE_SOURCE_RISK_QUEUE.json").write_text(
       json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    with (OUT/"NOMUSA_FIRST_V65_254_REVIEW_PRIORITY.csv").open("w",encoding="utf-8-sig",newline="") as f:
        w=csv.writer(f)
        w.writerow(["id","year","subject","number","sourceStage","page",
            "riskState","riskFlags","fullOriginalReferenceJPEG","provisionalCrop","scoring"])
        for q in review:w.writerow([q["id"],q["year"],q["subject"],q["questionNumber"],q["sourceStage"],
          q["originalSourcePdfPage"],q["state"],"|".join(q["reviewRiskFlags"]),
          q["originalFullPageReviewImage"]["file"],q["candidateCropImage"],"HOLD"])
    make_report(review)
    summary={k:v for k,v in result.items() if k!="rows"}
    summary["full254ReviewArtifact"]="review-artifacts/NOMUSA_FIRST_V65/NOMUSA_FIRST_V65_254_FULLPAGE_SOURCE_RISK_QUEUE.json"
    summary["offlineReviewGallery"]="review-artifacts/NOMUSA_FIRST_V65/NOMUSA_FIRST_V65_254_SOURCE_REVIEW_GALLERY.html"
    SUMMARY.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False))
if __name__=="__main__":main()

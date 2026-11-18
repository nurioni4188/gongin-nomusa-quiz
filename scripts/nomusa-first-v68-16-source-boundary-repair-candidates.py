#!/usr/bin/env python3
"""V68: issue actual revised Q-Net original-image crop candidates ONLY for
16 V65 suspicious boundaries (4 overlaps + 12 ink-filled gaps).
Only 4 where the next candidate is exactly the next printed question in the
same subject/year get a revised crop. The other 12 remain explicit HOLD.

Use SHA-checked official PDFs, not OCR text or invented question answers.
Crop ends get clamped just before the next *candidate heading* of the page,
preserving original IDs and images. Revised 4 JPEGs and old/new side-by-side
comparisons are reviewer-only: headings can be false positives, shared text
may cross pages, ①~⑤ may still be incomplete. No QDATA or scoring mutation.
"""
from __future__ import annotations
import hashlib, io, json, csv
from pathlib import Path
from collections import Counter
import fitz
from PIL import Image, ImageDraw, ImageOps

ROOT=Path(__file__).resolve().parents[1]
V65=ROOT/"review-artifacts/NOMUSA_FIRST_V65/NOMUSA_FIRST_V65_254_FULLPAGE_SOURCE_RISK_QUEUE.json"
V64=ROOT/"review-artifacts/NOMUSA_FIRST_V64/NOMUSA_FIRST_V64_254_ORIGINAL_REGION_IMAGE_QA.json"
OUT=ROOT/"review-artifacts/NOMUSA_FIRST_V68"
REPAIRS=OUT/"revised_candidate_question_crops"
COMPARE=OUT/"old_vs_new_original_source_images"
SUMMARY=ROOT/"review/NOMUSA_FIRST_V68_16_QNET_CROP_BOUNDARY_CORRECTION_CANDIDATES_20261119.json"
REPAIRS.mkdir(parents=True,exist_ok=True)
COMPARE.mkdir(parents=True,exist_ok=True)

def read(p):return json.loads(p.read_text(encoding="utf-8"))
def h(b):return hashlib.sha256(b).hexdigest()
def require(x,msg):
 if not x:raise AssertionError("HOLD_V68_"+msg)
def paired(old,new,path,id):
 def preview(im,size=(700,920)):
  z=im.copy().convert("RGB")
  z.thumbnail(size,Image.Resampling.LANCZOS)
  bg=Image.new("RGB",size,"white")
  bg.paste(z,((size[0]-z.width)//2,10))
  return bg
 a,b=preview(old),preview(new)
 can=Image.new("RGB",(1400,970),"white")
 can.paste(a,(0,42));can.paste(b,(700,42))
 dr=ImageDraw.Draw(can)
 dr.text((12,7),"BEFORE (unverified original crop)",fill="black")
 dr.text((712,7),"AFTER (unverified revision)",fill="black")
 can.save(path,"JPEG",quality=78)
 return {"path":str(path.relative_to(OUT)),"sha256":h(path.read_bytes()),
     "revisedOriginalQuestionFullyVerified":False}
def main():
 v65,v64=read(V65),read(V64)
 require(v65["targetUniqueSourceCropIds"]==len(v65["rows"])==254,"V65_SOURCE_254")
 require(v64["targetProvisionalCropImages"]==len(v64["rows"])==254,"V64_BASE_254")
 sourceByID={v["id"]:v for v in v64["rows"]}
 import importlib.util
 spec=importlib.util.spec_from_file_location(
  "v64source",ROOT/"scripts/nomusa-first-v64-254-official-crop-geometry-content-gate.py")
 module=importlib.util.module_from_spec(spec)
 spec.loader.exec_module(module)
 docs=module.get_docs()
 suspicious=[q for q in v65["rows"] if q["state"] in (
   "OVERLAPPING_CANDIDATE_CROPS_REVIEW",
   "SUSPECT_GAP_CONTAINS_SOURCE_CONTENT_REVIEW")]
 counts=Counter(q["state"] for q in suspicious)
 require(dict(counts)=={
  "OVERLAPPING_CANDIDATE_CROPS_REVIEW":4,
  "SUSPECT_GAP_CONTAINS_SOURCE_CONTENT_REVIEW":12},"16_SOURCE_FLAGS_"+str(counts))
 require(len(suspicious)==16 and len({q["id"] for q in suspicious})==16,"16_UNIQUE")
 safe=[];held=[]
 for q in suspicious:
  current=q["id"].split("-")
  following=(q["nearestOtherCandidateQuestionId"] or "").split("-")
  same_valid_sequence=(len(current)==len(following)==5 and
     current[1:4]==following[1:4] and
     int(following[-1])==int(current[-1])+1)
  if same_valid_sequence:
   safe.append(q)
  else:
   held.append({"id":q["id"],"year":q["year"],"subject":q["subject"],
     "currentQuestionNumber":q["questionNumber"],
     "nextProvisionalQuestionId":q["nearestOtherCandidateQuestionId"],
     "originalRisk":q["state"],
     "holdReason":"NEXT_ANCHOR_NOT_CONTIGUOUS_SAME_YEAR_AND_SUBJECT",
     "oldCropPreserved":True,
     "fullOriginalPageReferencePreserved":True,
     "noUnsafeGeometryChangeApplied":True,
     "independentContentApproved":False,"scoringApproved":False})
 require(len(safe)==4 and len(held)==12,"FOUR_SAFE_NEIGHBORS_TWELVE_HOLD")
 edits=[];types=Counter()
 for q in safe:
  id=q["id"]
  previous=sourceByID[id]
  src=q["originalSourcePdfSHA256"]
  require(src==previous["officialQNetPdfSha256"] and src in docs,"SOURCE_PDF_SHA_"+id)
  doc,_=docs[src]
  p=doc[q["originalSourcePdfPage"]-1]
  rect=fitz.Rect(previous["pdfCropRectanglePoints"])
  nextTop=q["nearestOtherCandidateQuestionCropStart"]
  require(nextTop is not None and nextTop>rect.y0+52,"NO_SAFE_NEXT_CANDIDATE_BOUNDARY_"+id)
  bottom=min(p.rect.height-18,nextTop-8)
  if q["state"]=="OVERLAPPING_CANDIDATE_CROPS_REVIEW":
   require(bottom<rect.y1-3,"EXPECTED_OVERLAP_CROP_SHORTEN_"+id)
   correction="SHORTEN_BEFORE_NEXT_HEADING_CANDIDATE"
  else:
   require(bottom>rect.y1+3,"EXPECTED_INK_GAP_CROP_EXTEND_"+id)
   correction="EXTEND_OVER_POTENTIALLY_OMITTED_INK"
  newRect=fitz.Rect(rect.x0,rect.y0,rect.x1,bottom)
  require(newRect.height>=55 and newRect.x0>=0 and newRect.x1<=p.rect.width+1,"BAD_REVISED_RECT_"+id)
  pic=p.get_pixmap(matrix=fitz.Matrix(1.65,1.65),clip=newRect,
       colorspace=fitz.csRGB,alpha=False)
  blob=pic.tobytes("jpeg",jpg_quality=80)
  require(len(blob)>2000,"REVISED_IMAGE_TOO_SMALL_"+id)
  dest=REPAIRS/(id+".jpg");dest.write_bytes(blob)
  old=ROOT/previous["originalCandidateImage"]
  require(old.is_file() and h(old.read_bytes())==previous["candidateImageSHA256"],"OLD_CROP_SHA_"+id)
  with Image.open(old) as im:
   oldPic=im.convert("RGB")
  with Image.open(io.BytesIO(blob)) as im:
   newPic=im.convert("RGB")
  side=paired(oldPic,newPic,COMPARE/(id+"_before_after.jpg"),id)
  types[correction]+=1
  edits.append({
   "id":id,"year":q["year"],"subject":q["subject"],"questionNumber":q["questionNumber"],
   "originalQNetPdfSHA256":src,"pdfPage":q["originalSourcePdfPage"],
   "priorSourceRisk":q["state"],"repairProposal":correction,
   "originalCrop":{"file":previous["originalCandidateImage"],
       "sha256":previous["candidateImageSHA256"],"pdfRect":[round(x,1) for x in rect]},
   "revisedSourceCrop":{"file":str(dest.relative_to(OUT)),"sha256":h(blob),
       "bytes":len(blob),"pdfRect":[round(x,1) for x in newRect],
       "createdFromExactOriginalQNetPDF":True},
   "comparisonPreview":side,
   "nextCandidateQuestionId":q["nearestOtherCandidateQuestionId"],
   "nextCandidateStartPdfY":nextTop,
   "sourceRiskWasExamined":True,
   "allStemFiveOptionsDiagramAndContinuationsVerified":False,
   "historicalExamLawAndOfficialAnswerVerified":False,
   "independentReviewerApproved":False,"readyForV44":False,"scoringApproved":False,
   "status":"SHA_VERIFIED_SOURCE_REGION_REPAIR_CANDIDATE_AWAITING_NATIVE_REVIEW"})
 for doc,_ in docs.values():doc.close()
 require(len(edits)==4 and len({e["id"] for e in edits})==4,"FOUR_CAUTIONARY_REVISIONS")
 require(types["SHORTEN_BEFORE_NEXT_HEADING_CANDIDATE"]==1 and types["EXTEND_OVER_POTENTIALLY_OMITTED_INK"]==3,
  "SAFE_SEQUENTIAL_REPAIR_TYPES")
 report={"schema":"NOMUSA_FIRST_V68_16_QNET_IMAGE_SOURCE_REVISED_BOUNDARY_CANDIDATES/1",
    "asOfKST":"2026-11-19",
    "originalImageQAUniverse":254,
    "sourceGeometrySuspiciousTargets":16,
    "overlapSourceRevisedCandidates":1,
    "inkGapSourceRevisedCandidates":3,
    "unsafeNonsequentialOrCrossSubjectCandidatesHeld":12,
    "unchangedOriginalCandidateImagesPreserved":254,
    "newSeparateRevisedQNetCropImages":len(edits),
    "oldVsNewComparisonImages":len(edits),
    "sourceRepairTypes":dict(sorted(types.items())),
    "independentlyVerifiedFullQuestionAndAllFiveOptions":0,
    "officialAFormAnswerAndExamDateLawVerified":0,
    "newQdataImports":0,"newScoringApproved":0,
    "status":"PASS_4_SEQUENTIAL_QNET_CROP_REVISED_12_UNSAFE_ANCHORS_HELD_NO_SCORING",
    "warning":"Only contiguous printed sequence in same year/subject qualifies for a revised image candidate. 12 unsafe anchors are preserved unchanged; even 4 proposals lack independent full-question verification.",
    "rows":edits,"unsafeHeldRows":held}
 OUT.mkdir(parents=True,exist_ok=True)
 (OUT/"NOMUSA_FIRST_V68_16_CROP_REPAIR_CANDIDATES.json").write_text(
    json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 with (OUT/"NOMUSA_FIRST_V68_16_REPAIR_CANDIDATES.csv").open("w",encoding="utf-8-sig",newline="") as f:
  w=csv.writer(f);w.writerow(["id","year","subject","number","repair","originalQNetPdfSha","PDFPage",
    "originalCrop","revisedCrop","reviewBeforeAfter","independentApproval","scoring"])
  for e in edits:w.writerow([e["id"],e["year"],e["subject"],e["questionNumber"],e["repairProposal"],
    e["originalQNetPdfSHA256"],e["pdfPage"],e["originalCrop"]["file"],e["revisedSourceCrop"]["file"],
    e["comparisonPreview"]["path"],"HOLD","HOLD"])
 short={k:v for k,v in report.items() if k not in ("rows","unsafeHeldRows")}
 short["heldQuestionIDs"]=[q["id"] for q in held]
 short["revisedCandidateQuestionIDs"]=[q["id"] for q in edits]
 short["full16SourceRepairEvidence"]="review-artifacts/NOMUSA_FIRST_V68/NOMUSA_FIRST_V68_16_CROP_REPAIR_CANDIDATES.json"
 SUMMARY.write_text(json.dumps(short,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print(json.dumps(short,ensure_ascii=False))
if __name__=="__main__":main()

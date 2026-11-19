#!/usr/bin/env python3
"""V55 2016 QNet official A management booklet, 125 candidate question positions.

All source is from real Q-Net attached 2016 A PDF and must match V53 SHA.
Numerical OCR page anchors are fallible; saved JPEGs may omit question parts,
tables or five options. NONE are independent source/content approval.
"""
from pathlib import Path
from collections import Counter, defaultdict
import hashlib, io, json, os, re, csv
import requests, fitz, pytesseract
from PIL import Image
os.environ["OMP_THREAD_LIMIT"]="1"
ROOT=Path(__file__).resolve().parents[1]
V53=ROOT/"review/NOMUSA_FIRST_V53_2016_MANAGEMENT_QNET_SOURCE_SUMMARY_20261118.json"
V34=ROOT/"review-artifacts/NOMUSA_FIRST_V34/NOMUSA_FIRST_V34_791_SOURCE_TARGETS.json"
OUT=ROOT/"review-artifacts/NOMUSA_FIRST_V55"
CROPS=OUT/"original_pdf_candidate_crops"
CROPS.mkdir(parents=True,exist_ok=True)
NUM=re.compile(r"^\s*(\d{1,3})\s*[.)．]$")
HEAD=re.compile(r"^\s*(\d{1,3})\s*[.)．]")
def sh(b):return hashlib.sha256(b).hexdigest()
def j(p):return json.loads(p.read_text(encoding="utf-8"))
def check(x,m):
 if not x:raise AssertionError("HOLD_V55_"+m)
def page_numbers(p):
 txt=[]
 for block in p.get_text("dict")["blocks"]:
  for line in block.get("lines",[]):
   s="".join(a.get("text","") for a in line.get("spans",[])).strip()
   m=HEAD.match(s)
   if not m:continue
   n=int(m.group(1));x,y=line["bbox"][:2]
   if 1<=n<=125 and 15<x<p.rect.width*.44 and 16<y<p.rect.height-20:
    txt.append({"number":n,"x":round(x,1),"y":round(y,1),"type":"PDF_NATIVE_TEXT"})
 if len(set(z["number"] for z in txt))>=2:
  return txt,"PDF_NATIVE_TEXT"
 pix=p.get_pixmap(matrix=fitz.Matrix(1.5,1.5),colorspace=fitz.csGRAY,alpha=False)
 with Image.open(io.BytesIO(pix.tobytes("png"))) as im:
  try:
   data=pytesseract.image_to_data(im,lang="eng",config="--oem 1 --psm 11",
        output_type=pytesseract.Output.DICT,timeout=11)
  except Exception as e:return txt,"OCR_FAILURE_"+type(e).__name__
 rows=[]
 for i,val in enumerate(data["text"]):
  m=NUM.match(val.strip())
  if not m:continue
  try:conf=float(data["conf"][i])
  except (TypeError,ValueError):continue
  n=int(m.group(1));x=float(data["left"][i])/1.5;y=float(data["top"][i])/1.5
  if 1<=n<=125 and conf>=30 and 15<x<p.rect.width*.44 and 16<y<p.rect.height-20:
   rows.append({"number":n,"x":round(x,1),"y":round(y,1),
                "type":"OCR_NUMBER_CANDIDATE","confidence":round(conf,1)})
 return (rows,"OCR_NUMBER_CANDIDATE") if rows else (txt,"NO_ANCHORS_HOLD")

def crop(doc,loc,anchors,name,src_sha):
 idx,a=loc
 page=doc[idx]
 after=[v["y"] for v in anchors if v["y"]>a["y"]+24 and abs(v["x"]-a["x"])<45]
 bottom=min(after)-6 if after else page.rect.height-22
 rect=fitz.Rect(18,max(0,a["y"]-10),page.rect.width-18,
                min(page.rect.height-15,max(bottom,a["y"]+68)))
 if rect.height<55:return None
 img=page.get_pixmap(matrix=fitz.Matrix(1.65,1.65),clip=rect,colorspace=fitz.csRGB,alpha=False)
 blob=img.tobytes("jpeg",jpg_quality=76)
 if len(blob)<1800:return None
 path=CROPS/(name+".jpg");path.write_bytes(blob)
 return {"image":str(path.relative_to(OUT)),"sha256":sh(blob),
         "sourcePdfSHA256":src_sha,"officialQnetPdfPageCandidate":idx+1,
         "sourceRectPDFPoints":[round(v,1) for v in rect],
         "entireFiveOptionsAndQuestionIndependentlyCompared":False,
         "verifiedForQDATA":False}
def main():
 info=j(V53);src=info["source"];q=j(V34)
 check(info["directQnetAFilesSHAValidated"]==1,"V53_PRIMARY")
 check(src["sourcePDFSHA256"]=="328d2a7e12623abfb958b3cbfb2ac094688da295f644c502e22ea575c2a4554a","OFFICIAL_PDF_SHA")
 targets=[v for v in q["rows"] if v["year"]==2016 and v["subject"]!="경제학원론"]
 check(len(targets)==125 and set(x["number"] for x in targets)==set(range(1,126)),"TARGETS_1_TO_125")
 r=requests.get(src["officialSourceURL"],headers={"User-Agent":"Mozilla/5.0","Referer":"https://www.q-net.or.kr/"},timeout=(12,100))
 r.raise_for_status();raw=r.content
 check(raw.startswith(b"%PDF") and sh(raw)==src["sourcePDFSHA256"],"DIRECT_QNET_SOURCE_SHA")
 doc=fitz.open(stream=raw,filetype="pdf")
 check(len(doc)==src["pdfPages"]==36,"PDF_36_PAGES")
 locations=defaultdict(list);methods=Counter()
 for ix,page in enumerate(doc):
  anchors,method=page_numbers(page);methods[method]+=1
  for a in anchors:locations[a["number"]].append((ix,a,anchors))
 rows=[];states=Counter()
 for q in targets:
  id=q["id"];n=q["number"];positions=locations[n];ev=None
  if len(positions)==1:
   ix,a,allp=positions[0]
   ev=crop(doc,(ix,a),allp,id,src["sourcePDFSHA256"])
   state="ONE_PROVISIONAL_JPEG_CROP_SOURCE_ONLY" if ev else "CROP_RENDER_UNUSABLE_HOLD"
  elif not positions:state="QUESTION_NUMBER_NOT_DETECTED_HOLD"
  else:state="MULTIPLE_PAGE_NUMBER_HITS_HOLD"
  states[state]+=1
  rows.append({"id":id,"year":2016,"subject":q["subject"],"number":n,
               "legacyAnswerCandidateNumbersUnapproved":q["candidateAnswers"],
               "sourcePDFSHA256":src["sourcePDFSHA256"],
               "officialQNetSourceURL":src["officialSourceURL"],
               "questionPageCandidates":[x[0]+1 for x in positions][:14],
               "provisionalImage":ev,"status":state,
               "officialFinalAnswerKeyCellIndependentlyVerified":False,
               "fullOriginalStemFiveOptionsVerified":False,
               "examDateLawOrTheoryApproved":False,
               "independentHumanProofreaderApproved":False,
               "scoringApproved":False,"readyForV44":False})
 doc.close()
 check(len(rows)==125 and len({x["id"] for x in rows})==125,"125_UNIQUE")
 summary={"schema":"NOMUSA_FIRST_V55_2016_QNET_MANAGEMENT_A_125_PAGE_CANDIDATES/1",
          "asOfKST":"2026-11-18",
          "officialQnetPDFSHAValidated":True,
          "officialPdfPages":36,
          "2016ManagementATargets":125,
          "byStatus":dict(sorted(states.items())),
          "pageOCRMethods":dict(sorted(methods.items())),
          "provisionalCropFiles":states["ONE_PROVISIONAL_JPEG_CROP_SOURCE_ONLY"],
          "approvedFullOriginalStemFiveOptions":0,
          "independentOfficialAnswerCellApprovals":0,
          "approvedHistoricalStatuteTheory":0,
          "independentSecondHumanProofreaderApprovals":0,
          "newQdataImports":0,"newScoringApproved":0,
          "status":"PASS_2016_MANAGEMENT_125_PAGE_TRIAGE_HOLD_INDEPENDENT_SOURCE_PROOFREAD",
          "rows":rows}
 (OUT/"NOMUSA_FIRST_V55_125_QUESTION_PAGE_AND_CROP_REVIEW.json").write_text(
    json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 with (OUT/"NOMUSA_FIRST_V55_125_QUESTION_PAGE_REVIEW.csv").open("w",encoding="utf-8-sig",newline="") as f:
  w=csv.writer(f)
  w.writerow(["id","subject","questionNo","sourceStatus","pageCandidates","cropFile","fiveOptions","scoring"])
  for x in rows:w.writerow([x["id"],x["subject"],x["number"],x["status"],
    "|".join(map(str,x["questionPageCandidates"])),(x["provisionalImage"] or {}).get("image",""),"HOLD","HOLD"])
 compact={k:v for k,v in summary.items() if k!="rows"}
 compact["fullEvidenceArtifact"]="review-artifacts/NOMUSA_FIRST_V55/NOMUSA_FIRST_V55_125_QUESTION_PAGE_AND_CROP_REVIEW.json"
 (ROOT/"review/NOMUSA_FIRST_V55_2016_MGMT125_QNET_PAGE_TRIAGE_SUMMARY_20261118.json").write_text(
    json.dumps(compact,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print(json.dumps(compact,ensure_ascii=False))
if __name__=="__main__":main()

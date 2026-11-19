#!/usr/bin/env python3
"""V51: Locate candidate printed question numbers in 175 original A-form records.

Uses ONLY V50 SHA-locked Q-Net A PDF sources. PDF-native text first, then
digit OCR (eng numerical markers only) on original scanned pages.
All crops and OCR coordinates are preliminary and may omit options, graphs,
shared stems or continuing pages. NO stem transcription, scoring, or approval.
"""
from pathlib import Path
from collections import Counter, defaultdict
from PIL import Image
import fitz, pytesseract, json, hashlib, re, io, os, csv
os.environ["OMP_THREAD_LIMIT"]="1"
ROOT=Path(__file__).resolve().parents[1]
V50=ROOT/"review-artifacts/NOMUSA_FIRST_V50"
OUT=ROOT/"review-artifacts/NOMUSA_FIRST_V51"
CROPS=OUT/"candidate_question_crops"
CROPS.mkdir(parents=True,exist_ok=True)
NUM=re.compile(r"^\s*(\d{1,3})\s*[.)．]\s*$")
HEAD=re.compile(r"^\s*(\d{1,3})\s*[.)．]")
def sha(b):return hashlib.sha256(b).hexdigest()
def load(p):return json.loads(p.read_text(encoding="utf-8"))
def assert_v(ok,msg):
 if not ok:raise AssertionError("HOLD_V51_"+msg)

def page_anchors(page):
 native=[]
 for block in page.get_text("dict")["blocks"]:
  for line in block.get("lines",[]):
   t="".join(s.get("text","") for s in line.get("spans",[]))
   m=HEAD.match(t)
   if not m:continue
   n=int(m.group(1));x,y=line["bbox"][:2]
   if 1<=n<=125 and 10<x<page.rect.width*.43 and 18<y<page.rect.height-20:
    native.append({"number":n,"x":round(x,1),"y":round(y,1),"source":"PDF_NATIVE"})
 if len({a["number"] for a in native})>=2:return native,"PDF_NATIVE"
 pix=page.get_pixmap(matrix=fitz.Matrix(1.45,1.45),colorspace=fitz.csGRAY,alpha=False)
 with Image.open(io.BytesIO(pix.tobytes("png"))) as image:
  try:
   data=pytesseract.image_to_data(image,lang="eng",config="--oem 1 --psm 11",
       output_type=pytesseract.Output.DICT,timeout=9)
  except Exception as e:
   return native,"OCR_TIMEOUT_OR_ERROR_"+type(e).__name__
 guesses=[]
 for i,t in enumerate(data["text"]):
  m=NUM.match(t)
  if not m:continue
  try:confidence=float(data["conf"][i])
  except (ValueError,TypeError):continue
  n=int(m.group(1));x=float(data["left"][i])/1.45;y=float(data["top"][i])/1.45
  if 1<=n<=125 and confidence>=30 and 10<x<page.rect.width*.43 and 18<y<page.rect.height-20:
   guesses.append({"number":n,"x":round(x,1),"y":round(y,1),"source":"OCR_DIGIT_GUESS","confidence":round(confidence,1)})
 return (guesses,"OCR_DIGIT_GUESS") if guesses else (native,"NO_RELIABLE_HEADING")

def candidate_crop(doc,page_idx,anchor,anchors,sourcehash,id):
 page=doc[page_idx];y=anchor["y"]
 after=[v["y"] for v in anchors if v["y"]>y+25 and abs(v["x"]-anchor["x"])<45]
 bot=min(after)-6 if after else page.rect.height-25
 rect=fitz.Rect(18,max(0,y-10),page.rect.width-18,min(page.rect.height-15,max(y+65,bot)))
 if rect.height<55:return None
 pix=page.get_pixmap(matrix=fitz.Matrix(1.6,1.6),clip=rect,colorspace=fitz.csRGB,alpha=False)
 raw=pix.tobytes("jpeg",jpg_quality=76)
 if len(raw)<2000:return None
 path=CROPS/(id+".jpg");path.write_bytes(raw)
 return {"file":str(path.relative_to(OUT)),"sha256":sha(raw),"bytes":len(raw),
         "officialPdfSHA256":sourcehash,"sourcePdfPage":page_idx+1,
         "cropRectPoints":[round(v,1) for v in rect],
         "provenance":"SHA_CHECKED_QNET_PDF_DIGIT_ANCHOR_PROVISIONAL",
         "independentlyOriginalTextApproved":False}

def main():
 v=load(V50/"NOMUSA_FIRST_V50_686_ENRICHED_SOURCE_QUEUE.json")
 assert_v(v["original686Preserved"]==686 and v["newOfficialAFormBookletSHAConnections"]==175,"BASE")
 docs={}
 for key,entry in v["officialDocuments"].items():
  file=V50/entry["file"];assert_v(file.is_file(),"MISSING_"+key)
  raw=file.read_bytes()
  assert_v(sha(raw)==entry["sha256"] and raw.startswith(b"%PDF"),"OFFICIAL_SHA_"+key)
  docs[key]=(fitz.open(stream=raw,filetype="pdf"),entry)
 rows=[r for r in v["rows"] if r["v50NewDocument"] and r["v50NewDocument"]["grade"].startswith("OFFICIAL_QNET")]
 assert_v(len(rows)==175 and len({x["id"] for x in rows})==175,"175_UNIQUE")
 wanted=defaultdict(list)
 for row in rows:wanted[row["v50NewDocument"]["sourceBooklet"]].append(row)
 allAnchors={};ocrModes=Counter()
 for key,(doc,entry) in docs.items():
  hits=defaultdict(list)
  for ix,page in enumerate(doc):
   candidates,mode=page_anchors(page)
   ocrModes[mode]+=1
   for a in candidates:
    # Store a page-level heading candidate; duplicate numbers across the
    # booklet prevent firm per-question association.
    hits[a["number"]].append((ix,a,candidates))
  allAnchors[key]=hits
 records=[];counter=Counter()
 for r in rows:
  ref=r["v50NewDocument"]; key=ref["sourceBooklet"];num=r["questionNumber"]
  options=allAnchors[key].get(num,[])
  item={"id":r["id"],"year":r["year"],"subject":r["subject"],
   "questionNumber":num,"officialSourceBooklet":key,
   "officialSourcePdfSHA256":ref["pdfSha256"],
   "officialAnswerCellComparedToFinalGrid":False,
   "originalFullStemFiveOptionsFormulaVerified":False,
   "fullIndependentHumanNativeProofread":False,
   "historicalLawOrAcademicTheoryVerified":False,
   "fiveOptionReasoningWrittenAndApproved":False,
   "newScoringApproved":False,"crop":None,
   "pageCandidates":[i+1 for i,*_ in options][:15]}
  if len(options)==1:
   ix,anchor,pageCandidates=options[0]
   crop=candidate_crop(docs[key][0],ix,anchor,pageCandidates,ref["pdfSha256"],r["id"])
   item["crop"]=crop
   item["state"]="SINGLE_HEADING_CROP_PROVISIONAL" if crop else "CROP_RENDER_HOLD"
  elif len(options)>1:item["state"]="MULTIPLE_HEADING_PAGE_CANDIDATES_HOLD"
  else:item["state"]="UNDETECTED_QUESTION_HEADING_HOLD"
  counter[item["state"]]+=1
  records.append(item)
 for doc,_ in docs.values():doc.close()
 assert_v(len(records)==175 and all(not x["newScoringApproved"] for x in records),"NO_SCORE")
 result={"schema":"NOMUSA_FIRST_V51_175_OFFICIAL_PDF_NATIVE_PAGE_DIGIT_LOCATOR/1",
         "asOfKST":"2026-11-18","officialAformBooklets":3,
         "officialSourceSHAValidation":3,"targetQuestionIds":175,
         "yearCounts":dict(sorted(Counter(str(r["year"]) for r in records).items())),
         "stateCounts":dict(sorted(counter.items())),
         "pageOCRModes":dict(sorted(ocrModes.items())),
         "provisionalIndividualCrops":counter["SINGLE_HEADING_CROP_PROVISIONAL"],
         "independentFullSourceTextApprovals":0,
         "independentlyVerifiedOfficialAFormAnswerCells":0,
         "independentlyVerifiedFiveOptionExplanations":0,
         "newScoringApproved":0,"newAppImports":0,
         "status":"PASS_OFFICIAL_PDF_SHA_PAGE_ANCHOR_TRIAGE_HOLD_ALL_INDEPENDENT_SOURCE_PROOFREAD",
         "meaning":"Numerical headers and provisional JPGs locate potential source pages only. May include adjacent questions or omit required options; no OCR transcription or scoring approval.",
         "rows":records}
 OUT.mkdir(parents=True,exist_ok=True)
 (OUT/"NOMUSA_FIRST_V51_175_QUESTION_LOCATOR.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 with (OUT/"NOMUSA_FIRST_V51_175_REVIEW_QUEUE.csv").open("w",encoding="utf-8-sig",newline="") as f:
  w=csv.writer(f);w.writerow(["id","year","subject","number","state","candidatePages","sourcePdfSHA","cropFile","finalIndependentApproval"])
  for r in records:
   w.writerow([r["id"],r["year"],r["subject"],r["questionNumber"],r["state"],
    "|".join(map(str,r["pageCandidates"])),r["officialSourcePdfSHA256"],(r["crop"] or {}).get("file",""),"HOLD"])
 summary={k:v for k,v in result.items() if k!="rows"}
 summary["fullEvidenceArtifact"]="review-artifacts/NOMUSA_FIRST_V51/NOMUSA_FIRST_V51_175_QUESTION_LOCATOR.json"
 (ROOT/"review/NOMUSA_FIRST_V51_175_QNET_AFORM_PAGE_TRIAGE_SUMMARY_20261118.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print(json.dumps(summary,ensure_ascii=False))
if __name__=="__main__":main()

#!/usr/bin/env python3
"""V61: link 100 known-page and infer bounded-page candidates for 26 unknown
2020/2021 A-form questions that were unresolved by V48.

Only SHA-verified Q-Net 88-page JPEG originals and historic source-page
candidate metadata are used. No full stem, option, final key, statute,
precedent, independent expert or scoring approval is implied.
"""
from __future__ import annotations
import csv,hashlib,json,re
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
V34=ROOT/"review-artifacts/NOMUSA_FIRST_V34/NOMUSA_FIRST_V34_791_SOURCE_TARGETS.json"
V38=ROOT/"review/NOMUSA_FIRST_V38_88_NATIVE_PAGE_SOURCE_20261118.json"
V41=ROOT/"review/NOMUSA_FIRST_V41_103_CROP_SHA_20261118.json"
V42=ROOT/"review/NOMUSA_FIRST_V42_FOUR_MANUAL_CROP_REPAIRS_20261118.json"
V61=ROOT/"study-hub/legacy-first-v61-sources.js"
IMG=ROOT/"study-hub/first-v38-qnet-pages-2020-2021"
V48CROPS=ROOT/"review/first-v48-provisional-crops"
OUT=ROOT/"review-artifacts/NOMUSA_FIRST_V61"
SUMMARY=ROOT/"review/NOMUSA_FIRST_V61_2020_2021_UNRESOLVED126_PAGE_EVIDENCE_20261118.json"
def load(p):return json.loads(p.read_text(encoding="utf8"))
def sha(b):return hashlib.sha256(b).hexdigest()
def check(cond,msg):
 if not cond:raise AssertionError("HOLD_V61_"+msg)

def main():
 v34=load(V34);v38=load(V38);v41=load(V41);v42=load(V42)
 js=V61.read_text(encoding="utf8")
 ledger=json.loads(js[js.index("{"):js.rfind(";")])
 exclusions={q["id"] for q in v41["files"]}|{"legacy1-2020-A-management-101","legacy1-2021-A-management-110"}
 check(len(exclusions)==105,"V41_V42_EXCLUSIONS")
 allq=[q for q in v34["rows"] if q["year"] in (2020,2021) and q["id"] not in exclusions]
 check(len(allq)==195,"2020_2021_REMAINING_195")
 original={q["id"]:q for q in allq}
 check(len(original)==195,"UNIQUE_195")
 check(v38["uniqueImagePages"]==88 and v38["OCRPageCandidates"]==274,"V38_SOURCE_PAGES")
 sourceImgs={}
 for d in v38["sourceDocuments"]:
  for item in d["images"]:
   img=IMG/item["image"]
   check(img.is_file() and sha(img.read_bytes())==item["sha256"],"SOURCE_PAGE_JPEG_SHA_"+item["image"])
   sourceImgs[(d["key"],item["page"])]={"path":str(img.relative_to(ROOT)),
      "jpegSHA256":item["sha256"],"pdfPage":item["page"],
      "sourcePdfSHA256":d["pdfSHA256"],
      "fullPageNotQuestionCrop":True}
 check(len(sourceImgs)==88,"QNET_88_SHA_PAGES")
 cropIDs={p.stem for p in V48CROPS.glob("*.jpg")}
 check(len(cropIDs)==67 and cropIDs.issubset(original.keys()),"V48_67")
 known=[]
 unresolved=[]
 for q in allq:
  record=ledger["records"].get(q["id"])
  check(record and q["sourceDocumentSHA256"] is not None,"NON_QNET_2020_2021_"+q["id"])
  source=record["source"];page=q.get("candidatePdfPage")
  if page is not None:
   check((source,page) in sourceImgs,"PAGE_IMAGE_SOURCE_MISSING_"+q["id"])
  info={"id":q["id"],"year":q["year"],"subject":q["subject"],
       "questionNumber":q["number"],"source":source,
       "sourcePdfSHA256":q["sourceDocumentSHA256"],"v38OCRPageCandidate":page}
  if q["id"] in cropIDs:known.append(info)
  else:unresolved.append(info)
 check(len(known)==67 and len(unresolved)==128,"195_MINUS_67")
 # V48's 195 includes two V42 legal-only originals. Distinguish them
 # from the 126 page-anchor failures, whose V48 source grade excludes
 # repaired legal crops even though they share an official 2020/21 PDF.
 repairs={x["id"] for x in v42["records"] if x["id"] not in exclusions}
 check(len(repairs)==2 and repairs.issubset({q["id"] for q in unresolved}),"TWO_LEGAL_REPAIRS")
 pending=[q for q in unresolved if q["id"] not in repairs]
 check(len(pending)==126,"V48_PENDING_126")
 knownByGroup=defaultdict(list)
 for q in known+pending:
  if q["v38OCRPageCandidate"] is not None:
   knownByGroup[q["source"]].append(q)
 result=[];status=Counter()
 for q in pending:
  page=q["v38OCRPageCandidate"];source=q["source"]
  guessPages=[]
  if page is not None:
   state="V38_OFFICIAL_QNET_ORIGINAL_FULL_PAGE_IMAGE_REVIEW_HOLD"
   guessPages=[page]
  else:
   neighbors=knownByGroup[source]
   before=[x for x in neighbors if x["questionNumber"]<q["questionNumber"]]
   after=[x for x in neighbors if x["questionNumber"]>q["questionNumber"]]
   lower=max(before,key=lambda x:x["questionNumber"]) if before else None
   upper=min(after,key=lambda x:x["questionNumber"]) if after else None
   lo=lower["v38OCRPageCandidate"] if lower else None
   hi=upper["v38OCRPageCandidate"] if upper else None
   if lo is not None and hi is not None and lo<=hi and hi-lo<=2:
    guessPages=list(range(lo,hi+1))
    state="ORDERED_V38_OCR_PAGE_BRACKET_REVIEW_HOLD"
   else:
    state="NO_TIGHT_QNET_ORIGINAL_PAGE_BRACKET_HOLD"
  images=[sourceImgs[(source,p)] for p in guessPages if (source,p) in sourceImgs]
  status[state]+=1
  result.append({
    **q,"state":state,
    "candidatePdfPages":guessPages,
    "QnetFullOriginalPagePreviewsSHA":images,
    "questionStartEndOriginalPageIndependentlyVerified":False,
    "originalStemAndFiveOptionsVerified":False,
    "formulaGraphicTableVerified":False,
    "officialFinalAFormAnswerCellVerified":False,
    "examDateLawAndTheoryVerified":False,
    "independentHumanReviewerApproval":False,
    "readyForV44":False,"scoringApproved":False
  })
 check(len(result)==126 and len({q["id"] for q in result})==126,"126_UNIQUE_HOLD")
 check(status["V38_OFFICIAL_QNET_ORIGINAL_FULL_PAGE_IMAGE_REVIEW_HOLD"]==100,"100_PRELIM_PAGES")
 check(status["ORDERED_V38_OCR_PAGE_BRACKET_REVIEW_HOLD"]+status["NO_TIGHT_QNET_ORIGINAL_PAGE_BRACKET_HOLD"]==26,"26_MISSING_PAGES")
 report={"schema":"NOMUSA_FIRST_V61_2020_2021_126_ORIGINAL_SOURCE_PAGE_REVIEW/1",
  "asOfKST":"2026-11-18",
  "total2020And2021Remaining195":195,
  "priorV48ProvisionalQuestionCropsPreserved":67,
  "priorV42LegalOriginalImageCropsPreserved":2,
  "unresolvedOriginalSourceQuestionIds":126,
  "existingQNetPdfPageJPGsSHAValidated":88,
  "alreadyOCRPageCandidateWithDirectFullPageJPG":100,
  "previouslyNoPdfPageWithOrderedBracket":status["ORDERED_V38_OCR_PAGE_BRACKET_REVIEW_HOLD"],
  "previouslyNoPdfPageStillUnbounded":status["NO_TIGHT_QNET_ORIGINAL_PAGE_BRACKET_HOLD"],
  "stateCounts":dict(sorted(status.items())),
  "individualQuestionOriginalTextFiveOptionsApproved":0,
  "independentOfficialAnswerKeyCellApproved":0,
  "legalAcademicExpertApproved":0,
  "newQDATAImports":0,"newScoringApproved":0,
  "status":"PASS_126_2020_2021_QNET_PDF_PAGE_REVIEW_QUEUE_HOLD_ALL_CONTENT_APPROVALS",
  "warning":"Original page SHA and nearest original page number are not a verified single question location, five options, answer, or historical law.",
  "rows":result}
 OUT.mkdir(parents=True,exist_ok=True)
 (OUT/"NOMUSA_FIRST_V61_126_ORIGINAL_QNET_PAGE_REVIEW.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 with (OUT/"NOMUSA_FIRST_V61_126_REVIEW_QUEUE.csv").open("w",encoding="utf-8-sig",newline="") as f:
  w=csv.writer(f);w.writerow(["id","year","subject","number","source","sourceSha","pageCandidates","stage","independentOriginalApproved","scoring"])
  for q in result:w.writerow([q["id"],q["year"],q["subject"],q["questionNumber"],
    q["source"],q["sourcePdfSHA256"],"|".join(map(str,q["candidatePdfPages"])),q["state"],"HOLD","HOLD"])
 short={k:v for k,v in report.items() if k!="rows"}
 short["full126EvidenceArtifact"]="review-artifacts/NOMUSA_FIRST_V61/NOMUSA_FIRST_V61_126_ORIGINAL_QNET_PAGE_REVIEW.json"
 SUMMARY.write_text(json.dumps(short,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 print(json.dumps(short,ensure_ascii=False))
if __name__=="__main__":main()

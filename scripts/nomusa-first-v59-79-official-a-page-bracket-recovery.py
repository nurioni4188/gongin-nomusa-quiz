#!/usr/bin/env python3
"""V59 ordered-page triage for V51 79 unresolved 2016/2018 Q-Net A-form items.

Works with V50 exact official Q-Net PDF SHA and V51 image/number probes.
Never assigns an exact printed question coordinate to inferred pages.
Full page source JPEGs are review aids only; all independent proofreading,
five-option, formulas and historic official final-key approvals remain zero.
"""
from pathlib import Path
from collections import defaultdict,Counter
import json,csv,hashlib
import fitz

ROOT=Path(__file__).resolve().parents[1]
V50=ROOT/"review-artifacts/NOMUSA_FIRST_V50/NOMUSA_FIRST_V50_686_ENRICHED_SOURCE_QUEUE.json"
V51=ROOT/"review-artifacts/NOMUSA_FIRST_V51/NOMUSA_FIRST_V51_175_QUESTION_LOCATOR.json"
SOURCE=ROOT/"review-artifacts/NOMUSA_FIRST_V50"
OUT=ROOT/"review-artifacts/NOMUSA_FIRST_V59"
IMAGES=OUT/"official_qnet_full_page_previews"
SUMMARY=ROOT/"review/NOMUSA_FIRST_V59_79_QNET_PAGE_BRACKET_SUMMARY_20261118.json"
OUT.mkdir(parents=True,exist_ok=True)
IMAGES.mkdir(parents=True,exist_ok=True)
def check(cond,msg):
 if not cond:raise AssertionError("HOLD_V59_"+msg)
def read(p):return json.loads(p.read_text(encoding="utf-8"))
def sha(blob):return hashlib.sha256(blob).hexdigest()
def main():
 v50=read(V50);v51=read(V51)
 check(v50["newOfficialAFormBookletSHAConnections"]==175,"V50_175")
 check(v51["targetQuestionIds"]==175 and v51["provisionalIndividualCrops"]==96,"V51_96")
 docs={}
 for key,desc in v50["officialDocuments"].items():
  path=SOURCE/desc["file"]
  check(path.is_file(),"QNET_SOURCE_PDF_NOT_DOWNLOADED_"+key)
  raw=path.read_bytes()
  check(sha(raw)==desc["sha256"] and raw.startswith(b"%PDF"),"QNET_SOURCE_SHA_CHANGE_"+key)
  d=fitz.open(stream=raw,filetype="pdf")
  check(len(d)==desc["pages"],"SOURCE_PAGECOUNT_"+key)
  docs[key]=(d,desc)
 bygroup=defaultdict(list)
 for row in v51["rows"]:bygroup[row["officialSourceBooklet"]].append(row)
 check(sum(len(v) for v in bygroup.values())==175 and len(bygroup)==3,"THREE_OFFICIAL_GROUPS")
 unresolved=[x for x in v51["rows"] if x["crop"] is None]
 check(len(unresolved)==79 and len({x["id"] for x in unresolved})==79,"V51_79_UNRESOLVED")
 preview_cache={};out=[];states=Counter()
 for key,group in bygroup.items():
  known={r["questionNumber"]:r["crop"]["sourcePdfPage"] for r in group if r["crop"]}
  for q in group:
   if q["crop"]:continue
   n=q["questionNumber"]
   lower=max([p for p in known if p<n],default=None)
   upper=min([p for p in known if p>n],default=None)
   lo=known.get(lower) if lower is not None else None
   hi=known.get(upper) if upper is not None else None
   bounded=lo is not None and hi is not None and lo<=hi and hi-lo<=2
   bracket=list(range(lo,hi+1)) if bounded else []
   hits=sorted(set(p for p in q["pageCandidates"] if p in bracket))
   if bounded and len(hits)==1:
    stage="MULTIPLE_NUMBER_HITS_FILTERED_TO_ONE_NEIGHBOR_PAGE_CANDIDATE"
    candidate=hits
   elif bounded:
    stage="ORDINALLY_BOUNDED_SOURCE_PAGE_REVIEW"
    candidate=bracket
   else:
    stage="NO_TIGHT_ORDERED_PAGE_BOUNDS_HOLD"
    candidate=[]
   imgs=[]
   doc,desc=docs[key]
   for page in candidate:
    token=(key,page)
    if token not in preview_cache:
     pix=doc[page-1].get_pixmap(matrix=fitz.Matrix(1.4,1.4),
      colorspace=fitz.csRGB,alpha=False)
     blob=pix.tobytes("jpeg",jpg_quality=75)
     path=IMAGES/("%s_p%03d.jpg"%(key,page))
     path.write_bytes(blob)
     preview_cache[token]={
      "path":str(path.relative_to(OUT)),"sha256":sha(blob),
      "QnetPdfSHA256":desc["sha256"],"pdfPage":page,
      "wholePageNotQuestionCrop":True}
    imgs.append(preview_cache[token])
   states[stage]+=1
   out.append({
    "id":q["id"],"year":q["year"],"subject":q["subject"],
    "questionNumber":n,"officialAFormSourceBooklet":key,
    "sourcePdfSHA256":desc["sha256"],
    "previousUniqueHeading":lower,"previousUniquePdfPage":lo,
    "nextUniqueHeading":upper,"nextUniquePdfPage":hi,
    "previousV51Candidates":q["pageCandidates"],
    "candidatePageBrackets":candidate,"originalFullPagePreviews":imgs,
    "state":stage,
    "independentPrintedQuestionPositionApproved":False,
    "independentOriginalStemOptionsApproved":False,
    "officialFinalAnswerKeyCellIndependentlyApproved":False,
    "mathGraphsAndExamDateLawVerified":False,
    "independentExpertSignoff":False,"readyForV44":False,
    "scoringApproved":False})
 for doc,_ in docs.values():doc.close()
 check(len(out)==79 and all(not q["scoringApproved"] for q in out),"NO_SCORE")
 report={"schema":"NOMUSA_FIRST_V59_79_QNET_AFORM_UNRESOLVED_PAGE_BRACKETS/1",
  "asOfKST":"2026-11-18","unresolvedQuestionIDs":79,
  "officialQnetAFormPDFHashesMatched":3,
  "preExistingV51IndividualProvisionalCropsPreserved":96,
  "orderedPageBracketsFound":79-states["NO_TIGHT_ORDERED_PAGE_BOUNDS_HOLD"],
  "unresolvedWithoutTightBracket":states["NO_TIGHT_ORDERED_PAGE_BOUNDS_HOLD"],
  "uniqueOfficialFullPageJPEGsForReview":len(preview_cache),
  "stateCounts":dict(sorted(states.items())),
  "fullQuestionAndFiveOptionsApproved":0,"officialFinalAnswerCellApproved":0,
  "independentHistoricalLegalAcademicContentApproved":0,
  "newQDATAImports":0,"newScoringApproved":0,
  "status":"PASS_79_OFFICIAL_PAGE_BRACKET_TRIAGE_HOLD_FINAL_CONTENT_APPROVAL",
  "warning":"Provisional OCR/neighbor bracket constraints from the same scanned Q-Net source. A bracket is NOT a verified individual page or option-proofread.",
  "rows":out}
 (OUT/"NOMUSA_FIRST_V59_79_UNRESOLVED_PAGES_REVIEW.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 with (OUT/"NOMUSA_FIRST_V59_79_REVIEW_QUEUE.csv").open("w",encoding="utf-8-sig",newline="") as f:
  w=csv.writer(f);w.writerow(["id","year","subject","number","sourceBooklet","priorPageHits","candidatePageBracket","risk","scoring"])
  for q in out:w.writerow([q["id"],q["year"],q["subject"],q["questionNumber"],q["officialAFormSourceBooklet"],
   "|".join(map(str,q["previousV51Candidates"])),"|".join(map(str,q["candidatePageBrackets"])),q["state"],"HOLD"])
 summary={k:v for k,v in report.items() if k!="rows"}
 summary["full79EvidenceArtifact"]="review-artifacts/NOMUSA_FIRST_V59/NOMUSA_FIRST_V59_79_UNRESOLVED_PAGES_REVIEW.json"
 SUMMARY.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 print(json.dumps(summary,ensure_ascii=False))
if __name__=="__main__":main()

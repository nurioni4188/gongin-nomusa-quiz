#!/usr/bin/env python3
"""V66: reduce 14 historical first-stage PDF-source gaps via secondary-host
2017/2019 A-form originals, with SHAs, page and native-text candidates.

These 4 PDFs are republished original Q-Net exam scans (secondary host),
NOT independently authenticated against the original Q-Net downloadable PDF.
No question is scored/approved, even when text and ①~⑤ appear complete.
"""
from __future__ import annotations
import csv, hashlib, json, re, urllib.parse
from collections import Counter, defaultdict
from pathlib import Path
import requests, fitz

ROOT=Path(__file__).resolve().parents[1]
V34=ROOT/"review-artifacts/NOMUSA_FIRST_V34/NOMUSA_FIRST_V34_791_SOURCE_TARGETS.json"
OUT=ROOT/"review-artifacts/NOMUSA_FIRST_V66"
BOOKS=OUT/"secondary_host_source_pdfs"
BOOKS.mkdir(parents=True,exist_ok=True)
SUMMARY=ROOT/"review/NOMUSA_FIRST_V66_2017_2019_14_MIRROR_ORIGINAL_A_SOURCE_SUMMARY_20261119.json"
SOURCES={
 "2017-management":{"url":"https://cbtexam.kr/file/e69ef0b86a/","pages":36},
 "2017-economics":{"url":"https://cbtexam.kr/file/dcd44dc069/","pages":37},
 "2019-management":{"url":"https://cbtexam.kr/file/873c31e2f7/","pages":37},
 "2019-economics":{"url":"https://cbtexam.kr/file/1c888d2970/","pages":38},
}
CIRCLED="①②③④⑤"
HEAD=re.compile(r"(?m)^\s*(\d{1,3})\s*[.．]\s+(?=\S)")
def read(p):return json.loads(p.read_text(encoding="utf8"))
def sha(b):return hashlib.sha256(b).hexdigest()
def require(v,msg):
 if not v:raise AssertionError("HOLD_V66_"+msg)
def collect(doc):
 found=defaultdict(list)
 for idx,page in enumerate(doc):
  text=page.get_text("text",sort=True)
  matches=list(HEAD.finditer(text))
  for j,m in enumerate(matches):
   n=int(m.group(1))
   if not 1<=n<=125:continue
   end=matches[j+1].start() if j+1<len(matches) else len(text)
   candidate=text[m.start():end]
   found[n].append({"pdfPage":idx+1,"textUnverifiedCandidate":candidate[:5000],
       "fiveOptionUnicodeMarkersFound":sum(c in candidate for c in CIRCLED),
       "sourceHasNativeText":len(text)>100})
 return found
def main():
 q=read(V34)
 targets=[r for r in q["rows"] if r["year"] in (2017,2019)]
 require(len(targets)==14 and len({r["id"] for r in targets})==14,"14_TARGETS")
 books={};positions={}
 for k,meta in SOURCES.items():
  response=requests.get(meta["url"],headers={"User-Agent":"Mozilla/5.0","Accept":"application/pdf,*/*"},
     timeout=(12,90))
  response.raise_for_status()
  raw=response.content
  require(raw.startswith(b"%PDF"),"EXPECTED_PDF_"+k)
  doc=fitz.open(stream=raw,filetype="pdf")
  require(len(doc)==meta["pages"],"PAGE_COUNT_"+k)
  first=doc[0].get_text("text",sort=True)
  require("A형" in first,"A_FORM_NOT_IN_FIRST_PAGE_"+k)
  path=BOOKS/(k+".pdf")
  path.write_bytes(raw)
  books[k]={"url":meta["url"],"pdfSha256":sha(raw),"pages":len(doc),"bytes":len(raw),
    "sourceProvenance":"SECONDARY_ARCHIVE_OF_QNET_EXAM_PDF_NOT_OFFICIAL_SHA_AUTHENTICATED",
    "firstPageAFormMarker":True,"file":str(path.relative_to(OUT)),
    "actualOfficialQNetSamePdfVerified":False}
  positions[k]=collect(doc)
  doc.close()
 entries=[];counts=Counter()
 for t in targets:
  k=str(t["year"])+("-economics" if "경제학" in t["subject"] else "-management")
  found=positions[k].get(t["number"],[])
  state="ONE_SECONDARY_AFORM_PDF_NATIVE_HEADING_CANDIDATE" if len(found)==1 else (
      "AMBIGUOUS_SECONDARY_AFORM_HEADING_CANDIDATE" if len(found)>1 else
      "QUESTION_HEADING_NOT_LOCATED_SECONDARY_SOURCE")
  counts[state]+=1
  entries.append({"id":t["id"],"year":t["year"],"subject":t["subject"],"questionNumber":t["number"],
      "secondarySourceBooklet":k,"secondarySourcePdfSHA256":books[k]["pdfSha256"],
      "candidatePdfHeadingLocations":[{"pdfPage":m["pdfPage"],
        "fiveOptionUnicodeMarkersFound":m["fiveOptionUnicodeMarkersFound"],
        "textUnreviewedCandidate":m["textUnverifiedCandidate"]} for m in found][:12],
      "previousAnswerCandidateUnapproved":t["candidateAnswers"],
      "state":state,
      "secondaryPdfMatchesOfficialQNetOriginal":False,
      "completeOriginalStemFiveOptionsIndependentlyVerified":False,
      "officialAFormAnswerCellIndependentlyApproved":False,
      "examDateStatutesPrecedentsAcademicEvidenceApproved":False,
      "independentReviewerApproved":False,"readyForV44":False,"scoringApproved":False})
 require(len(entries)==14 and len({r["id"] for r in entries})==14,"14_UNIQUE")
 report={
  "schema":"NOMUSA_FIRST_V66_2017_2019_14_SECONDARY_A_FORM_SOURCE_SHA/1",
  "asOfKST":"2026-11-19",
  "targetYears":{"2017":6,"2019":8},"targetMissingQNetPDFSourceIds":14,
  "secondaryHostMirrorBookletPdfShaValidated":4,
  "individualNativeHeadingStates":dict(sorted(counts.items())),
  "thirdPartyPdfSHAConnectedCandidateIDs":14,
  "officialQNetOriginalPdfEqualityApproved":0,
  "independentFullTextFiveOptionProofread":0,
  "officialFinalAFormKeyCellApproved":0,
  "historicalLawAcademicTheoryProofread":0,
  "newQdataImports":0,"newScoringApproved":0,
  "status":"PASS_14_SECONDARY_PDF_SOURCE_CANDIDATES_HOLD_OFFICIAL_ORIGINAL_AND_CONTENT_APPROVAL",
  "notes":"Neither the secondary host's attribution nor matching an A-form label certifies the independently authenticated Q-Net original, correct question/choice boundaries or final answer.",
  "booklets":books,"rows":entries}
 (OUT/"NOMUSA_FIRST_V66_14_SECONDARY_PDF_ORIGINAL_CANDIDATES.json").write_text(
    json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 with (OUT/"NOMUSA_FIRST_V66_14_REVIEW_QUEUE.csv").open("w",encoding="utf-8-sig",newline="") as f:
  w=csv.writer(f);w.writerow(["id","year","subject","number","PDFSHA","candidatePages","candidateState","approvedOriginal","scoring"])
  for row in entries:w.writerow([row["id"],row["year"],row["subject"],row["questionNumber"],
     row["secondarySourcePdfSHA256"],
     "|".join(str(x["pdfPage"]) for x in row["candidatePdfHeadingLocations"]),row["state"],"HOLD","HOLD"])
 short={k:v for k,v in report.items() if k!="rows"}
 short["complete14ProofreadingQueue"]="review-artifacts/NOMUSA_FIRST_V66/NOMUSA_FIRST_V66_14_SECONDARY_PDF_ORIGINAL_CANDIDATES.json"
 SUMMARY.write_text(json.dumps(short,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 print(json.dumps(short,ensure_ascii=False))
if __name__=="__main__":main()

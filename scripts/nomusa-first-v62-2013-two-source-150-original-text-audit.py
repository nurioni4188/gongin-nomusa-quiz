#!/usr/bin/env python3
"""V62: independent-host comparison of all 2013 A-form question PAGE texts.

Prima facie source A: primeedunet.com original combined 80 page PDF (39+41).
Independent hosting source B: gosi24.com two separate PDF copies, 39 + 41.
Download each file; capture SHA. Normalize native PDF text, compare text and
numbered heading positions one PAGE at a time. This is NOT Q-Net authentication,
a final-choice proofread, an A-form answer-cell check, or grading approval.
"""
from __future__ import annotations
import csv, hashlib, json, re, unicodedata, urllib.parse
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path
import requests, fitz

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"review-artifacts/NOMUSA_FIRST_V62"
SUMMARY=ROOT/"review/NOMUSA_FIRST_V62_2013_150_INDEPENDENT_MIRROR_TEXT_COMPARE_20261119.json"
OUT.mkdir(parents=True,exist_ok=True)
PRIME="https://renew.primeedunet.com/public/file/board/03063ffb-3bd2-4a86-93b9-38fc71a51fbf.pdf"
GOSI={
 "management":"https://gosi24.com/wp-content/uploads/2026/10/2013-exam-2793-6ce7521fd988.pdf",
 "economics":"https://gosi24.com/wp-content/uploads/2026/10/2013-exam-2793-0bab7f9a7ba3.pdf",
}
BASE_SHA="57709f98343d157e7a10ebc73c1a3113661970b22a561a101a0e781cfc5e0677"
SECTIONS={"management":(0,39),"economics":(39,80)}
HEADING=re.compile(r"(?m)^\s*(\d{1,3})\s*[.)．]\s+\S")
def require(x,m):
 if not x:raise AssertionError("HOLD_V62_"+m)
def sha(b):return hashlib.sha256(b).hexdigest()
def download(url, allow_prime_untrusted=False):
 try:
  r=requests.get(url,headers={"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) Chrome/124.0","Accept":"application/pdf,*/*"},timeout=(15,110))
  r.raise_for_status()
  return r.content,True,r.url
 except requests.exceptions.SSLError:
  require(allow_prime_untrusted and urllib.parse.urlsplit(url).hostname=="renew.primeedunet.com",
    "EXTERNAL_TLS_OVERRIDE_PROHIBITED")
  import urllib3
  urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
  r=requests.get(url,headers={"User-Agent":"Mozilla/5.0","Accept":"application/pdf,*/*"},
       timeout=(15,110),verify=False)
  r.raise_for_status()
  return r.content,False,r.url

def canonical(s):
 s=unicodedata.normalize("NFKC",s or "")
 # Do not remove symbols, numerals, original question options or equations.
 return re.sub(r"\s+","",s)
def page_info(page):
 text=page.get_text("text",sort=True)
 matches=[int(x) for x in HEADING.findall(text) if 1<=int(x)<=125]
 return {"text":text,"canonical":canonical(text),"numberHeadings":sorted(set(matches)),
         "characters":len(text)}
def main():
 raw,prime_tls,prime_url=download(PRIME,allow_prime_untrusted=True)
 require(raw.startswith(b"%PDF") and sha(raw)==BASE_SHA,"PRIME_SHA_OR_SIGNATURE_DRIFT")
 base=fitz.open(stream=raw,filetype="pdf")
 require(len(base)==80,"PRIME_80_PAGES")
 altfiles={}
 alt_docs={}
 for k,url in GOSI.items():
  try:
   raw,tls,final=download(url)
  except Exception as e:
   altfiles[k]={"status":"ALTERNATE_DOWNLOAD_HOLD","sourceURL":url,
                "error":type(e).__name__+":"+str(e)[:180]}
   continue
  require(raw.startswith(b"%PDF"),"GOSI_PDF_MAGIC_"+k)
  doc=fitz.open(stream=raw,filetype="pdf")
  require(len(doc)==SECTIONS[k][1]-SECTIONS[k][0],"GOSI_PAGES_"+k)
  altfiles[k]={"status":"SHA_VERIFIED_ALTERNATE_PUBLIC_PDF","sourceURL":url,"resolvedURL":final,
       "sha256":sha(raw),"pages":len(doc),"bytes":len(raw),
       "tlsCertificateVerified":tls,
       "notOfficialQNetSource":True}
  alt_docs[k]=doc
 rows=[];counts=Counter()
 for kind,(start,end) in SECTIONS.items():
  other=alt_docs.get(kind)
  for j in range(end-start):
   ours=page_info(base[start+j])
   if other is None:
    state="ALTERNATE_PDF_DOWNLOAD_HOLD"
    similarity=None;other_heads=[];length_b=None
   else:
    comp=page_info(other[j])
    # Limit SequenceMatcher cost, while using exact text normalizations
    a,b=ours["canonical"],comp["canonical"]
    if a==b:similarity=1.0
    else:similarity=round(SequenceMatcher(None,a,b,autojunk=False).ratio(),6)
    state=("EXACT_PAGE_TEXT_MATCH" if similarity==1 else
           "HIGH_PAGE_TEXT_SIMILARITY_CANDIDATE" if similarity>=.985 else
           "MODERATE_PAGE_TEXT_SIMILARITY_REVIEW" if similarity>=.93 else
           "PAGE_TEXT_DIFFERENCE_NEEDS_NATIVE_INSPECTION")
    other_heads=comp["numberHeadings"];length_b=comp["characters"]
    if ours["numberHeadings"]!=other_heads:
     state="DIFFERENT_PRINTED_HEADING_DETECTION_REVIEW"
   counts[state]+=1
   rows.append({"kind":kind,"combinedOriginalPage":start+j+1,
     "alternateOriginalPage":j+1,
     "originalMirrorSHA256":BASE_SHA,
     "alternateSourceSHA256":altfiles.get(kind,{}).get("sha256"),
     "originalTextCharacters":ours["characters"],
     "alternateTextCharacters":length_b,
     "normalizedTextSimilarity":similarity,
     "primeHeadingNumbers":ours["numberHeadings"],
     "otherHostHeadingNumbers":other_heads,
     "state":state,
     "officialOriginalQNetSameDocumentConfirmed":False,
     "allOriginalQuestionFiveOptionsIndependentlyProofread":False,
     "officialFinalAFormAnswerCellApproved":False,"scoringApproved":False})
 for doc in alt_docs.values():doc.close()
 base.close()
 require(len(rows)==80,"80_PAGE_COMPARISON_LEDGER")
 allDownloaded=len(alt_docs)==2
 report={"schema":"NOMUSA_FIRST_V62_2013_A_CROSS_HOST_NATIVE_PAGE_TEXT_150/1",
  "asOfKST":"2026-11-19",
  "target2013AQuestionCandidates":150,
  "sourceA":{"url":PRIME,"sha256":BASE_SHA,"pages":80,"tlsCertificateVerified":prime_tls},
  "independentPublicHosts":2 if allDownloaded else 1,
  "sourceBByBooklet":altfiles,
  "bookletPageCompareResults":len(rows),
  "pageTextStates":dict(sorted(counts.items())),
  "pageTextsHighConfidenceMatched":sum(v for k,v in counts.items() if k in ("EXACT_PAGE_TEXT_MATCH","HIGH_PAGE_TEXT_SIMILARITY_CANDIDATE")),
  "individualExactStemsFiveOptionsApproved":0,
  "independentQNetOriginalSourceIdentityApproved":0,
  "independentHistoricalLawsCasesApproved":0,
  "officialAFormFinalAnswerCellApproved":0,
  "newAppImports":0,"newScoringApprovals":0,
  "status":("PASS_TWO_HOST_PDF_NATIVE_TEXT_COMPARE_QNET_SOURCE_EQUALITY_HOLD" if allDownloaded else
     "HOLD_ALTERNATE_HOST_DOWNLOAD_PARTIAL"),
  "warning":"Two public hosts are not two independent human proofreaders and are not the official Q-Net release. Similarity only concerns extracted PDF page text, not figures, options correctness or exam-time law.",
  "rows":rows}
 (OUT/"NOMUSA_FIRST_V62_2013_80_PAGES_SOURCE_TEXT_DIFF.json").write_text(
  json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 with (OUT/"NOMUSA_FIRST_V62_2013_80_PAGES_SOURCE_TEXT_DIFF.csv").open("w",encoding="utf-8-sig",newline="") as f:
  w=csv.writer(f);w.writerow(["booklet","primePage","alternatePage","textSimilarity","state","primeHeadings","otherHeadings"])
  for x in rows:w.writerow([x["kind"],x["combinedOriginalPage"],x["alternateOriginalPage"],
     x["normalizedTextSimilarity"],x["state"],"|".join(map(str,x["primeHeadingNumbers"])),
     "|".join(map(str,x["otherHostHeadingNumbers"]))])
 summary={k:v for k,v in report.items() if k!="rows"}
 summary["full80PageCompareArtifact"]="review-artifacts/NOMUSA_FIRST_V62/NOMUSA_FIRST_V62_2013_80_PAGES_SOURCE_TEXT_DIFF.json"
 SUMMARY.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 print(json.dumps(summary,ensure_ascii=False))
if __name__=="__main__":main()

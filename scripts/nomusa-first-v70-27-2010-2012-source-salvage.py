#!/usr/bin/env python3
"""V70 recover original source leads for remaining 27 2010-2012 economics IDs.

2010: public CBTP problem reconstruction with stem + five answer choices.
2011/2012: published HWP scan original attachment via historical exam archive.
All are independent reprints, NOT official original Q-Net certifications;
answer candidates from V34 are not verified against final answers.
No scoring, no app data changes, no fabricated academic explanations.
"""
from __future__ import annotations
import csv,hashlib,json,re,urllib.parse
from collections import Counter
from pathlib import Path
import requests,bs4
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"review-artifacts/NOMUSA_FIRST_V34/NOMUSA_FIRST_V34_791_SOURCE_TARGETS.json"
OUT=ROOT/"review-artifacts/NOMUSA_FIRST_V70"
SUMMARY=ROOT/"review/NOMUSA_FIRST_V70_2010_2012_27_SOURCE_GAP_RECONCILIATION_20261119.json"
OUT.mkdir(parents=True,exist_ok=True)
SOURCES={
 2010:{"url":"https://cbtbank.kr/exam/cfr20100606","expectedMime":"text/html","type":"RECONSTRUCTED_CBT_BANK_NOT_QNET"},
 2011:{"url":"https://app.lawschool.co.kr/nlawschool/board/Download.asp?boardName=pds&code=1502&fileIdx=13376&idx=32815","expectedMime":"HWP","type":"HISTORICAL_A_ECON_HWP_REPRINT_NOT_QNET"},
 2012:{"url":"https://m.lawschool.co.kr/nlawschool/board/Download.asp?boardName=pds&code=1502&fileIdx=19425&idx=39243","expectedMime":"HWP","type":"HISTORICAL_A_ECON_HWP_REPRINT_NOT_QNET"}
}
def sha(b):return hashlib.sha256(b).hexdigest()
def ok(v,t):
 if not v:raise AssertionError("HOLD_V70_"+t)
def get(url):
 try:
  r=requests.get(url,headers={"User-Agent":"Mozilla/5.0 Chrome/124.0","Accept":"*/*"},timeout=(10,40))
  r.raise_for_status()
  return r.content,r.status_code,r.url,None
 except Exception as e:return None,None,url,type(e).__name__+":"+str(e)[:180]
def harvest_2010(text):
 soup=bs4.BeautifulSoup(text,"html.parser")
 for bad in soup.select("script,style,nav,footer"):bad.decompose()
 chunks=[p.strip() for p in soup.get_text("\n",strip=True).splitlines() if p.strip()]
 # Section starts with a printed N. heading, followed by 5 ordered options.
 # Reject any list item 1. that lacks a following exact 1 through 5 pattern.
 candidates={}
 for idx,line in enumerate(chunks):
  m=re.match(r"^(\d{1,3})[.)]\s+(.+)$",line)
  if not m:continue
  n=int(m.group(1))
  if not 1<=n<=25:continue
  tail=chunks[idx+1:idx+32]
  options={}
  for word in tail:
   mi=re.match(r"^([1-5])[.)]\s*(.*)$",word)
   if mi:
    j=int(mi.group(1))
    if j==1 and options:break
    if j not in options:options[j]=mi.group(2).strip()
    if len(options)==5:break
  if len(options)!=5 or min(len(v) for v in options.values())<1:continue
  # Cross-check title is not one of the five choices (list markers should be 1 to 5).
  textstem=m.group(2).strip()
  if len(textstem)<10:continue
  current={"questionNumber":n,"untrustedStemCandidate":textstem,
     "fiveOptionReprintCandidates":[options[i] for i in range(1,6)],
     "paragraphMayOmitTablesEquationsOrSharedStem":True,
     "originalQNetQuestionVisuallyVerified":False}
  if n not in candidates or len(current["untrustedStemCandidate"])>len(candidates[n]["untrustedStemCandidate"]):
   candidates[n]=current
 return candidates,len(chunks)

def main():
 base=json.loads(BASE.read_text(encoding="utf8"))
 rows=[x for x in base["rows"] if x["year"] in (2010,2011,2012)]
 ok(len(rows)==27 and len({x["id"] for x in rows})==27,"27_DISTINCT")
 ok(Counter(x["year"] for x in rows)=={2010:25,2011:1,2012:1},"25_1_1")
 files={};firstYearText={}
 for year,src in SOURCES.items():
  raw,status,url,error=get(src["url"])
  if raw is None:
   files[year]={**src,"status":"DOWNLOAD_HOLD","error":error}
   continue
  isHwp=raw[:8]==bytes.fromhex("D0CF11E0A1B11AE1") or raw[:4]==b"HWP "
  isHtml=b"<html" in raw[:5000].lower() or b"<!doctype" in raw[:5000].lower()
  if year==2010 and not isHtml:
   files[year]={**src,"status":"NOT_HTML_EXPECTED","sha256":sha(raw),"contentType":str(raw[:20])}
   continue
  if year!=2010 and not isHwp:
   files[year]={**src,"status":"NOT_VALID_HWP_DOCUMENT_HOLD","sha256":sha(raw),"firstBytes":raw[:32].hex()}
   continue
  name=("2010_cbtreconstruction.html" if year==2010 else f"{year}_economics_A_reprint.hwp")
  (OUT/name).write_bytes(raw)
  files[year]={**src,"status":"REPRINT_SOURCE_SHA_CANDIDATE_NOT_OFFICIAL",
     "sha256":sha(raw),"bytes":len(raw),"file":name,
     "responseStatus":status,"resolvedUrl":url,"independentlyAuthenticatedAsQNetOriginal":False}
  if year==2010:
   # Public CBT reproduction may not preserve mathematical figures and formula glyphs.
   try: text=raw.decode("utf8")
   except UnicodeDecodeError:text=raw.decode("cp949","replace")
   candidates,nlines=harvest_2010(text)
   firstYearText=candidates
   files[year]["nativeQuestionCandidates"]=len(candidates)
   files[year]["parsedPageLines"]=nlines
 review=[];states=Counter()
 for q in rows:
  year=q["year"];name=q["id"];book=files[year]
  candidate=firstYearText.get(q["number"]) if year==2010 else None
  status=("THIRD_PARTY_CBT_STEM_FIVE_OPTION_CANDIDATE" if candidate else
          "HWP_SOURCE_PROVENANCE_ONLY_QNET_CONTENT_HOLD" if book["status"]=="REPRINT_SOURCE_SHA_CANDIDATE_NOT_OFFICIAL" else
          "OFFICIAL_QUESTION_SOURCE_STILL_UNAVAILABLE_HOLD")
  states[status]+=1
  review.append({"id":name,"year":year,"subject":q["subject"],"questionNumber":q["number"],
    "publicSource":book["url"],
    "sourceSHA256":book.get("sha256"),
    "thirdPartyUnverifiedStem":candidate["untrustedStemCandidate"] if candidate else None,
    "thirdPartyUnverifiedOptions":candidate["fiveOptionReprintCandidates"] if candidate else None,
    "priorAnswerCandidateUnapproved":q["candidateAnswers"],
    "status":status,"sourceMirrorIndependentlyQNetAuthenticated":False,
    "wholeQuestionFiveOptionsIndependentlyProofread":False,
    "finalOfficialAnswerCellApproved":False,"academicMathProofVerified":False,
    "humanIndependentApproval":False,"scoringApproved":False,"readyForV44":False})
 ok(len(review)==27 and len({x["id"] for x in review})==27,"27_RECORDS")
 report={"schema":"NOMUSA_FIRST_V70_2010_2012_27_EXTERNAL_SOURCE_PROVENANCE/1",
   "asOfKST":"2026-11-19",
   "targetUnlinkedQuestionIDs":27,
   "years":{"2010":25,"2011":1,"2012":1},
   "sourceStatusCounts":dict(sorted(states.items())),
   "thirdParty2010FiveOptionCandidates":states["THIRD_PARTY_CBT_STEM_FIVE_OPTION_CANDIDATE"],
   "reprintSourceDocuments":{str(k):v for k,v in files.items()},
   "independentOfficialQNetOriginalApprovals":0,
   "individualOfficialFinalAnswerCellApprovals":0,
   "academicCalculationExplanationApprovals":0,
   "newAppImports":0,"newScoringApproved":0,
   "status":"REPRINT_SOURCE_TRIAGE_ONLY_ALL_ORIGINAL_CONTENT_AND_SCORING_HOLD",
   "warning":"Third-party reconstructed text/archived HWP files may differ from official QNet A original, lose graphs, and are never approved for scoring.",
   "rows":review}
 (OUT/"NOMUSA_FIRST_V70_27_SOURCE_AND_TEXT_REVIEW.json").write_text(
   json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 with (OUT/"NOMUSA_FIRST_V70_27_REVIEW.csv").open("w",encoding="utf-8-sig",newline="") as f:
  w=csv.writer(f);w.writerow(["id","year","subject","number","status","sourceSHA","stemCandidate","optionsCount","grading"])
  for q in review:w.writerow([q["id"],q["year"],q["subject"],q["questionNumber"],
    q["status"],q["sourceSHA256"],q["thirdPartyUnverifiedStem"],
    len(q["thirdPartyUnverifiedOptions"] or []),"HOLD"])
 summary={k:v for k,v in report.items() if k!="rows"}
 summary["full27EvidenceArtifact"]="review-artifacts/NOMUSA_FIRST_V70/NOMUSA_FIRST_V70_27_SOURCE_AND_TEXT_REVIEW.json"
 SUMMARY.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 print(json.dumps(summary,ensure_ascii=False))
if __name__=="__main__":main()

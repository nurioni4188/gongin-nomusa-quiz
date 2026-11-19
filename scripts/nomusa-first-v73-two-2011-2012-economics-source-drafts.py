#!/usr/bin/env python3
"""V73 recover 2011/12 final two 686-source candidates from public CBT reprints.

2011 economy A Q14 is CBT economics exercise 14.
2012 economy A Q119 is elective economics exercise 19 (numbered 101-125
inside the complete A paper); offset 100 is only a booklet-layout assumption,
NOT independently authenticated against official QNet A paper. Exact reprint
source text plus 5 choices are staged; 2012 original graph must be reviewed.
No approval of original QNet, five-choice visual completeness, final key,
economics explanation, independent human reviewer or scored question import.
"""
import csv,hashlib,json,re
from pathlib import Path
from collections import Counter
import requests
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"review-artifacts/NOMUSA_FIRST_V34/NOMUSA_FIRST_V34_791_SOURCE_TARGETS.json"
OUT=ROOT/"review-artifacts/NOMUSA_FIRST_V73"
SUMMARY=ROOT/"review/NOMUSA_FIRST_V73_2011_2012_TWO_LAST_SOURCE_CANDIDATES_20261119.json"
SOURCES={
 2011:{"url":"https://cbtbank.kr/exam/cfr20110612","sourceNo":14,"legacyNo":14},
 2012:{"url":"https://cbtbank.kr/exam/cfr20120609","sourceNo":19,"legacyNo":119}
}
def insist(x,msg):
 if not x:raise AssertionError("HOLD_V73_"+msg)
def sha(b):return hashlib.sha256(b).hexdigest()
def harvest(text,target):
 soup=BeautifulSoup(text,"html.parser")
 for bad in soup.select("script,style,nav,footer"):bad.decompose()
 chunks=[p.strip() for p in soup.get_text("\n",strip=True).splitlines() if p.strip()]
 opts=[]
 for idx,line in enumerate(chunks):
  if line!=str(target) or idx+7>=len(chunks):continue
  if not chunks[idx+1].startswith(". "):continue
  stem=chunks[idx+1][2:].strip()
  choices=chunks[idx+2:idx+7]
  if len(stem)<25 or len(choices)!=5 or any(len(x.strip())<1 for x in choices):continue
  # Other questions/answer explanations may contain the same ordinal,
  # so fail closed if two full five-choice parses have distinct stems.
  opts.append({"stem":stem,"options":choices,"sourceHtmlTextLineStart":idx})
 distinct={x["stem"] for x in opts}
 insist(len(distinct)==1,"AMBIGUOUS_PRINTED_QUESTION_"+str(target))
 return opts[0],len(chunks)
def main():
 base=json.loads(BASE.read_text(encoding="utf8"))
 targets=[x for x in base["rows"] if x["year"] in (2011,2012)]
 insist(len(targets)==2,"EXACT_TWO_UNRESOLVED")
 ids={x["year"]:x for x in targets}
 out=[]
 OUT.mkdir(parents=True,exist_ok=True)
 for year,spec in SOURCES.items():
  r=requests.get(spec["url"],headers={"User-Agent":"Mozilla/5.0 Chrome/124.0","Accept":"text/html,*/*"},
     timeout=(10,70));r.raise_for_status()
  data=r.content
  insist(b"<html" in data[:10000].lower() or b"<!doctype" in data[:10000].lower(),"NOT_HTML_"+str(year))
  name=OUT/(str(year)+"_economics_legacy_CBT_reprint.html");name.write_bytes(data)
  try:t=data.decode("utf8")
  except UnicodeDecodeError:t=data.decode("cp949","replace")
  native,total=harvest(t,spec["sourceNo"])
  q=ids[year]
  insist(q["number"]==spec["legacyNo"] and q["subject"]=="경제학원론","LEGACY_ID_"+str(year))
  risks=["THIRD_PARTY_CBT_NOT_QNET_OFFICIAL_ORIGINAL",
         "SINGLE_REPRINT_SOURCE_NOT_SECOND_HUMAN_REVIEW",
         "FINAL_A_FORM_OFFICIAL_ANSWER_KEY_NOT_INDEPENDENTLY_VERIFIED"]
  if year==2012:
   risks.append("FULL_ORIGINAL_QUESTION_NUMBER_119_ASSUMED_FROM_ECONOMICS_19_PLUS_100")
   risks.append("2012_Q19_TARIFF_DIAGRAM_NOT_INCLUDED_IN_NATIVE_TEXT")
  else:risks.append("ENGEL_CURVE_FORMULA_ALGEBRA_NEEDS_INDEPENDENT_SECOND_REVIEW")
  out.append({
   "id":q["id"],"year":year,"subject":q["subject"],
   "originalHistoricQuestionNumber":q["number"],
   "publishedEconomicsSectionQuestionNumber":spec["sourceNo"],
   "questionNumberMappingIndependentlyVerified":False if year==2012 else True,
   "thirdPartyHtmlSourceURL":spec["url"],
   "thirdPartyHtmlSourceSHA256":sha(data),
   "thirdPartySourceFile":name.name,"htmlTextLines":total,
   "unverifiedStemCandidate":native["stem"],
   "unverifiedFiveOptions":native["options"],
   "priorLegacyAnswerCandidateUnapproved":q["candidateAnswers"],
   "riskFlags":risks,
   "originalQNetAFormSourceIndependentlyVerified":False,
   "completeOriginalFiveOptionsGraphVerified":False,
   "independentOfficialFinalAnswerKeyCellApproved":False,
   "economicsCalculationAndAllOptionReasonsIndependentlyApproved":False,
   "independentHumanReviewersApproved":False,
   "readyForV44":False,"scoringApproved":False,
   "status":"PUBLIC_CBT_REPRINT_TWO_LAST_ECONOMICS_DRAFTS_CONTENT_APPROVAL_HOLD"
  })
 insist(len(out)==2 and len({x["id"] for x in out})==2,"TWO_UNIQUE")
 report={"schema":"NOMUSA_FIRST_V73_2011_2012_TWO_LAST_PUBLIC_CBT_SOURCE_CANDIDATES/1",
   "asOfKST":"2026-11-19",
   "historicalTwoUnlinkedIDs":["legacy1-2011-A-economics-014","legacy1-2012-A-economics-119"],
   "reprintTextFiveOptionCandidates":2,
   "years":{"2011":1,"2012":1},
   "independentlyCertifiedQnetOriginalFiles":0,
   "independentlyConfirmedFinalAnswerCells":0,
   "independentEconomicsExplanations":0,
   "newScoringApprovals":0,"newAppImports":0,
   "status":"PASS_TWO_MISSING_IDS_SECONDARY_HTML_REPRINT_DRAFTS_HOLD_OFFICIAL_ORIGINAL_AND_SCORING",
   "warning":"2012 legacy Q119 ↔ external section Q19 mapping and its figure require independent official original booklet comparison. Both external CBT reconstructions are unapproved drafts.",
   "rows":out}
 (OUT/"NOMUSA_FIRST_V73_LAST_2_NATIVE_STEM_FIVE_OPTION_DRAFTS.json").write_text(
    json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 with (OUT/"NOMUSA_FIRST_V73_LAST_2_DRAFTS.csv").open("w",encoding="utf-8-sig",newline="") as f:
  w=csv.writer(f);w.writerow(["id","year","officialLegacyQuestionNo","externalSectionNo","stemDraft",
    "option1","option2","option3","option4","option5","figureOrMathRisk","scoring"])
  for q in out:w.writerow([q["id"],q["year"],q["originalHistoricQuestionNumber"],q["publishedEconomicsSectionQuestionNumber"],
      q["unverifiedStemCandidate"],*q["unverifiedFiveOptions"],"|".join(q["riskFlags"]),"HOLD"])
 short={k:v for k,v in report.items() if k!="rows"}
 short["fullTwoSourceDraftArtifact"]="review-artifacts/NOMUSA_FIRST_V73/NOMUSA_FIRST_V73_LAST_2_NATIVE_STEM_FIVE_OPTION_DRAFTS.json"
 SUMMARY.write_text(json.dumps(short,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 print(json.dumps(short,ensure_ascii=False))
if __name__=="__main__":main()

#!/usr/bin/env python3
"""V69 actual native PDF source split for 14 2017/2019 missing first-stage items.

Preserve the exact question stem and 5 numbered options from 4 SHA-verified
secondary-host A-form PDFs. Strip printed page footers; flag mathematically
undecodable PDF private-use glyphs. This is a source *draft*, not Q-Net origin,
visual graph, legal analysis, official answer cell or independent signoff.
Never import to live quiz/score.
"""
import json, csv, re
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
V66=ROOT/"review-artifacts/NOMUSA_FIRST_V66/NOMUSA_FIRST_V66_14_SECONDARY_PDF_ORIGINAL_CANDIDATES.json"
OUT=ROOT/"review-artifacts/NOMUSA_FIRST_V69"
SUMMARY=ROOT/"review/NOMUSA_FIRST_V69_14_NATIVE_FIVE_OPTION_SOURCE_DRAFT_SUMMARY_20261119.json"
MARKS="①②③④⑤"
FOOTERS=[
 re.compile(r"(?m)^\s*A형-\d+-\d+\s*$"),
 re.compile(r"(?m)^\s*20(?:17|19)년도제\d+회공인노무사1차1교시A형\s*\([^)]*\)\s*$")
]
def must(v,name):
 if not v:raise AssertionError("HOLD_V69_"+name)
def private_glyphs(s):return sum(0xe000<=ord(c)<=0xf8ff for c in s)
def main():
 v=json.loads(V66.read_text(encoding="utf8"))
 must(v["targetMissingQNetPDFSourceIds"]==14 and len(v["rows"])==14,"V66_14")
 must(v["secondaryHostMirrorBookletPdfShaValidated"]==4,"V66_FOUR_SOURCE_BOOKLETS")
 result=[];flags=Counter()
 for q in v["rows"]:
  cand=q["candidatePdfHeadingLocations"]
  must(len(cand)==1,"UNIQUE_HEADING_"+q["id"])
  source=cand[0]["textUnreviewedCandidate"]
  chunks=re.split("([①②③④⑤])",source)
  marks=[s for s in chunks if s in MARKS]
  must(len(chunks)==11 and marks==list(MARKS),"FIVE_OPTION_SEQUENCE_"+q["id"])
  stem=chunks[0].strip()
  must(re.search(r"^\s*"+str(q["questionNumber"])+r"\s*[.．]",stem),"PRINTED_QUESTION_ID_"+q["id"])
  choices=[];removed=0
  for i in range(5):
   body=chunks[2*i+2].strip()
   for p in FOOTERS:
    body,k=p.subn("",body);removed+=k
   body=body.strip()
   must(bool(body),"EMPTY_OPTION_"+q["id"]+"_"+str(i+1))
   choices.append({"choiceNumber":i+1,"rawNativeTextCandidate":body,
        "PDFPrivateUseGlyphCount":private_glyphs(body),
        "independentOriginalTextProofread":False})
  risks=[]
  if removed:risks.append("REMOVED_PRINTED_PAGE_FOOTER_FROM_OPTION_TEXT")
  if private_glyphs(stem)+sum(c["PDFPrivateUseGlyphCount"] for c in choices):
   risks.append("PDF_PRIVATE_USE_MATH_GLYPHS_NOT_READABLE_AS_TEXT")
  if "표" in stem or "그래프" in stem or "그림" in stem:
   risks.append("TABLE_OR_GRAPH_MUST_BE_VISUALLY_COMPARED")
  if "-civil-" in q["id"]:
   risks.append("EXAM_YEAR_CIVIL_LAW_AND_PRECEDENTS_NOT_APPROVED")
  if "-economics-" in q["id"]:
   risks.append("ECONOMICS_EQUATIONS_GRAPH_NOT_VISUALLY_APPROVED")
  risks.append("SECONDARY_SOURCE_NOT_AUTHENTICATED_AGAINST_OFFICIAL_QNET")
  for risk in risks:flags[risk]+=1
  result.append({"id":q["id"],"year":q["year"],"subject":q["subject"],
    "questionNumber":q["questionNumber"],
    "sourceBooklet":q["secondarySourceBooklet"],
    "sourcePdfPageCandidate":cand[0]["pdfPage"],
    "sourcePdfSHA256":q["secondarySourcePdfSHA256"],
    "questionStemNativeCandidate":stem,"fiveOptionNativeCandidates":choices,
    "printedFootersRemovedFromOptionText":removed,
    "sourceContentRisks":risks,
    "legacyAnswerCandidateUnapproved":q["previousAnswerCandidateUnapproved"],
    "originalOfficialQNetBookletIndependentlyCertified":False,
    "originalFullQuestionFiveChoicesIndependentlyVerified":False,
    "examDateLawOrEconomicsCalculationApproved":False,
    "officialFinalAFormAnswerCellApproved":False,
    "humanSecondReviewerApproved":False,
    "readyForV44":False,"scoringApproved":False,
    "status":"NATIVE_FIVE_OPTION_DRAFT_SOURCE_REVIEW_HOLD"})
 must(len(result)==len(set(q["id"] for q in result))==14,"14_NATIVE_DRAFTS")
 data={"schema":"NOMUSA_FIRST_V69_2017_2019_14_SECONDARY_NATIVE_STEM_FIVE_OPTIONS/1",
    "asOfKST":"2026-11-19","target":14,"individualFiveOptionNativeDrafts":14,
    "officialQNetOriginalCertifications":0,"completeVisualOriginalProofreadingApprovals":0,
    "verifiedFinalAnswerCells":0,"historicalLegalEconomicTheoryApprovals":0,
    "newScoringApprovals":0,"newAppImports":0,"riskCounts":dict(sorted(flags.items())),
    "status":"PASS_14_NATIVE_STEM_FIVE_OPTION_DRAFTS_GLYPH_AND_FOOTER_QA_HOLD_SCORING",
    "warning":"Native PDF candidate text may omit graphs/formulas or contain private-use symbols; source is a third-party mirror not independently authenticated Q-Net original.",
    "rows":result}
 OUT.mkdir(parents=True,exist_ok=True)
 (OUT/"NOMUSA_FIRST_V69_14_FIVE_OPTIONS_CANDIDATES.json").write_text(
     json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 with (OUT/"NOMUSA_FIRST_V69_14_QUESTION_OPTION_REVIEW.csv").open("w",encoding="utf-8-sig",newline="") as f:
  w=csv.writer(f);w.writerow(["id","year","subject","number","page","stem","choice1","choice2","choice3","choice4","choice5","sourceRisk","scoring"])
  for q in result:w.writerow([q["id"],q["year"],q["subject"],q["questionNumber"],q["sourcePdfPageCandidate"],
       q["questionStemNativeCandidate"],*[c["rawNativeTextCandidate"] for c in q["fiveOptionNativeCandidates"]],
       "|".join(q["sourceContentRisks"]),"HOLD"])
 compact={k:v for k,v in data.items() if k!="rows"}
 compact["sourceDraftArtifact"]="review-artifacts/NOMUSA_FIRST_V69/NOMUSA_FIRST_V69_14_FIVE_OPTIONS_CANDIDATES.json"
 SUMMARY.write_text(json.dumps(compact,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 print(json.dumps(compact,ensure_ascii=False))
if __name__=="__main__":main()

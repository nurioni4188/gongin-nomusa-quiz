#!/usr/bin/env python3
"""V60: stage 2013 150 native-text five-option CANDIDATES for content proofread.

Based only on SHA-locked external 2013 80-page academy mirror, NOT the
independently verified original Q-Net document. Five Unicode circled markers
and candidate text do not establish actual complete/full questions, exam-date
statute/precedent correctness, or the final A-form official answer.
No scoring, no app source writes.
"""
import csv,hashlib,json,re
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"review-artifacts/NOMUSA_FIRST_V58/NOMUSA_FIRST_V58_2013_150_NATIVE_TEXT_SOURCE_REVIEW.json"
OUT=ROOT/"review-artifacts/NOMUSA_FIRST_V60"
OUT.mkdir(parents=True,exist_ok=True)
SUMMARY=ROOT/"review/NOMUSA_FIRST_V60_2013_150_STEM_FIVE_OPTION_CANDIDATE_SUMMARY_20261118.json"
MARKS="①②③④⑤"
def load(p):return json.loads(p.read_text(encoding="utf8"))
def require(v,s):
 if not v:raise AssertionError("HOLD_V60_"+s)
def split_stem_and_five(text):
 chunks=re.split(r"([①②③④⑤])",text)
 found=[m for m in chunks if m in MARKS]
 if found!=list(MARKS):return None,None,"FIVE_OPTION_MARKER_SEQUENCE_NOT_EXACT"
 if len(chunks)!=11:return None,None,"INCONSISTENT_MARKER_FRAGMENT_COUNT"
 stem=chunks[0].strip()
 options=[{"number":i+1,"marker":chunks[i*2+1],
           "unverifiedOriginalChoiceCandidate":chunks[i*2+2].strip(),
           "independentSourceVerified":False,
           "optionReasonIndependentlyVerified":False} for i in range(5)]
 if not stem or len(stem)<15:return None,None,"STEM_TOO_SHORT_FOR_SOURCE_DRAFT"
 if any(len(x["unverifiedOriginalChoiceCandidate"])<1 for x in options):
  return stem,options,"ONE_OR_MORE_EMPTY_OPTION_CANDIDATE"
 return stem,options,"NATIVE_FIVE_MARKER_CANDIDATES_FOR_MANUAL_PROOFREAD"

def main():
 src=load(SRC)
 require(src["targetQuestionIDs"]==150 and len(src["rows"])==150,"V58_EXACT_150")
 require(src["officialQNetSourceEqualityApproved"]==0 and src["newScoringApprovals"]==0,"UNEXPECTED_APPROVALS")
 results=[];states=Counter();perYear=Counter()
 for r in src["rows"]:
  text=r["untrustedNativePDFTextCandidate"]
  stem,options,state=split_stem_and_five(text)
  if r["status"]!="NATIVE_PDF_TEXT_AND_IMAGE_CANDIDATE_UNVERIFIED":
   stem,options,state=None,None,"QUESTION_NUMBER_OR_CROP_BOUNDARY_AMBIGUOUS_HOLD"
  risk=[]
  if not options:risk.append("NATIVE_PDF_FIVE_CHOICE_EXTRACTION_INCOMPLETE")
  if len(text)<70:risk.append("SHORT_NATIVE_TEXT_OR_MISSING_SHARED_STEM")
  if re.search(r"[=±÷∑∫^√%]|그래프|표\s*[0-9①②③⑤]",text):
   risk.append("FORMULA_GRAPH_OR_TABLE_VISUAL_REVIEW_REQUIRED")
  if r["subject"] in ("노동법1","노동법2","사회보험법","민법"):
   risk.append("2013_06_08_EXAM_DATE_STATUTES_AND_PRECEDENTS_UNVERIFIED")
  else:risk.append("ACADEMIC_THEORY_OR_CALCULATIONS_UNVERIFIED")
  risk.append("THIRD_PARTY_2013_MIRROR_NOT_CONFIRMED_QNET_ORIGINAL")
  states[state]+=1
  results.append({
   "id":r["id"],"year":2013,"subject":r["subject"],"number":r["number"],
   "sourceMirrorSHA256":r["thirdPartyMirrorPDFSHA256"],
   "sourceBookletFooter":r["sourceBookletFooter"],
   "candidateOriginalPDFPages":[p["pdfPage"] for p in r["matchingNumberLocations"]],
   "candidateImageParts":r["provisionalImageParts"],
   "unverifiedSourceStemCandidate":stem,
   "unverifiedFiveOptionCandidates":options,
   "legacyAnswerCandidateUnapproved":r["historicAFormAnswerCandidateUnapproved"],
   "stage":state,"riskFlags":risk,
   "officialQNetSourceContentIdentityApproved":False,
   "allOriginalStemChoicesIndependentlyProofread":False,
   "examDateLegalTheoryReasonsIndependentlyApproved":False,
   "officialFinalAFormAnswerCellVerified":False,
   "independentReviewerApproval":False,
   "readyForV44":False,"scoringApproved":False
  })
 require(len(results)==150 and len({x["id"] for x in results})==150,"RESULTS_EXACT_150")
 result={"schema":"NOMUSA_FIRST_V60_2013_UNAPPROVED_STEM_FIVE_OPTIONS/1",
  "asOfKST":"2026-11-18",
  "thirdPartyMirrorPDFSHA256":src["mirrorPDFSHA256"],
  "targetQuestionIDs":150,
  "fiveMarkerOptionCandidateRecords":states["NATIVE_FIVE_MARKER_CANDIDATES_FOR_MANUAL_PROOFREAD"],
  "questionStemChoiceCandidacyIncomplete":150-states["NATIVE_FIVE_MARKER_CANDIDATES_FOR_MANUAL_PROOFREAD"],
  "stageCounts":dict(sorted(states.items())),
  "officialQNetMirrorEqualityApproved":0,"independentFiveOptionProofread":0,
  "examDateLawOrTheoryApproved":0,"individualOfficialAnswerCellsApproved":0,
  "newQdataImports":0,"newScoringApproved":0,
  "status":"PASS_EXTERNAL_2013_NATIVE_FIVE_OPTION_CANDIDATE_SPLIT_HOLD_ORIGINAL_AND_SCORING",
  "warning":"An exact marker pattern is not proof of a complete native original A-form question: entire mirror and all five options still require Q-Net comparison and human review.",
  "rows":results}
 (OUT/"NOMUSA_FIRST_V60_2013_150_STEM_AND_OPTIONS_CANDIDATE_REVIEW.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 with (OUT/"NOMUSA_FIRST_V60_2013_150_NATIVE_OPTION_QA.csv").open("w",encoding="utf-8-sig",newline="") as f:
  w=csv.writer(f);w.writerow(["id","subject","number","pages","stage","fiveOptionCandidates","officialQnetMirrorApproved","scoring"])
  for q in results:w.writerow([q["id"],q["subject"],q["number"],"|".join(map(str,q["candidateOriginalPDFPages"])),
   q["stage"],len(q["unverifiedFiveOptionCandidates"] or []),"HOLD","HOLD"])
 summary={k:v for k,v in result.items() if k!="rows"}
 summary["all150DraftsArtifact"]="review-artifacts/NOMUSA_FIRST_V60/NOMUSA_FIRST_V60_2013_150_STEM_AND_OPTIONS_CANDIDATE_REVIEW.json"
 SUMMARY.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 print(json.dumps(summary,ensure_ascii=False))
if __name__=="__main__":main()

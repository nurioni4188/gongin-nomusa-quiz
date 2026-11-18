#!/usr/bin/env python3
"""V74 full 686 record *provenance and proofreading workspace*; final two
2011/2012 original-source draft five options are now found, 191/254/241.

Only adds source-lead / unreviewed candidates to existing SHA-tested V71
workspace. Even the 2011 worked academic example is a THEORY DRAFT, not
independent Q-Net original matching or an approved final answer cell.
The 2012 trade tariff figure remains missing and cannot be graded. No merges.
"""
from __future__ import annotations
import csv,hashlib,json,re,shutil
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/"review-artifacts"
BASE=ART/"V74_V71_BUNDLE"
SOURCE=ART/"V74_V73_BUNDLE/NOMUSA_FIRST_V73_LAST_2_NATIVE_STEM_FIVE_OPTION_DRAFTS.json"
OUT=ART/"NOMUSA_FIRST_V74"
SUMMARY=ROOT/"review/NOMUSA_FIRST_V74_686_COMPLETE_SOURCE_LEADS_REVIEW_SUMMARY_20261119.json"
def require(c,s):
 if not c:raise AssertionError("HOLD_V74_"+s)
def read(p):return json.loads(p.read_text(encoding="utf8"))
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 old=read(BASE/"NOMUSA_FIRST_V71_686_UNAPPROVED_SOURCE_REVIEW.json")
 add=read(SOURCE)
 require(old["targetCount"]==len(old["rows"])==686,"V71_686")
 require(old["reviewStageCounts"]=={
   "unapproved_full_stem_and_five_options":189,
   "unapproved_OCR_transcript":254,
   "original_source_only_need_full_transcription":243},"V71_EXPECTED_SPLIT")
 require(add["reprintTextFiveOptionCandidates"]==len(add["rows"])==2,"V73_TWO")
 require(add["independentlyConfirmedFinalAnswerCells"]==0,"NO_OFFICIAL_KEY_APPROVAL")
 require({x["id"] for x in add["rows"]}=={
  "legacy1-2011-A-economics-014","legacy1-2012-A-economics-119"},"EXACT_MISSING_IDS")
 rows=old["rows"]
 byID={r["id"]:r for r in rows}
 theory={
  "legacy1-2011-A-economics-014":{
   "status":"INDEPENDENT_ALGEBRA_DRAFT_NOT_OFFICIAL_KEY_APPROVAL",
   "formula":"Y=2X; M=P_X X+P_Y Y=(P_X+2P_Y)X; dM/dX=P_X+2P_Y.",
   "provisionalTheoreticalChoiceNumber":4,
   "fiveChoiceDraftReasons":[
    "① 2P_X는 Y재에 드는 지출항을 반영하지 않습니다.",
    "② 3P_Y는 X재 단위당 지출 P_X를 누락합니다.",
    "③ 2P_X+P_Y는 주어진 소비비율 1:2에서 가격계수를 뒤바꾼 값입니다.",
    "④ P_X+2P_Y는 X재 1단위와 Y재 2단위 구매에 필요한 소득증가분입니다.",
    "⑤ P_X/(2P_Y)는 소득 변화/수량 변화의 차원과 일치하지 않습니다."],
   "historicalOfficialQuestionAndFinalAnswerApproval":False,
   "independentHumanSecondReview":False},
  "legacy1-2012-A-economics-119":{
   "status":"GRAPH_DEPENDENT_TARIFF_CONCEPT_DRAFT_ONLY_DO_NOT_CHOOSE_FINAL_KEY",
   "concept":"수입관세는 무관세 자유무역에 비해 국내소비자가격을 올리고, 소비량을 줄이며 국내 공급량을 늘립니다. 관세수입과 후생순손실 영역은 실제 그래프의 점·면적 표기를 확인해야 합니다.",
   "provisionalTheoreticalChoiceNumber":None,
   "missingSourceAssets":["2012 QNet A 경제학 전체문항 119번과 외부 복원 경제학 19번의 연결 승인",
     "그래프의 점 E,F,G,K,C와 가격 P1,P2,PE 영역 시각대조"],
   "historicalOfficialQuestionAndFinalAnswerApproval":False,
   "independentHumanSecondReview":False}
 }
 for x in add["rows"]:
  q=byID[x["id"]]
  require(q["reviewStage"]=="original_source_only_need_full_transcription","TARGET_WAS_SOURCE_ONLY_"+q["id"])
  require(q["legacyAnswerCandidateNotApproved"]==x["priorLegacyAnswerCandidateUnapproved"],
    "LEGACY_KEY_NOT_CHANGED_"+q["id"])
  require(len(x["unverifiedFiveOptions"])==5 and all(x["unverifiedFiveOptions"]), "FIVE_CHOICES_"+q["id"])
  require(not x["originalQNetAFormSourceIndependentlyVerified"] and not x["scoringApproved"],"EXTERNAL_UNAPPROVED")
  q["provisionalQuestionText"]=x["unverifiedStemCandidate"]
  q["fiveOptionTextCandidates"]=x["unverifiedFiveOptions"]
  q["originalSourceGrade"]="THIRD_PARTY_CBT_REPRINT_NOT_OFFICIAL_QNET"
  q["originalSourceURL"]=x["thirdPartyHtmlSourceURL"]
  q["originalSourcePdfSHA256"]=None
  q["externalHtmlSourceSHA256"]=x["thirdPartyHtmlSourceSHA256"]
  q["externalNumberingAssumption"]=x["publishedEconomicsSectionQuestionNumber"]
  q["reviewStage"]="unapproved_full_stem_and_five_options"
  q["riskFlags"]=sorted(set(q["riskFlags"]+x["riskFlags"]))
  q["draftLearningNote"]=theory[x["id"]]
  require(not q["scoringApproved"] and not q["readyForV44"],"NO_SCORING_"+q["id"])
 stage=Counter(q["reviewStage"] for q in rows)
 require(dict(stage)=={"unapproved_full_stem_and_five_options":191,
  "unapproved_OCR_transcript":254,
  "original_source_only_need_full_transcription":241},"V74_SPLIT_"+str(stage))
 require(len({q["id"] for q in rows})==686,"ALL_DISTINCT")
 require(all(not q["scoringApproved"] and not q["readyForV44"] for q in rows),"NO_APPROVALS")
 OUT.mkdir(parents=True,exist_ok=True)
 # Full source JPEGs are inherited byte-identically from reviewed V71 run.
 oldimgs=BASE/"source-images"
 require(oldimgs.is_dir(),"BASE_448_IMAGES_MISSING")
 dest=OUT/"source-images"
 if dest.exists():shutil.rmtree(dest)
 shutil.copytree(oldimgs,dest)
 validated=0
 for q in rows:
  for pic in q["reviewerOriginalImageCandidates"]:
   p=OUT/pic["path"]
   require(p.is_file() and sha(p.read_bytes())==pic["sha256"],"SRC_IMAGE_DRIFT_"+q["id"])
   validated+=1
 require(validated==old["originalImageEvidenceFilesSHAValidated"]==448,"IMAGE_SHA_448")
 j={**old,
   "schema":"NOMUSA_FIRST_V74_ALL_686_SOURCE_LEADS_REVIEW_ONLY/1",
   "asOfKST":"2026-11-19",
   "reviewStageCounts":dict(sorted(stage.items())),
   "thirdPartyNativeFullFiveChoiceSourcesWithoutIndependentApproval":191,
   "secondaryOriginalSourceLeadMissingIDs":0,
   "additionalHistoricalOfficialQNetOriginalApproved":0,
   "unapprovedDraftTheoreticalExplanationCount":2,
   "newScoredQuestionsImported":0,
   "independentlyVerifiedOfficialFullQuestionAnswers":0,
   "independentLawTheoryExplanationApprovals":0,
   "status":"PASS_686_ALL_SOURCE_LEADS_191_FIVE_CHOICE_DRAFTS_254_OCR_241_SOURCE_ONLY_HOLD_SCORING",
   "warning":"All 686 IDs have at least public secondary source leads; 191 unreviewed stem/options does NOT mean official QNet final answers verified; 241 remain without complete source text; official/expert approval zero.",
   "rows":rows}
 (OUT/"NOMUSA_FIRST_V74_686_ALL_SOURCE_LEADS_UNAPPROVED.json").write_text(
  json.dumps(j,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 with (OUT/"NOMUSA_FIRST_V74_686_REVIEW_QUEUE.csv").open("w",encoding="utf-8-sig",newline="") as f:
  w=csv.writer(f);w.writerow(["id","year","subject","number","reviewStage","sourceURL",
   "sourceFileSHAorExternalHtmlSHA","stemDraft","optionsCount","candidateAnswerUnapproved",
   "independentFiveOptionApproval","officialKeyApproval","grading"])
  for q in rows:w.writerow([q["id"],q["year"],q["subject"],q["questionNumber"],
   q["reviewStage"],q["originalSourceURL"],q["originalSourcePdfSHA256"] or q.get("externalHtmlSourceSHA256"),
   q["provisionalQuestionText"],len(q["fiveOptionTextCandidates"] or []),
   "|".join(map(str,q["legacyAnswerCandidateNotApproved"])),"HOLD","HOLD","HOLD"])
 # Keep the actual validated V71 review interface and replace only its
 # JSON payload and static stage labels. Preserve memo localStorage keys.
 html=(BASE/"index.html").read_text(encoding="utf8")
 payload=json.dumps(rows,ensure_ascii=False,separators=(",",":")).replace("</script","<\\/script")
 pat=r'(<script type="application/json" id="question-data">).*?(</script>)'
 html,n=re.subn(pat,lambda m:m.group(1)+payload+m.group(2),html,count=1,flags=re.S)
 require(n==1,"HTML_EMBEDDED_JSON_NOT_REPLACED")
 html=html.replace("검토대장 V71","검토대장 V74").replace("원문검토 V71","원문검토 V74")
 html=html.replace("후보 189개","후보 191개").replace("미완료 243개","미완료 241개")
 html=html.replace("5선지 후보 189개","5선지 후보 191개")
 html=html.replace("원문 전사 미완료 243개","원문 전사 미완료 241개")
 needle="""+(opts||'<p>5개 보기가 아직 구조화되지 않았습니다.</p>')+pics+"""
 injection="""+(opts||'<p>5개 보기가 아직 구조화되지 않았습니다.</p>')+
(q.draftLearningNote?'<details><summary>경제학 풀이 초안 (공식 정답 승인 전)</summary>'+
'<div class="text">'+e(q.draftLearningNote.formula||q.draftLearningNote.concept||'')+'</div>'+
(q.draftLearningNote.fiveChoiceDraftReasons||[]).map(e).join('<p></p>')+
'<p><strong>학습용 초안일 뿐, 공식 A형 정답표·원문·그래프 전문가 승인 전입니다.</strong></p></details>':'')+pics+"""
 require(needle in html,"UI_STUDY_DRAFT_SLOT_MISSING")
 html=html.replace(needle,injection,1)
 (OUT/"index.html").write_text(html,encoding="utf8")
 readme=(BASE/"README_KO.md").read_text(encoding="utf8")
 readme+="\nV74 보강: 2011 14번/2012 전체 119번에 외부 기출 복원자료의 지문·5선지를 연결했습니다. 2012 119↔경제학19 매핑 및 관세 그래프는 공식 원본 대조 HOLD입니다. 686 원본 자료 출처의 존재는 확인했지만 공식 정답·문항 내용승인은 아직 0입니다.\n"
 (OUT/"README_KO.md").write_text(readme,encoding="utf8")
 sm={"schema":"NOMUSA_FIRST_V74_686_ALL_SOURCE_LEADS_SUMMARY/1",
  "asOfKST":"2026-11-19","targetQuestionIDs":686,
  "unreviewedFullFiveOptionDrafts":191,"unreviewedOfficialImageOCRDrafts":254,
  "sourceOnlyNeedFullOriginalText":241,
  "publicSourceLeadForEachID":686,
  "originalJPEGsSHA256Verified":448,
  "experimentalEconomicTheoryDrafts":2,
  "officialQNetFullOriginalQuestionAndFiveChoicesApproved":0,
  "independentlyVerifiedOfficialFinalAnswerCells":0,
  "independentlyVerifiedFiveChoiceExplanationsWithExamDateLaw":0,
  "newScoringApprovals":0,"newQDATAImports":0,
  "status":"PASS_FULL_686_REVIEW_SOURCE_COVERAGE_ONLY_FINAL_CONTENT_AND_GRADING_HOLD",
  "warning":"This is not 686 officially proofread model answers. 241 items lack full transcription, and official answer cells, 5-option explanations, exam-date legal evidence & independent reviewer approvals all remain 0."
 }
 SUMMARY.write_text(json.dumps(sm,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 print(json.dumps(sm,ensure_ascii=False))
if __name__=="__main__":main()

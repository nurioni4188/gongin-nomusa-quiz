#!/usr/bin/env python3
"""V71: reproducible 686 A-form ORIGINAL + 5-option review workspace.

Combine exact previous artifact bytes, 686 unique historic IDs, and complete
provenance—not a scored examination bank. Never treat OCR, reprinted A-form
text, preliminary answers, or source-page imagery as independent original
Q-Net/final answer/legal reasoning approval. Main/production remain frozen.
"""
from pathlib import Path
from collections import Counter
import hashlib,csv,json,re,shutil
ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/"review-artifacts"
OUT=ART/"NOMUSA_FIRST_V71"
SUMMARY=ROOT/"review/NOMUSA_FIRST_V71_686_WORKSPACE_SUMMARY_20261119.json"
V50=ART/"V71_V50_BUNDLE/NOMUSA_FIRST_V50/NOMUSA_FIRST_V50_686_ENRICHED_SOURCE_QUEUE.json"
V58=ART/"V71_V58_BUNDLE/NOMUSA_FIRST_V58_2013_150_NATIVE_TEXT_SOURCE_REVIEW.json"
V69=ART/"V71_V69_BUNDLE/NOMUSA_FIRST_V69/NOMUSA_FIRST_V69_14_FIVE_OPTIONS_CANDIDATES.json"
V70=ART/"V71_V70_BUNDLE/NOMUSA_FIRST_V70_27_SOURCE_AND_TEXT_REVIEW.json"
V52=ART/"V71_V50_BUNDLE/NOMUSA_FIRST_V52/NOMUSA_FIRST_V52_163_OCR_SOURCE_RISK_REVIEW.json"
V56=ART/"V71_V56_BUNDLE/NOMUSA_FIRST_V56/NOMUSA_FIRST_V56_91_UNAPPROVED_OCR_TEXT_AND_RISK.json"
V65=ART/"V71_V50_BUNDLE/NOMUSA_FIRST_V65/NOMUSA_FIRST_V65_254_FULLPAGE_SOURCE_RISK_QUEUE.json"
def load(p):return json.loads(p.read_text(encoding="utf8"))
def sha(b):return hashlib.sha256(b).hexdigest()
def insist(c,msg):
 if not c:raise AssertionError("HOLD_V71_"+msg)
def split(t):
 parts=re.split("([①②③④⑤])",t or "")
 if len(parts)==11 and [x for x in parts if x in "①②③④⑤"]==list("①②③④⑤"):
  opts=[parts[2*i+2].strip() for i in range(5)]
  if all(opts) and parts[0].strip():return parts[0].strip(),opts
 return None,None
def copy_sha(src,dest,known):
 insist(src.is_file(),"MISSING_ORIGINAL_IMAGE_"+src.name)
 bb=src.read_bytes()
 insist(sha(bb)==known,"IMAGE_SOURCE_HASH_"+src.name)
 dest.parent.mkdir(parents=True,exist_ok=True)
 dest.write_bytes(bb)
 return str(dest.relative_to(OUT))

def main():
 base,v58,v69,v70,v52,v56,v65=map(load,[V50,V58,V69,V70,V52,V56,V65])
 insist(len(base["rows"])==686 and base["original686Preserved"]==686,"BASE_686")
 insist(len(v58["rows"])==150 and v58["nativeQuestionHeadingsWithProvisionalText"]==150,"2013_FULL_150")
 insist(len(v69["rows"])==14 and v69["individualFiveOptionNativeDrafts"]==14,"2017_2019_14")
 insist(len(v70["rows"])==27 and v70["thirdParty2010FiveOptionCandidates"]==25,"2010_25")
 insist(len(v52["rows"])==163 and len(v56["rows"])==91 and len(v65["rows"])==254,"OCR_AND_OFFICIAL_254")
 old={x["id"]:x for x in v58["rows"]};recent={x["id"]:x for x in v69["rows"]}
 last={x["id"]:x for x in v70["rows"]}
 o52={x["id"]:x for x in v52["rows"]};o56={x["id"]:x for x in v56["rows"]}
 original={x["id"]:x for x in v65["rows"]}
 insist(len(old)==150 and len(recent)==14 and len(last)==27 and len(original)==254,"ALL_UNIQUE")
 OUT.mkdir(parents=True,exist_ok=True)
 data=[];stages=Counter();images=0
 for q in base["rows"]:
  id=q["id"];year=q["year"];stem=None;choices=None;ocr=None
  sourceSHA=q.get("sourceDocumentSHA256");page=None;risks=[];imgs=[]
  url=q.get("sourceNoticeOrPdfUrl")
  v50=q.get("v50NewDocument") or {}
  if year in (2016,2018):
   url=v50.get("officialQNetSourceURL") or url
   sourceSHA=v50.get("pdfSha256") or sourceSHA
  grade=("official_QNet_A_booklet_SHA" if year in (2016,2018,2020,2021) else
         "thirdparty_reprint_not_independent_official")
  if id in old:
   x=old[id];stem,choices=split(x["untrustedNativePDFTextCandidate"])
   insist(stem is not None and len(choices)==5,"2013_TEXT_5_OPTIONS_"+id)
   sourceSHA=x["thirdPartyMirrorPDFSHA256"];url=x["thirdPartyMirrorUrl"]
   page=x["matchingNumberLocations"][0]["pdfPage"]
   for file in x.get("provisionalImageParts") or []:
    a=ART/"V71_V58_BUNDLE"/file["path"]
    dest=OUT/"source-images/2013-crops"/Path(file["path"]).name
    imgs.append({"type":"thirdparty_unapproved_original_crop",
        "path":copy_sha(a,dest,file["sha256"]),"sha256":file["sha256"]});images+=1
   risks.append("2013년 외부 재게시 원본 — 공식 Q-Net 동일성 미승인")
  if id in recent:
   x=recent[id];stem=x["questionStemNativeCandidate"]
   choices=[o["rawNativeTextCandidate"] for o in x["fiveOptionNativeCandidates"]]
   sourceSHA=x["sourcePdfSHA256"];page=x["sourcePdfPageCandidate"]
   risks+=x["sourceContentRisks"]
  if id in last:
   x=last[id];stem=x["thirdPartyUnverifiedStem"];choices=x["thirdPartyUnverifiedOptions"]
   sourceSHA=x.get("sourceSHA256");url=x["publicSource"]
   risks.append("2010~12 재게시본 원문·공식 최종정답 미검증")
  if id in o52:
   x=o52[id];ocr=x["untrustedOCRTextCandidate"];risks+=x["qaFlags"]
  if id in o56:
   x=o56[id];ocr=x["ocrTextUnreviewedDraft"];risks+=x["flags"]
  if id in original:
   x=original[id];page=x["originalSourcePdfPage"]
   sourceSHA=x["originalSourcePdfSHA256"]
   risks+=x["reviewRiskFlags"]
   img=x["originalFullPageReviewImage"]
   src=ART/"V71_V50_BUNDLE/NOMUSA_FIRST_V65"/img["file"]
   dest=OUT/"source-images/QNet-original-pages"/(id+".jpg")
   imgs.append({"type":"official_QNet_original_page_with_provisional_crop_rectangle",
       "path":copy_sha(src,dest,img["sha256"]),"sha256":img["sha256"]});images+=1
  if stem and choices and len(choices)==5:
   stage="unapproved_full_stem_and_five_options"
  elif ocr:stage="unapproved_OCR_transcript"
  else:stage="original_source_only_need_full_transcription"
  stages[stage]+=1
  data.append({"id":id,"year":year,"subject":q["subject"],"form":"A",
   "questionNumber":q["questionNumber"],
   "provisionalQuestionText":stem,"fiveOptionTextCandidates":choices,
   "unreviewedOCR":ocr,"legacyAnswerCandidateNotApproved":q["legacyAnswerCandidate"],
   "originalSourceGrade":grade,"originalSourceURL":url,
   "originalSourcePdfSHA256":sourceSHA,"originalPdfPageCandidate":page,
   "reviewerOriginalImageCandidates":imgs,"riskFlags":sorted(set(risks)),
   "reviewStage":stage,"officialQNetQuestionAndAllFiveOptionsIndependentlyProofread":False,
   "officialFinalAAnswerCellVerified":False,
   "historicalLawOrAcademicExplanationIndependentlyVerified":False,
   "independentHumanReviewerSignoff":False,"readyForV44":False,
   "scoringApproved":False})
 insist(len(data)==len({x["id"] for x in data})==686,"686_DISTINCT")
 insist(dict(stages)=={"unapproved_full_stem_and_five_options":189,
          "unapproved_OCR_transcript":254,
          "original_source_only_need_full_transcription":243},"189_254_243")
 insist(images>=448,"448_SOURCE_IMAGES")
 insist(all(not x["scoringApproved"] and not x["readyForV44"] for x in data),"NO_SCORING")
 packet={"schema":"NOMUSA_FIRST_V71_686_SOURCE_REVIEW_ONLY/1","asOfKST":"2026-11-19",
  "targetCount":686,"reviewStageCounts":dict(sorted(stages.items())),
  "originalImageEvidenceFilesSHAValidated":images,
  "independentlyVerifiedOfficialFullQuestionAnswers":0,
  "independentLawTheoryExplanationApprovals":0,
  "newScoredQuestionsImported":0,
  "status":"PASS_686_SOURCE_REVIEW_WORKSPACE_HOLD_LEARNING_ANSWERS_AND_DEPLOYMENT",
  "warning":"No item is independently certified; preexisting answer candidates and unreviewed external reconstructions MUST NOT be used for scoring.",
  "rows":data}
 (OUT/"NOMUSA_FIRST_V71_686_UNAPPROVED_SOURCE_REVIEW.json").write_text(
  json.dumps(packet,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 with (OUT/"NOMUSA_FIRST_V71_686_SOURCE_REVIEW.csv").open("w",encoding="utf-8-sig",newline="") as f:
  w=csv.writer(f);w.writerow(["id","year","subject","questionNumber","sourceGrade","reviewStage","originalPDFPage",
   "stemUnreviewed","fiveOptionsDraft","legacyAnswerNotApproved","finalAnswerProof","explanationApproval","scoring"])
  for q in data:w.writerow([q["id"],q["year"],q["subject"],q["questionNumber"],q["originalSourceGrade"],
    q["reviewStage"],q["originalPdfPageCandidate"],q["provisionalQuestionText"],
    len(q["fiveOptionTextCandidates"] or []),"|".join(map(str,q["legacyAnswerCandidateNotApproved"])),
    "HOLD","HOLD","HOLD"])
 payload=json.dumps(data,ensure_ascii=False,separators=(",",":")).replace("</script","<\\/script")
 html='''<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>공인노무사 1차 686문항 원문검토 V71</title><style>
*{box-sizing:border-box}body{font-family:system-ui,sans-serif;margin:0;background:#f4f7fb;color:#192943}
header{background:#17304e;color:white;padding:18px}header h1{font-size:1.25rem;margin:0 0 8px}main{max-width:1000px;padding:14px;margin:auto}
.warn{padding:13px 16px;background:#fff;border:1px solid #d9e0ea;border-radius:10px;line-height:1.7}
.controls{display:flex;gap:8px;flex-wrap:wrap;margin:14px 0}select,input,button,textarea{font:inherit;padding:9px;border:1px solid #bdcbd7;border-radius:7px;background:white}
.controls>*{flex:1;min-width:115px}#list{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:7px}
.item{text-align:left;padding:12px;border-radius:9px}article{margin-top:14px;background:white;border:1px solid #d9e0ea;border-radius:10px;padding:18px;overflow-wrap:anywhere}
h2{font-size:1.17rem}.text{white-space:pre-wrap;background:#f8fbff;padding:12px;border-left:3px solid #6194c7;line-height:1.6}
.option{padding:9px;border-bottom:1px solid #edf0f4;line-height:1.5}img{display:block;max-width:100%;border:1px solid #ccd5df;margin:10px 0}
small{color:#657487}textarea{width:100%;min-height:100px}details{margin:12px 0}a{color:#1760ac}
</style></head><body><header><h1>686문항 원문·정답 교열대장 V71</h1><div>원문/정답/해설 독립 승인 0 · 기존 채점/Production/Preview 불변</div></header>
<main><p class="warn"><strong>686개 문항을 빠짐없이 조회하는 검토용 초안입니다.</strong> 지문·5선지 후보 189개, OCR 후보 254개, 원문 전사 미완료 243개입니다. 답안으로 승인되지 않았으며 자동 채점되지 않습니다.</p>
<div class="controls"><select id="year"><option value="">전체 연도</option></select><select id="subject"><option value="">전체 과목</option></select>
<select id="stage"><option value="">전체 단계</option><option value="unapproved_full_stem_and_five_options">5선지 초안</option><option value="unapproved_OCR_transcript">OCR 후보</option><option value="original_source_only_need_full_transcription">원본 링크</option></select>
<input id="search" placeholder="문항 ID·지문 검색"></div><p id="count"></p><div id="list"></div><article id="detail">문항을 선택하세요.</article></main>
<script type="application/json" id="question-data">__PAYLOAD__</script>
<script>
const list=JSON.parse(document.getElementById("question-data").textContent);
const e=s=>String(s??"").replace(/[&<>\"']/g,x=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[x]));
const years=[...new Set(list.map(x=>x.year))].sort(),subjects=[...new Set(list.map(x=>x.subject))].sort();
for(const y of years)document.getElementById("year").add(new Option(y+"년",y));
for(const s of subjects)document.getElementById("subject").add(new Option(s,s));
let selected=null;function show(id){const q=list.find(x=>x.id===id);if(!q)return;selected=id;
const opts=(q.fiveOptionTextCandidates||[]).map((v,i)=>'<div class="option">'+('①②③④⑤'[i])+' '+e(v)+'</div>').join("");
const pics=(q.reviewerOriginalImageCandidates||[]).map(x=>'<details><summary>원본 페이지·문항 이미지 보기</summary><img loading="lazy" src="'+encodeURI(x.path)+'"></details>').join("");
const notesKey="nomusa.v71.reviewNote."+q.id;
document.getElementById("detail").innerHTML='<h2>'+e(q.year+'년 '+q.subject+' '+q.questionNumber+'번')+'</h2><small>'+e(q.id)+'</small>'+
'<p><b>단계:</b> '+e(q.reviewStage)+' · <b>개별 내용승인:</b> HOLD</p>'+
'<div class="text">'+e(q.provisionalQuestionText||q.unreviewedOCR||"지문 미확정. 원본 PDF 대조 필요")+'</div>'+
(opts||'<p>5개 보기가 아직 구조화되지 않았습니다.</p>')+pics+
'<details><summary>원본·정답 후보(미승인)·검토위험</summary><p>정답 후보(미승인): '+e((q.legacyAnswerCandidateNotApproved||[]).join(","))+'</p>'+
(q.originalSourceURL?'<a href="'+e(q.originalSourceURL)+'" target="_blank" rel="noopener">원본 출처 열기</a>':'')+
'<p>SHA-256: '+e(q.originalSourcePdfSHA256||"미확보")+'</p><p>'+q.riskFlags.map(e).join(" / ")+'</p></details>'+
'<p><b>개인 교열 메모 (로컬 저장·최종승인 아님)</b></p><textarea id="memo"></textarea><p><button id="save">메모 저장</button></p>';
document.getElementById("memo").value=localStorage.getItem(notesKey)||"";
document.getElementById("save").onclick=()=>{localStorage.setItem(notesKey,document.getElementById("memo").value);alert("로컬 저장 완료, 답안 승인 아님");};}
function search(){const y=document.getElementById("year").value,s=document.getElementById("subject").value,
stage=document.getElementById("stage").value,q=document.getElementById("search").value.toLowerCase().trim();
const matches=list.filter(x=>(!y||String(x.year)===y)&&(!s||x.subject===s)&&(!stage||x.reviewStage===stage)&&(!q||(x.id+" "+(x.provisionalQuestionText||"")).toLowerCase().includes(q)));
document.getElementById("count").textContent="조건 "+matches.length+" / 전체 686 문항";
const x=matches.slice(0,40);
document.getElementById("list").innerHTML=x.map(z=>'<button class="item" data-id="'+e(z.id)+'">'+e(z.year+' '+z.subject+' '+z.questionNumber+'번')+'<br><small>'+e(z.reviewStage)+'</small></button>').join("");
document.querySelectorAll(".item").forEach(b=>b.onclick=()=>show(b.dataset.id));if(x.length)show(x[0].id);else document.getElementById("detail").textContent="조건에 맞는 문제 없음";
}
for(const id of ["year","subject","stage","search"])document.getElementById(id).addEventListener("input",search);search();
</script></body></html>'''
 (OUT/"index.html").write_text(html.replace("__PAYLOAD__",payload),encoding="utf8")
 (OUT/"README_KO.md").write_text(
  "# 공인노무사 1차 686문항 검토용 학습 허브 V71\\n\\n686개 ID·원문 후보·출처·정답 후보를 전수 보존합니다. "+
  "원문·공식 정답·법률과 학술근거의 독립 승인 0건, 채점 0건입니다. "+
  "압축을 풀고 index.html을 열어 연도/과목/문항 원본을 대조하십시오. 운영 앱, main과 Production은 변경하지 않습니다.\\n",
  encoding="utf8")
 summary={"schema":"NOMUSA_FIRST_V71_686_REVIEW_ONLY_SOURCE_WORKSPACE_SUMMARY/1",
  "asOfKST":"2026-11-19","totalQuestions":686,
  "fullFiveChoiceUnapprovedDrafts":189,"unreviewedOCR":254,
  "sourceOnlyWithoutStructuredOptions":243,
  "sourceImageFileSHA256Validated":images,
  "independentQuestionTextFiveOptionApprovals":0,
  "officialAnswerCellApprovals":0,"historicalLawTheoryExplanationApprovals":0,
  "newScoringApprovals":0,"newQDATAImports":0,
  "status":"PASS_FULL_686_REVIEW_WORKSPACE_HOLD_COMPLETE_APPROVAL_AND_DEPLOYMENT",
  "warning":"686 complete record coverage is NOT 686 exam-grade complete answers."}
 SUMMARY.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 print(json.dumps(summary,ensure_ascii=False))
if __name__=="__main__":main()

/* NOMUSA V10 — 2024·2026 노동법 12개 소문항 render-only overlay.
 * 원장(rc27_essay_catalog.js)·문항 ID·배점·localStorage 키·원본 PDF 불변.
 * 직전 상세·압축 텍스트는 detailedBeforeV10/compressedBeforeV10으로 런타임 보존.
 * 공식 모범답안·채점·수기분량 승인 아님(모두 HOLD). */
(function(){'use strict';
const prev=window.NOMUSA_CANONICAL_SELECTION_V1;
const v9=window.NOMUSA_V9_QUALITY_GATE;
const cases=window.NOMUSA_V10_MANUSCRIPTS||{};
const questions=window.N27_CATALOG?.items||[];
const expected=['2024-노동법1|1|1','2024-노동법1|1|2','2024-노동법1|2|0','2024-노동법2|1|1','2024-노동법2|1|2','2024-노동법2|2|0',
 '2026-노동법1|1|1','2026-노동법1|1|2','2026-노동법1|2|0','2026-노동법2|1|1','2026-노동법2|1|2','2026-노동법2|2|0'];
if(!prev?.items||v9?.v9Deepened!==4||questions.length!==377||Object.keys(prev.items).length!==328)
  throw Error('NOMUSA_V10_BASELINE_MISMATCH');
if(Object.keys(cases).length!==expected.length||expected.some(id=>!cases[id])||
   Object.keys(cases).some(id=>!expected.includes(id)))
  throw Error('NOMUSA_V10_CASE_REGISTRY_MISMATCH');
const qmap=new Map(questions.map(q=>[q.id,q]));
const items=Object.assign(Object.create(null),prev.items),rows=[];
const seeds=window.N1071_SEEDS=window.N1071_SEEDS||{};
for(const id of expected){
 const q=qmap.get(id),before=prev.items[id],v=cases[id];
 if(!q?.sourceText||!before?.renderable||!before.detailed||!before.compressed)
  throw Error('NOMUSA_V10_BASE_MISSING_'+id);
 if(q.points!==v.points)throw Error('NOMUSA_V10_SCORE_MISMATCH_'+id);
 // 기존 압축답안은 상세답안에서 제목만 뺀 사실상 동일 분량이었으므로, V10 압축답안은 '더 길게'가 아니라
 // 상세답안보다 짧고 Ⅰ쟁점~Ⅳ결론 4단 구조를 갖춘 독립 문장형인지로 검사한다.
 if(!v.full||!v.compact||v.full.length<before.detailed.length*1.6||v.compact.length<480||
    v.compact.length>=v.full.length*0.5||!/Ⅰ\.[\s\S]*Ⅱ\.[\s\S]*Ⅲ\.[\s\S]*Ⅳ\./.test(v.compact)||!/결론/.test(v.compact))
  throw Error('NOMUSA_V10_NOT_ENHANCED_'+id);
 const next=Object.freeze({...before,detailed:v.full,compressed:v.compact,
   detailedBeforeV10:before.detailed,compressedBeforeV10:before.compressed,
   memorySeedsV10:Object.freeze([...v.seeds]),
   verifiedPrecedentUrlsV10:Object.freeze([...v.evidence]),
   precedentAuditStatusV10:v.status,
   contentStatusV10:'A_LEARNING_DRAFT_COMPLETE',
   evidenceStatusV10:v.evidence.length&&!/번호.{0,12}HOLD|원문대조 미완료/.test(v.status)?'B_PARTIAL_CASE_NUMBER_VERIFIED':'B_HOLD',
   finalAcademicApproval:'HOLD',officialScoreApproval:'HOLD',
   paperPagesVerified:false,scoringApproved:false});
 items[id]=next;
 // 암기 탭 자동 후보(사용자가 저장한 카드가 있으면 그 카드가 우선함: essay-app cardFor 참조)
 if(!seeds[id])seeds[id]=[v.seeds];
 rows.push(Object.freeze({id,year:q.year,subject:q.subject,points:q.points,
   priorDetailedChars:before.detailed.length,revisedDetailedChars:v.full.length,
   priorCompactChars:before.compressed.length,revisedCompactChars:v.compact.length,
   previousVersionPreserved:true,precedentUrls:Object.freeze([...v.evidence]),
   evidenceStatus:next.evidenceStatusV10,manualPageCountVerified:false,finalApproval:'HOLD'}));
}
if(Object.keys(items).length!==328||rows.length!==12)throw Error('NOMUSA_V10_ID_SET_CHANGED');
const gate=Object.freeze({schema:'nomusa-20year-essay-labor-depth/10',
  sourceQuestions:377,representativeCandidates:328,v10Rewritten:12,
  scope:'2024·2026 노동법 전 소문항(12) — 이전 집중심화 57개에 미포함',
  originalCatalogChanged:false,originalPointsChanged:false,originalStorageKeysChanged:false,
  productionMutated:false,previewDeployed:false,handwritingPageTargetReached:false,
  finalContentApprovals:0,reviewStatus:'REVIEW_ONLY_V10_LABOR_2024_2026_CONTENT_HOLD',
  rows:Object.freeze(rows)});
window.NOMUSA_CANONICAL_SELECTION_V1=Object.freeze({...prev,items:Object.freeze(items),qualityV10:gate});
window.NOMUSA_V10_QUALITY_GATE=gate;
})();

/* NOMUSA V13 — 2022·2023·2025 법률과목 50점 사례형 12개 확장 overlay(render-only).
 * 원장 ID·배점·localStorage 키·원본 PDF 불변. 직전 텍스트는 detailedBeforeV13/compressedBeforeV13으로 보존.
 * 분량 기준: 앱 writingPlan 기본값(500자/쪽)으로 8쪽=4,000자 이상. 실제 수기 장수 검증 아님. */
(function(){'use strict';
const prev=window.NOMUSA_CANONICAL_SELECTION_V1;
const v12=window.NOMUSA_V12_QUALITY_GATE;
const cases=window.NOMUSA_V13_MANUSCRIPTS||{};
const questions=window.N27_CATALOG?.items||[];
const expected=['2022-labor1-1','2022-labor2-1','2022-admin-1','2022-civil-1','2023-labor1-1','2023-labor2-1','2023-admin-1','2023-civil-1',
 '2025-labor1-1','2025-labor2-1','2025-admin-1','2025-civil-1'];
const CHARS_PER_PAGE_APP_DEFAULT=500,MIN_PAGES_50=8;
if(!prev?.items||v12?.v12Rewritten!==20||questions.length!==377||Object.keys(prev.items).length!==328)
  throw Error('NOMUSA_V13_BASELINE_MISMATCH');
if(Object.keys(cases).length!==expected.length||expected.some(id=>!cases[id])||Object.keys(cases).some(id=>!expected.includes(id)))
  throw Error('NOMUSA_V13_CASE_REGISTRY_MISMATCH');
const qmap=new Map(questions.map(q=>[q.id,q]));
const items=Object.assign(Object.create(null),prev.items),rows=[];
const seeds=window.N1071_SEEDS=window.N1071_SEEDS||{};
for(const id of expected){
 const q=qmap.get(id),before=prev.items[id],v=cases[id];
 if(!q?.sourceText||!before?.renderable||!before.detailed||!before.compressed)throw Error('NOMUSA_V13_BASE_MISSING_'+id);
 if(q.points!==50||v.points!==50||v.parts.reduce((a,b)=>a+b,0)!==50)throw Error('NOMUSA_V13_SCORE_MISMATCH_'+id);
 const est=v.full.length/CHARS_PER_PAGE_APP_DEFAULT;
 if(est<MIN_PAGES_50||v.full.length<before.detailed.length*1.1||v.compact.length<=before.compressed.length||
    v.compact.length>=v.full.length*0.5||!/Ⅰ\.[\s\S]*Ⅱ\.[\s\S]*Ⅲ\.[\s\S]*Ⅳ\./.test(v.compact)||!/결론/.test(v.compact))
  throw Error('NOMUSA_V13_NOT_ENHANCED_'+id);
 const next=Object.freeze({...before,detailed:v.full,compressed:v.compact,
   detailedBeforeV13:before.detailed,compressedBeforeV13:before.compressed,
   subPointsV13:Object.freeze([...v.parts]),appPageEstimateV13:Math.round(est*10)/10,
   memorySeedsV13:Object.freeze([...v.seeds]),verifiedPrecedentUrlsV13:Object.freeze([...v.evidence]),
   precedentAuditStatusV13:v.status,contentStatusV13:'A_LEARNING_DRAFT_COMPLETE_50PT_EXPANDED',
   finalAcademicApproval:'HOLD',officialScoreApproval:'HOLD',paperPagesVerified:false,scoringApproved:false});
 items[id]=next;
 seeds[id]=[v.seeds];
 rows.push(Object.freeze({id,year:q.year,subject:q.subject,points:50,subPoints:v.parts,
   priorDetailedChars:before.detailed.length,revisedDetailedChars:v.full.length,
   priorCompactChars:before.compressed.length,revisedCompactChars:v.compact.length,
   appPageEstimate:Math.round(est*10)/10,previousVersionPreserved:true,
   precedentUrls:Object.freeze([...v.evidence]),manualPageCountVerified:false,finalApproval:'HOLD'}));
}
if(Object.keys(items).length!==328||rows.length!==12)throw Error('NOMUSA_V13_ID_SET_CHANGED');
const gate=Object.freeze({schema:'nomusa-20year-essay-50pt-expansion/13',
  sourceQuestions:377,representativeCandidates:328,v13Expanded:12,
  pageEstimateBasis:'app writingPlan default 500 chars/page (user-adjustable 300~800)',
  allAtLeastEightAppPages:rows.every(r=>r.appPageEstimate>=MIN_PAGES_50),
  scope:'2022·2023·2025 노동법Ⅰ·Ⅱ·행정쟁송법·민사소송법 50점 사례형 12개',
  originalCatalogChanged:false,originalPointsChanged:false,originalStorageKeysChanged:false,
  productionMutated:false,previewDeployed:false,handwritingPageTargetReached:false,finalContentApprovals:0,
  reviewStatus:'REVIEW_ONLY_V13_50PT_EXPANSION_CONTENT_HOLD',rows:Object.freeze(rows)});
window.NOMUSA_CANONICAL_SELECTION_V1=Object.freeze({...prev,items:Object.freeze(items),qualityV13:gate});
window.NOMUSA_V13_QUALITY_GATE=gate;
})();

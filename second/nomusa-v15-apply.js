/* NOMUSA V15 — 2007~2014 법률 기본초안 50점 28개 재작성 + 2019·2020 법률 50점 8개 확장 overlay(render-only).
 * 원장 ID·배점·localStorage 키·원본 PDF 불변. 직전 텍스트는 detailedBeforeV15/compressedBeforeV15로 보존.
 * 분량 기준: 앱 writingPlan 기본값 500자/쪽. 실제 필기 장수 검증 아님. 2007~2012 legacy2 문항은 HWP 원문 시각대조 HOLD. */
(function(){'use strict';
const prev=window.NOMUSA_CANONICAL_SELECTION_V1;
const v13=window.NOMUSA_V13_QUALITY_GATE;
const cases=window.NOMUSA_V15_MANUSCRIPTS||{};
const questions=window.N27_CATALOG?.items||[];
const GROUPS={
 labor_a:['legacy2-2007-labor2-q1','legacy2-2008-labor1-q1','legacy2-2008-labor2-q1','legacy2-2009-labor2-q1','legacy2-2010-labor-q1','legacy2-2010-labor-q2','legacy2-2011-labor1-q1','legacy2-2011-labor2-q1'],
 labor_b:['legacy2-2012-labor1-q1','legacy2-2012-labor2-q1','2013_p1_q1','2013_p2_q1','2014_p1_q1','2014_p2_q1'],
 admin:['legacy2-2007-administrative-q1','legacy2-2007-administrative-q2','legacy2-2008-administrative-q1','legacy2-2010-administrative-q1','legacy2-2011-administrative-q1','legacy2-2012-administrative-q1','2013_p4_q1','2014_p4_q1'],
 civil:['legacy2-2010-civil-procedure-q1','legacy2-2010-civil-procedure-q2','legacy2-2011-civil-procedure-q1','legacy2-2012-civil-procedure-q1','2013_p7_q1','2014_p7_q1'],
 v12:['2019_p5_q1','2019_p6_q1','2020_p1_q1','2020_p2_q1','2019_p1_q1','2020_p4_q1','2019_p4_q1','2020_p7_q1']};
const expected=Object.values(GROUPS).flat();
if(!prev?.items||v13?.v13Expanded!==12||questions.length!==377||Object.keys(prev.items).length!==328)
  throw Error('NOMUSA_V15_BASELINE_MISMATCH');
const present=expected.filter(id=>cases[id]);
if(Object.keys(cases).some(id=>!expected.includes(id)))throw Error('NOMUSA_V15_UNEXPECTED_ID');
const qmap=new Map(questions.map(q=>[q.id,q]));
const items=Object.assign(Object.create(null),prev.items),rows=[];
const seeds=window.N1071_SEEDS=window.N1071_SEEDS||{};
for(const id of present){
 const q=qmap.get(id),before=prev.items[id],v=cases[id];
 if(!q?.sourceText||!before?.renderable||!before.detailed||!before.compressed)throw Error('NOMUSA_V15_BASE_MISSING_'+id);
 const pts=typeof q.points==='number'?q.points:before.pointsVerifiedV12;
 if(pts!==50||v.points!==50||!Array.isArray(v.parts)||v.parts.reduce((a,b)=>a+b,0)!==50)throw Error('NOMUSA_V15_SCORE_MISMATCH_'+id);
 if(v.full.length<4200||v.compact.length<700||v.compact.length>=v.full.length*0.5||
    !/Ⅰ\.[\s\S]*Ⅱ\.[\s\S]*Ⅲ\.[\s\S]*Ⅳ\./.test(v.compact)||!/결론/.test(v.compact)||!/【암기·복습 카드】/.test(v.full)||
    /확인되지 않은 판결번호를 만들지 않는다/.test(v.full))
  throw Error('NOMUSA_V15_NOT_ENHANCED_'+id);
 const legacy=id.startsWith('legacy2-');
 const next=Object.freeze({...before,detailed:v.full,compressed:v.compact,
   detailedBeforeV15:before.detailed,compressedBeforeV15:before.compressed,
   subPointsV15:Object.freeze([...v.parts]),appPageEstimateV15:Math.round(v.full.length/50)/10,
   memorySeedsV15:Object.freeze([...v.seeds]),verifiedPrecedentUrlsV15:Object.freeze([...v.evidence]),
   precedentAuditStatusV15:v.status,sourceVisualCheckHoldV15:legacy,
   contentStatusV15:'A_LEARNING_DRAFT_COMPLETE_50PT',
   finalAcademicApproval:'HOLD',officialScoreApproval:'HOLD',paperPagesVerified:false,scoringApproved:false});
 items[id]=next; seeds[id]=[v.seeds];
 rows.push(Object.freeze({id,year:q.year,subject:q.subject,points:50,subPoints:v.parts,
   priorDetailedChars:before.detailed.length,revisedDetailedChars:v.full.length,
   priorCompactChars:before.compressed.length,revisedCompactChars:v.compact.length,
   appPageEstimate:Math.round(v.full.length/50)/10,sourceVisualCheckHold:legacy,
   precedentUrls:Object.freeze([...v.evidence]),manualPageCountVerified:false,finalApproval:'HOLD'}));
}
if(Object.keys(items).length!==328)throw Error('NOMUSA_V15_ID_SET_CHANGED');
const gate=Object.freeze({schema:'nomusa-20year-essay-law50-v15/15',
  sourceQuestions:377,representativeCandidates:328,v15Target:expected.length,v15Rewritten:rows.length,
  groups:Object.freeze(Object.fromEntries(Object.entries(GROUPS).map(([g,l])=>[g,l.filter(id=>cases[id]).length]))),
  pageEstimateBasis:'app writingPlan default 500 chars/page',
  originalCatalogChanged:false,originalPointsChanged:false,originalStorageKeysChanged:false,
  productionMutated:false,previewDeployed:false,handwritingPageTargetReached:false,finalContentApprovals:0,stage5Count:0,
  reviewStatus:'REVIEW_ONLY_V15_LAW50_CONTENT_HOLD',rows:Object.freeze(rows)});
window.NOMUSA_CANONICAL_SELECTION_V1=Object.freeze({...prev,items:Object.freeze(items),qualityV15:gate});
window.NOMUSA_V15_QUALITY_GATE=gate;
})();

/* NOMUSA V9 — source-matched case-law argument quality overlay.
 * Render-only revision, preserving all catalog, ID, localStorage and source PDF bytes.
 * Four verified precedent cases. Remaining 53 unaltered. No official score approval. */
(function(){'use strict';
const prev=window.NOMUSA_CANONICAL_SELECTION_V1;
const baseline=window.NOMUSA_V8_QUALITY_GATE;
const cases=window.NOMUSA_V9_MANUSCRIPTS||{};
const questions=window.N27_CATALOG?.items||[];
const expected=['2022-labor1-2','2022-admin-2','2023-labor1-1','2023-admin-3'];
if(!prev?.items||baseline?.focusedRewritten!==57||baseline?.newManuscripts!==38
 ||questions.length!==377||Object.keys(prev.items).length!==328)
  throw Error('NOMUSA_V9_BASELINE_MISMATCH');
if(Object.keys(cases).length!==4||expected.some(id=>!cases[id])||
   Object.keys(cases).some(id=>!expected.includes(id)))
  throw Error('NOMUSA_V9_CASE_REGISTRY_MISMATCH');
const questionMap=new Map(questions.map(q=>[q.id,q]));
const items=Object.assign(Object.create(null),prev.items),rows=[];
for(const id of expected){
 const q=questionMap.get(id),before=prev.items[id],v=cases[id];
 if(!q?.sourceText||!before?.renderable||!before?.detailed||!before?.compressed||
  !v.full||!v.compact||v.full.length<=before.detailed.length+200||
  v.compact.length<=before.compressed.length||v.evidence?.length<1)
  throw Error('NOMUSA_V9_NOT_ENHANCED_'+id);
 if((id==='2023-labor1-1'?q.points===50:q.points===25)!==true)
  throw Error('NOMUSA_V9_SCORE_MISMATCH_'+id);
 const next=Object.freeze({...before,detailed:v.full,compressed:v.compact,
   detailedBeforeV9:before.detailed,compressedBeforeV9:before.compressed,
   sourceMatchedJudgmentV9:Object.freeze([...v.evidence]),
   precedentAuditStatusV9:v.status,
   finalAcademicApproval:'HOLD',officialScoreApproval:'HOLD',
   paperPagesVerified:false,sourcePdfOfficialHashVerified:false,
   scoringApproved:false});
 items[id]=next;
 rows.push(Object.freeze({id,year:q.year,subject:q.subject,points:q.points,
   priorDetailedChars:before.detailed.length,revisedDetailedChars:v.full.length,
   priorCompactChars:before.compressed.length,revisedCompactChars:v.compact.length,
   previousVersionPreserved:next.detailedBeforeV9===before.detailed&&next.compressedBeforeV9===before.compressed,
   precedentUrls:Object.freeze([...v.evidence]),
   officialExamSourceVerified:false,manualPageCountVerified:false,
   finalApproval:'HOLD'}));
}
if(Object.keys(items).length!==328||rows.length!==4)throw Error('NOMUSA_V9_ID_SET_CHANGED');
const gate=Object.freeze({schema:'nomusa-20year-essay-legal-depth/9',
  sourceQuestions:377,representativeCandidates:328,v8FocusedManuscripts:57,
  originalFocusedDraftsPreserved:true,v9Deepened:4,remainingFocusedNeedingIndividualReview:53,
  originalCatalogChanged:false,originalPointsChanged:false,originalStorageKeysChanged:false,
  originalsMutated:false,productionMutated:false,previewDeployed:false,
  fourDirectPreExamJudgmentsChecked:true,sourcePdfOfficialHashVerified:false,
  handwritingPageTargetReached:false,finalContentApprovals:0,
  reviewStatus:'REVIEW_ONLY_FOUR_PRECEDENTS_VERIFIED_CONTENT_HOLD',
  rows:Object.freeze(rows)});
window.NOMUSA_CANONICAL_SELECTION_V1=Object.freeze({...prev,
  items:Object.freeze(items),qualityV9:gate});
window.NOMUSA_V9_QUALITY_GATE=gate;
})();
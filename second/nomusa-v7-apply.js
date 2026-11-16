/* NOMUSA 20YEAR V7 — Five direct-case 50-point independent essay manuscripts.
 * In-memory projection only. Original problem pages, point values, stable IDs,
 * localStorage/user notes, prior essays, RC27, RC35, main and Production unchanged.
 * Drafts are not verified handwriting-page-length answers. */
(function(){'use strict';
const snapshot=window.NOMUSA_CANONICAL_SELECTION_V1;
const v6=window.NOMUSA_V6_MANUSCRIPT_GATE;
const corpus=window.NOMUSA_V7_MANUSCRIPTS||{};
const questions=window.N27_CATALOG?.items||[];
const expected=[
  '2022-labor2-1','2022-civil-1','2022-admin-1',
  '2023-civil-1','2023-admin-1'
];
if(snapshot?.gate?.catalogCount!==377||v6?.v6NewManuscripts!==9||
   v6?.remainingInFocusedSet!==43||questions.length!==377)
  throw Error('NOMUSA_V7_EXPECTED_V6_BASELINE_MISMATCH');
const keys=Object.keys(corpus);
if(keys.length!==5||expected.some(id=>!corpus[id])||
 keys.some(id=>!expected.includes(id)))throw Error('V7_MANUSCRIPT_SET_MISMATCH');
const lookup=new Map(questions.map(x=>[x.id,x]));
const items=Object.assign(Object.create(null),snapshot.items),rows=[];
for(const id of expected){
 const q=lookup.get(id),prev=snapshot.items[id],manuscript=corpus[id];
 if(!q||q.points!==50||!q.sourceText?.includes('문제')||
  !prev?.renderable||!prev.detailed||!prev.compressed||
  manuscript.full?.length<3100||manuscript.compact?.length<300)
  throw Error('NOMUSA_V7_SOURCE_OR_TEXT_INVALID_'+id);
 items[id]=Object.freeze({...prev,
  detailed:manuscript.full,compressed:manuscript.compact,
  detailedBeforeV7:prev.detailed,compressedBeforeV7:prev.compressed,
  sourceAwareFullEssayV7:'SUBQUESTION_SCORED_LONGFORM_DRAFT',
  explicitSourcesV7:Object.freeze([...(manuscript.sources||[])]),
  examYearResearchV7:manuscript.verification||'PARTIAL',
  independentLawAcademicApproval:'HOLD',
  sourcePDFVisualVerification:'HOLD',
  handwritingPageVerification:'HOLD',
  scoringApproved:false});
 rows.push(Object.freeze({id,year:q.year,points:q.points,subject:q.subject,
  fullChars:manuscript.full.length,compactChars:manuscript.compact.length,
  sourceTextDirectlyRead:true,oldDetailRestorable:!!items[id].detailedBeforeV7,
  oldCompactRestorable:!!items[id].compressedBeforeV7,
  examYearEvidence:manuscript.verification||'HOLD',contentApproval:'HOLD',
  originalPDFVisualVerified:false,handwritingPagesVerified:false}));
}
if(Object.keys(items).length!==328||rows.length!==5)throw Error('V7_CANDIDATE_COUNT_BROKEN');
const gate=Object.freeze({schema:'nomusa-20year-essay-manuscript/7',
 exercises:377,candidates:328,v4Drafts:57,v5Rewritten:5,v6Rewritten:9,
 v7NewManuscripts:5,totalRewrittenInFocusedSet:19,
 remainingInFocusedSet:38,v7FiftyPoint:5,
 originalCatalogChanged:false, originalPointsChanged:false,
 originalIDsChanged:false, existingStoredAnswersChanged:false,
 storageKeysChanged:false,previousManuscriptsPreserved:true,
 handwriting8to10PageVerified:false,
 fullLegalAndAcademicApproval:false,
 finalApprovalCount:0,status:'REVIEW_BRANCH_DRAFT_HOLD',rows:Object.freeze(rows)});
window.NOMUSA_CANONICAL_SELECTION_V1=Object.freeze({...snapshot,
 items:Object.freeze(items),qualityV7:gate});
window.NOMUSA_V7_MANUSCRIPT_GATE=gate;
})();
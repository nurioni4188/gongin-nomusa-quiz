/* NOMUSA V5 longform manuscripts: only five individually reviewed original questions.
 * No fake completion counts for all 57; all legal source approvals/handwritten pages HOLD.
 * The prior canonical projection, IDs, study keys, and original data remain intact. */
(function(){'use strict';
const old=window.NOMUSA_CANONICAL_SELECTION_V1,v4=window.NOMUSA_V4_DEEPENING;
const drafts=window.NOMUSA_V5_MANUSCRIPTS||{};
const expected=['2023-econ-1','2025-econ-2','2025-econ-3','2025-labor2-1','2025-labor1-2'];
if(old?.gate?.catalogCount!==377||v4?.authored!==57||v4.allCandidates!==328||
   Object.keys(drafts).length!==5||expected.some(id=>!drafts[id]))
  throw Error('NOMUSA_V5_REVIEW_BASELINE_MISMATCH');
const projection=Object.assign(Object.create(null),old.items);
const catalog=new Map((window.N27_CATALOG?.items||[]).map(q=>[q.id,q]));
const report=[];
for(const id of expected){
 const before=old.items[id],draft=drafts[id],source=catalog.get(id);
 if(!before?.renderable||!source?.sourceText||!draft?.full||
    draft.full.length<1500||draft.compact.length<250||
    !source.sourceText.includes('문제'))throw Error('V5_MANUSCRIPT_SOURCE_OR_LENGTH_'+id);
 projection[id]=Object.freeze({...before,
   detailed:draft.full,compressed:draft.compact,
   detailedBeforeV5:before.detailed,compressedBeforeV5:before.compressed,
   editorialV5:'QUESTION_AND_SUBQUESTION_ALIGNED_MANUSCRIPT',
   legalAcademicApproval:'HOLD',
   handwritingPagesVerified:false,
   sourcePDFVisualVerified:false,scoringApproved:false});
 report.push(Object.freeze({id,year:source.year,subject:source.subject,
   points:source.points,manuscriptCharacters:draft.full.length,
   previousTextPreserved:true,originalQuestionVerifiedInCatalog:true,
   examYearLegalOrAcademicReview:'PARTIAL_OR_HOLD',
   handwritingTargetPagesVerified:false,sourcePDFVisualVerified:false,
   finalApproved:false}));
}
if(Object.keys(projection).length!==328||report.length!==5)throw Error('V5_REGISTRY_BREAK');
const gate=Object.freeze({schema:'nomusa-answer-manuscript/5',
  originalExercises:377,originalRepresentativeCandidates:328,
  v4ExistingDeepened:57,fullyRewrittenQuestionManuscripts:5,
  notYetRewrittenInThisPass:52,
  originalCatalogModified:false,studyKeysChanged:false,
  previousAnswerVersionsPreserved:true,
  all50PointPageTargetsCertified:false,contentApprovalsIssued:0,
  finalStatus:'DRAFT_LONGFORM_NOT_HANDWRITING_COMPLETE',rows:Object.freeze(report)});
window.NOMUSA_CANONICAL_SELECTION_V1=Object.freeze({...old,
  items:Object.freeze(projection),qualityV5:gate});
window.NOMUSA_V5_MANUSCRIPT_GATE=gate;
})();
/* NOMUSA 20YEAR QUALITY V6: nine original-prompt-aligned essay manuscripts.
 * Zero official approvals. Replaces only the in-memory study display projection.
 * Original PDFs/HWP, catalog question IDs, scores, existing save keys, prior answer
 * versions, production, and release branches are NEVER modified by this module. */
(function(){'use strict';
const old=window.NOMUSA_CANONICAL_SELECTION_V1;
const v4=window.NOMUSA_V4_DEEPENING;
const v5=window.NOMUSA_V5_MANUSCRIPT_GATE;
const originals=window.N27_CATALOG?.items||[];
const drafts=window.NOMUSA_V6_MANUSCRIPTS||{};
const expected=[
 '2025-econ-1','2025-labor1-1','2025-admin-1','2025-civil-1',
 '2025-civil-2','2025-civil-3','2022-labor1-1',
 '2023-labor2-1','2022-econ-1'
];
if(old?.gate?.catalogCount!==377||v4?.authored!==57||
   v5?.fullyRewrittenQuestionManuscripts!==5||originals.length!==377)
  throw Error('NOMUSA_V6_SOURCE_SNAPSHOT_NOT_VERIFIED');
const ids=Object.keys(drafts);
if(ids.length!==9||expected.length!==9||
   expected.some(id=>!drafts[id])||ids.some(id=>!expected.includes(id)))
  throw Error('NOMUSA_V6_MANUSCRIPT_REGISTRY_MISMATCH');
const lookup=new Map(originals.map(x=>[x.id,x]));
const byId=Object.assign(Object.create(null),old.items),rows=[];
for(const id of expected){
 const q=lookup.get(id),oldRecord=old.items[id],d=drafts[id];
 if(!q?.sourceText||!oldRecord?.renderable||!d?.full||!d?.compact||
    d.full.length<1900||d.compact.length<180||
    !q.sourceText.includes('문제')||!oldRecord.detailed||!oldRecord.compressed)
   throw Error('NOMUSA_V6_INVALID_MANUSCRIPT_'+id);
 const revised=Object.freeze({...oldRecord,
    detailed:d.full,compressed:d.compact,
    detailedBeforeV6:oldRecord.detailed,
    compressedBeforeV6:oldRecord.compressed,
    issueBasedManuscriptV6:'FULL_QUESTION_AND_SUBQUESTION_DRAFT',
    manuscriptEvidenceUrls:Object.freeze([...(d.sources||[])]),
    legalAcademicApproval:'HOLD',
    examYearIndependentCaseVerification:'PARTIAL_OR_HOLD',
    handwritingPageVerification:'HOLD',
    sourcePDFVisualVerified:false,scoringApproved:false});
 byId[id]=revised;
 rows.push(Object.freeze({id,year:q.year,subject:q.subject,points:q.points,
    fullChars:d.full.length,compactChars:d.compact.length,
    previousDetailPreserved:revised.detailedBeforeV6===oldRecord.detailed,
    previousCompactPreserved:revised.compressedBeforeV6===oldRecord.compressed,
    sourceQuestionLinked:true,
    contentApproval:'HOLD',
    legalAcademicSources:d.validation||'PARTIAL_OR_HOLD',
    handwritingPageVerification:'HOLD',sourcePDFVisualVerified:false}));
}
if(Object.keys(byId).length!==328||rows.length!==9)throw Error('NOMUSA_V6_CANONICAL_SET_MISMATCH');
const gate=Object.freeze({schema:'nomusa-20year-essay-manuscript/6',
  exercises:377,candidates:328,
  v4ArgumentAdditions:57,v5PriorManuscripts:5,v6NewManuscripts:9,
  currentlyRewrittenInFocusedSet:14,remainingInFocusedSet:43,
  fiftyPointV6:7,twentyFivePointV6:2,
  modifiedCatalog:false,modifiedStoredAnswers:false,modifiedKeys:false,
  sourcePageVerified:false,
  target8to10PagesVerified:false,target4PagesVerified:false,
  officialFinalContentApprovals:0,
  manuscriptStatus:'DRAFT_ISSUE_SPECIFIC_NOT_HANDWRITING_CERTIFIED',
  rows:Object.freeze(rows)});
window.NOMUSA_CANONICAL_SELECTION_V1=Object.freeze({...old,
  items:Object.freeze(byId),qualityV6:gate});
window.NOMUSA_V6_MANUSCRIPT_GATE=gate;
})();
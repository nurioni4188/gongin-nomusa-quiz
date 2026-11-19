/* NOMUSA V8 — 38 source-aligned essay manuscript drafts.
 * V8 is a review-only presentation projection. Never alter user-written answers,
 * app save keys, original IDs, original points or source PDF.
 * "All 57 drafted" does not mean 50pt 8-10 page manuscripts were certified. */
(function(){'use strict';
const before=window.NOMUSA_CANONICAL_SELECTION_V1;
const catalog=window.N27_CATALOG?.items||[];
const drafts=window.NOMUSA_V8_MANUSCRIPTS||{};
const v4=window.NOMUSA_V4_DEEPENING,v5=window.NOMUSA_V5_MANUSCRIPT_GATE,
      v6=window.NOMUSA_V6_MANUSCRIPT_GATE,v7=window.NOMUSA_V7_MANUSCRIPT_GATE;
const recovered=window.NOMUSA_V8_PDF_2023_LABOR1_Q1;
if(before?.gate?.catalogCount!==377||catalog.length!==377||
   v4?.authored!==57||v5?.fullyRewrittenQuestionManuscripts!==5||
   v6?.v6NewManuscripts!==9||v7?.v7NewManuscripts!==5)
  throw Error('NOMUSA_V8_BASELINE_DRIFT');
if(recovered?.page!==2||recovered?.subquestions?.map(q=>q.points).join(',')!=='25,25'||
   recovered.sha256!=='9fb544e9e6bed6d314a9d151474e23d009c7f6bd82ea01c6ec4d342486fdfa7d')
  throw Error('NOMUSA_V8_ORIGINAL_PDF_RECOVERY_DRIFT');
const accounted=new Set([...v5.rows,...v6.rows,...v7.rows].map(q=>q.id));
const v4ids=v4.rows.map(q=>q.id);
const pending=v4ids.filter(id=>!accounted.has(id));
if(new Set(v4ids).size!==57||accounted.size!==19||pending.length!==38||
   Object.keys(drafts).length!==38||pending.some(id=>!drafts[id])||
   Object.keys(drafts).some(id=>!pending.includes(id)))
  throw Error('NOMUSA_V8_NOT_EXACT_REMAINING_38');
const byQuestion=new Map(catalog.map(q=>[q.id,q]));
const transformed=Object.assign(Object.create(null),before.items);
const rows=[];
for(const id of pending){
 const q=byQuestion.get(id),prev=before.items[id],draft=drafts[id];
 if(!q||!prev?.renderable||!prev.detailed||!prev.compressed||
    !draft?.full||!draft?.compact)
   throw Error('NOMUSA_V8_MISSING_SOURCE_OR_PREVIOUS_'+id);
 const min=Number(q.points)>=50?1200:(Number(q.points)>=25?700:350);
 if(draft.full.length<min||draft.compact.length<150||
    !draft.full.includes('## '))
   throw Error('NOMUSA_V8_EMPTY_OR_THIN_MANUSCRIPT_'+id);
 transformed[id]=Object.freeze({...prev,
    detailed:draft.full,compressed:draft.compact,
    detailedBeforeV8:prev.detailed,compressedBeforeV8:prev.compressed,
    issueBasedEssayV8:'ORIGINAL_QUESTION_ANSWER_REWRITTEN',
    originalQuestionSourceType:q.sourceOnly?'LEGACY_HWP_TEXT_ONLY':'CATALOG_PDF_OR_EXAM_TEXT',
    recoveredQuestion2023:q.id==='2023-labor1-1'?recovered:null,
    legalAcademicEvidenceV8:draft.status||'HOLD',
    examYearOriginalPDFVisualVerified:false,
    examYearStatutesAndPrecedentsApproved:false,
    handwritingPageTargetReached:false,
    contentApproved:false,scoringApproved:false});
 rows.push(Object.freeze({id,year:q.year,points:q.points,subject:q.subject,
    manuscriptChars:draft.full.length,compressedChars:draft.compact.length,
    sourceOnly:!!q.sourceOnly,
    sourcePageReadback:q.id==='2023-labor1-1'?'REPO_PDF_2023_P2':'NOT_APPROVED',
    previousDetailedSaved:!!transformed[id].detailedBeforeV8,
    previousCompressedSaved:!!transformed[id].compressedBeforeV8,
    officialSourceIdentityVerified:false,
    originalSourcePDFVisualVerified:false,
    contentApproved:false,handwritingPagesVerified:false}));
}
if(Object.keys(transformed).length!==328||rows.length!==38||
   rows.filter(x=>x.sourceOnly).length!==10)
  throw Error('NOMUSA_V8_OVERVIEW_MISMATCH');
const scoreCounts=rows.reduce((a,r)=>(a[r.points]=(a[r.points]||0)+1,a),{});
const gate=Object.freeze({schema:'nomusa-20year-essay-quality-batch/8',
  catalogCount:377,representativeCandidates:328,focusedTotal:57,
  previousManuscripts:19,newManuscripts:38,
  focusedRewritten:57,focusedOutstanding:0,
  earlierSourceOnlyItems:10,
  officialPublishedSourceReconciled:0,
  recovered2023Labor1Q1Subquestions:2,
  scoreCounts:Object.freeze(scoreCounts),
  previousAnswerVersionPreserved:true,
  canonicalIDsChanged:false,originalPointsChanged:false,storageKeysChanged:false,
  originalDocumentsChanged:false,productionChanged:false,
  archivedHWPVisualCheckPassed:false,allExamYearLegalRulesApproved:false,
  paper8to10PagesProven:false, paper4PagesProven:false,
  finalOfficialContentApprovals:0,approval:'HOLD',
  materialStatus:'ALL_57_REWRITTEN_DRAFTS_NOT_HANDWRITING_CERTIFIED',
  rows:Object.freeze(rows)});
window.NOMUSA_CANONICAL_SELECTION_V1=Object.freeze({...before,
  items:Object.freeze(transformed),qualityV8:gate});
window.NOMUSA_V8_QUALITY_GATE=gate;
})();
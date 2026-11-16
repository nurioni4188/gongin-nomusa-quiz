/* NOMUSA V4 — 57 problem-specific argumentative additions, 26 PDF score readback.
 * No original source, page, IDs, stored records, production, or exam-year legal approvals are mutated.
 */
(function(){'use strict';
const old=window.NOMUSA_CANONICAL_SELECTION_V1;
const thin=window.NOMUSA_THIN_ENRICHMENT_V2;
const v3=window.NOMUSA_20YEAR_V3_GATE;
const score=window.NOMUSA_V4_PDF_SCORE_AUDIT;
const drafts=window.NOMUSA_V4_DEEP_DRAFTS||{};
if(old?.gate?.catalogCount!==377||thin?.authored!==61||
   v3?.v3Manuscripts!==7||score?.total!==26||score.matchedScoreMarkers!==26)
  throw Error('NOMUSA_V4_INTEGRITY_GATE');
const skip=new Set(['legacy2-2007-administrative-q1','legacy2-2008-administrative-q1',
  'legacy2-2010-civil-procedure-q1','2022-econ-2']);
const targets=thin.rows.map(x=>x.id).filter(id=>!skip.has(id));
const drafted=Object.keys(drafts);
if(targets.length!==57||drafted.length!==57||new Set(drafted).size!==57||
   drafted.some(id=>!targets.includes(id))||targets.some(id=>!drafts[id]))
  throw Error('NOMUSA_V4_57_IDS_MISMATCH');
const next=Object.assign(Object.create(null),old.items);
const catalogue=new Map((window.N27_CATALOG?.items||[]).map(x=>[x.id,x]));
const result=[];
for(const id of targets){
 const existing=old.items[id],d=drafts[id],row=catalogue.get(id);
 const addition=String(d?.detail||'').trim();
 if(!existing?.renderable||!row||addition.length<160||
    !existing.detailed||!existing.compressed)throw Error('NOMUSA_V4_BAD_ANSWER_'+id);
 const detail=existing.detailed+'\n\n【V4 출제문항 연계 심화논증 · 검증 전 학습 초안】\n'+addition;
 next[id]=Object.freeze({...existing,detailed:detail,
   previousDetailedV4:existing.detailed,previousCompressedV4:existing.compressed,
   issueDeepeningV4:'ISSUE_SPECIFIC_SOURCE_CONNECTED_DRAFT',
   examYearSourcesStatus:d.verification||'HOLD',
   sourcePDFVisualVerified:false,academicLegalContentApproval:'HOLD',
   handwritingPagesVerified:false,scoringApproved:false});
 result.push(Object.freeze({id,year:row.year,subject:row.subject,points:row.points,
   previousDetailLength:existing.detailed.length,newDetailLength:detail.length,
   addedCharacters:addition.length,
   existingCompressedPreserved:true,oldAnswerPreserved:true,
   examYearSourceVerification:d.verification||'HOLD',sourcePDFVisualVerified:false,
   contentApproval:'HOLD',handwritingPagesVerified:false}));
}
if(Object.keys(next).length!==328||result.length!==57)throw Error('NOMUSA_V4_328_CANDIDATES_BROKEN');
const report=Object.freeze({schema:'nomusa-20year-57-deepening/4',targets:57,authored:57,
  allCandidates:328,allCatalogue:377,previousV1Expanded:208,
  previousV2Added:61,previousV3Manuscripts:7,
  scoreAuditCount:26,repoPDFScoreReadback:26,qnetPublisherFileHashVerified:false,
  remaining57RequiredExamYearVerification:57,
  50PointPagesMet:false,25PointPagesMet:false,
  originalCatalogModified:false,originalStorageKeysModified:false,
  previousCompressedPreserved:true,
  independentContentApproval:'HOLD',status:'DRAFT_AWAITING_EXAM_YEAR_SOURCE_AND_HANDWRITING_REVIEW',
  rows:Object.freeze(result)});
window.NOMUSA_CANONICAL_SELECTION_V1=Object.freeze({...old,items:Object.freeze(next),qualityV4:report});
window.NOMUSA_V4_DEEPENING=report;
})();
/* NOMUSA 20YEAR QUALITY BATCH V2 - 61 source/topic-specific enrichment drafts.
 * This modifies an in-memory projection only. It does not alter the catalog,
 * existing source PDFs, IDs, save keys, original detailed/compact drafts or approvals.
 * Each authored passage is a study draft, not verified exam-year law or a grading key. */
(function(){'use strict';
const baseline=window.NOMUSA_CANONICAL_SELECTION_V1;
const batch=window.NOMUSA_20YEAR_QUALITY_BATCH_V1;
const drafts=window.NOMUSA_THIN_ANSWER_DRAFTS||{};
if(!baseline||!batch||baseline.gate?.catalogCount!==377||batch.candidateCount!==328){
  throw Error('NOMUSA_V2_HOLD_NO_VERIFIED_REGISTRY');
}
const targets=batch.rows.filter(x=>x.status==='HOLD_THIN_DETAIL');
const ids=targets.map(x=>x.id);
const names=Object.keys(drafts);
if(ids.length!==61||names.length!==61||ids.some(id=>!drafts[id])||names.some(id=>!ids.includes(id))){
  throw Error('NOMUSA_V2_HOLD_61_TO_61_MAPPING');
}
const byId=Object.assign(Object.create(null),baseline.items);
const report=[];
for(const row of targets){
  const original=baseline.items[row.id],entry=drafts[row.id];
  if(!original?.renderable||typeof entry?.detail!=='string'||typeof entry?.compact!=='string'||
     entry.detail.trim().length<110||entry.compact.trim().length<85){
    throw Error('NOMUSA_V2_HOLD_EMPTY_OR_SHORT_'+row.id);
  }
  const detailed=original.detailed+'\n\n【V2 출제문구 연계 추가 논증 · 법령·학술근거 검증 HOLD】\n'+entry.detail.trim();
  const compressed=original.compressed+'\n\n【V2 추가 압축논증 · 학습 초안】\n'+entry.compact.trim();
  byId[row.id]=Object.freeze({...original,detailed,compressed,
    beforeThinV2Detailed:original.detailed,beforeThinV2Compressed:original.compressed,
    qualityV2:'NEW_ISSUE_SPECIFIC_DRAFT_UNVERIFIED',contentStatus:'DRAFT_UNVERIFIED',
    scoringApproved:false,citationApproval:'HOLD',examYearSourcesVerified:false,
    handwritingPages:'HOLD'});
  report.push(Object.freeze({id:row.id,year:row.year,subject:row.subject,points:row.points,
    sourceStatus:row.sourceStatus,from:'HOLD_THIN_DETAIL',to:'NEW_ISSUE_SPECIFIC_DRAFT_UNVERIFIED',
    oldDetailChars:original.detailed.length,newDetailChars:detailed.length,
    oldCompactChars:original.compressed.length,newCompactChars:compressed.length,
    sourcePageVerified:false,legalOrAcademicReview:'HOLD',handwritingPageVerified:false}));
}
const remaining=batch.rows.filter(x=>x.status!=='HOLD_THIN_DETAIL'&&x.status.startsWith('HOLD'));
const audit=Object.freeze({schema:'nomusa-20year-thin-issue-enrichment/2',status:'AUTHOR_DRAFT_READY_CONTENT_HOLD',
    targets:61,authored:report.length,remainingOtherHold:remaining.length,
    remainingPointsHold:remaining.filter(x=>x.status==='HOLD_POINTS_UNKNOWN').length,
    remainingOtherReasons:remaining.filter(x=>x.status!=='HOLD_POINTS_UNKNOWN').map(x=>({id:x.id,reason:x.status})),
    contentApproval:'HOLD',sourcePDFPageVerification:'HOLD',examYearLegalSources:'HOLD',
    authorship:'NEW_CONTENT_AUTHORED_FROM_QUESTION_TEXT_AND_EXISTING_DRAFT',
    sourceCatalogChanged:false,storageKeyChanged:false,rows:Object.freeze(report)});
window.NOMUSA_CANONICAL_SELECTION_V1=Object.freeze({...baseline,items:Object.freeze(byId),thinEnrichmentV2:audit});
window.NOMUSA_THIN_ENRICHMENT_V2=audit;
})();
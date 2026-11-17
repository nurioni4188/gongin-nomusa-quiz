/* NOMUSA V24: 30 full printed-question transcription candidates, sourced from original PDF
 * page images, 2015-2018 & 2021 HR/ORG. This changes only q.sourceText for 30
 * known child question IDs (not the PDF, question ID, points, learner storage,
 * detailed/compact answers, or approval). Original sourceText is preserved.
 * Independent source proofreading and content/expert approval remain HOLD.
 */
(function(){'use strict';
const source=window.N27_CATALOG?.items;
const records=[...(window.NOMUSA_V24_2015_2016||[]),
               ...(window.NOMUSA_V24_2017_2018||[]),
               ...(window.NOMUSA_V24_2021||[])];
const expectedYears=Object.freeze({2015:6,2016:6,2017:6,2018:6,2021:6});
const gateFail=(code,issues=[])=>{
 window.NOMUSA_V24_SOURCE_GATE=Object.freeze({status:'HOLD_'+code,
   count:records.length,issues,expertApproval:'HOLD',
   deploy:false,production:false,main:false,originalQuestionPDFsModified:false});
};
if(!Array.isArray(source)||!window.NOMUSA_V20_CONTENT_GATE||records.length!==30)
  {gateFail('SOURCE_OR_COUNT');return;}
const m=new Map(),issues=[];
for(let i=0;i<source.length;i++){
 const q=source[i];if(m.has(q.id))issues.push('DUPLICATE_CATALOG_'+q.id);m.set(q.id,{q,i});
}
const seen=new Set(),years={},pointCounts={50:0,25:0};
for(const e of records){
 if(seen.has(e.id)){issues.push('DUPLICATE_TRANSCRIPTION_'+e.id);continue;}
 seen.add(e.id);
 years[e.year]=(years[e.year]||0)+1;
 pointCounts[e.points]=(pointCounts[e.points]||0)+1;
 const old=m.get(e.id)?.q;
 if(!old)issues.push('NO_ORIGINAL_'+e.id);
 else {
   if(Number(old.year)!==e.year||String(old.subject)!==String(e.subject)||
      Number(old.points)!==e.points)
     issues.push('YEAR_SUBJECT_POINTS_MISMATCH_'+e.id);
   if(!old.sourceText||!(/요지|원문 전문은|기출 전문은|원본 PDF 참조|PDF를 참조|PDF 참조/.test(old.sourceText.slice(0,120))))
     issues.push('NOT_ORIGINAL_SUMMARY_'+e.id);
   if(!e.sourceText?.trim()||e.sourceText.includes('원문 전문은 PDF 참조')||
      !/\(\d+점\)/.test(e.sourceText))
     issues.push('NO_FULL_EXAM_TEXT_'+e.id);
   if(!e.sourceFile||!Number.isInteger(e.pdfPage)||e.pdfPage<1)
     issues.push('MISSING_PDF_PROVENANCE_'+e.id);
 }
}
for(const [year,n] of Object.entries(expectedYears))
 if(years[year]!==n)issues.push('SIX_PER_YEAR_'+year);
if(seen.size!==30||pointCounts[50]!==10||pointCounts[25]!==20)
 issues.push('TOTAL_OR_POINTS_'+seen.size+'_'+pointCounts[50]+'_'+pointCounts[25]);
if(issues.length){gateFail('PREFLIGHT',issues);return;}
const done=[];
for(const e of records){
 const {q,i}=m.get(e.id);
 source[i]={...q,sourceTextBeforeV24:q.sourceText,sourceText:e.sourceText,
   sourceCorrectionV24:Object.freeze({questionId:e.id,year:e.year,
     officialPDFCandidate:e.sourceFile,sourcePDFPage:e.pdfPage,
     comparisonMethod:'PDF_PAGE_IMAGE_VISUAL_TRANSCRIPTION_DRAFT',
     imageReviewedBy:'AI_VISUAL_REVIEW_NOT_INDEPENDENT_EXPERT',
     sourceProofreadApproval:'HOLD',expertContentApproval:'HOLD',
     priorSummaryPreserved:true}),
   scoringApproved:false};
 done.push(Object.freeze({id:e.id,year:e.year,points:e.points,
    beforeChars:q.sourceText.length,afterChars:e.sourceText.length,
    page:e.pdfPage,source:e.sourceFile,rollbackAvailable:true}));
}
window.NOMUSA_V24_SOURCE_GATE=Object.freeze({
 schema:'NOMUSA_V24_30_OFFICIAL_QUESTION_VISUAL_TRANSCRIPTION_CANDIDATES/1',
 status:'PASS_30_TRANSCRIPTION_CANDIDATES_EXPERT_SOURCE_PROOFREAD_HOLD',
 total:30,years:Object.freeze(years),points50:10,points25:20,rows:Object.freeze(done),
 originalPDFChanged:false,idsChanged:false,storageKeysChanged:false,
 answerDetailsChanged:false,expertApproval:'HOLD',finalApproval:'HOLD',
 previewDeployed:false,mainChanged:false,productionChanged:false
});
})();
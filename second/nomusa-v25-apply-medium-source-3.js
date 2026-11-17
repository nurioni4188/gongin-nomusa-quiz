/* NOMUSA V25: three MEDIUM official PDF image crosschecks.
 * 2016_p5_q2 is already visually faithful: keep its sourceText untouched.
 * 2019_p4_q3 and 2020_p7_q3: replace joined OCR + footer with exact printed
 * problem-3 prompt. Existing IDs, points, answers, other texts and keys immutable.
 * AI visual confirmation does NOT create independent expert approval.
 */
(function(){'use strict';
const catalog=window.N27_CATALOG?.items;
const v24=window.NOMUSA_V24_SOURCE_GATE;
const gateFail=(issues)=>{
 window.NOMUSA_V25_MEDIUM_GATE=Object.freeze({status:'HOLD_PREFLIGHT',issues,
   expected:3,sourceCorrections:0,independentExpertApproved:0,finalApproval:'HOLD',
   mainChanged:false,productionChanged:false,previewDeployed:false});
};
if(!Array.isArray(catalog)||!String(v24?.status||'').startsWith('PASS_')){
 gateFail(['MISSING_CATALOG_OR_V24_GATE']);return;
}
const printed=[
 {id:'2016_p5_q2',year:2016,subject:'경영조직론',points:25,
  sourceText:'2. 조직관리에서 학습의 중요성, 학습과정 그리고 학습의 주요 원리로서의 강화에 대하여 각각 설명하시오. (25점)',
  originalPDF:'source_pdf/2016/2016_second_full_original.pdf',page:7,action:'KEEP_ALREADY_MATCHES_PDF'},
 {id:'2019_p4_q3',year:2019,subject:'민사소송법',points:25,
  sourceText:'【문제 3】 공동소송참가에 관하여 설명하시오. (25점)',
  originalPDF:'source_pdf/2019/2019_p4_civil_procedure.pdf',page:1,action:'CORRECT_OCR_SPACE_AND_PAGE_FOOTER'},
 {id:'2020_p7_q3',year:2020,subject:'민사소송법',points:25,
  sourceText:'【문제 3】 유사필수적 공동소송에 관하여 설명하시오. (25점)',
  originalPDF:'source_pdf/2020/2020_p7_civil_procedure.pdf',page:1,action:'CORRECT_OCR_SPACE_AND_PAGE_FOOTER'}
];
const norm=(v)=>String(v||'').replace(/[^가-힣]/g,'');
const index=new Map(),issues=[];
for(let i=0;i<catalog.length;i++){
 if(index.has(catalog[i].id))issues.push('DUPLICATE_'+catalog[i].id);
 index.set(catalog[i].id,i);
}
for(const p of printed){
 const i=index.get(p.id);
 if(i===undefined){issues.push('MISSING_'+p.id);continue;}
 const old=catalog[i];
 if(Number(old.year)!==p.year||String(old.subject)!==p.subject||Number(old.points||window.NOMUSA_CANONICAL_SELECTION_V1?.items?.[p.id]?.verifiedPointsV18)!==p.points)
  issues.push('YEAR_SUBJECT_POINTS_MISMATCH_'+p.id);
 if(p.action==='KEEP_ALREADY_MATCHES_PDF'){
  if(old.sourceText!==p.sourceText)issues.push('2016_NOT_YET_MATCHING_ORIGINAL');
 } else if(!norm(old.sourceText).includes(norm(p.sourceText).replace(/^문제/,''))) {
  issues.push('OLD_TEXT_NOT_CONTAINING_ORIGINAL_EXAM_QUESTION_'+p.id);
 } else if(old.sourceText===p.sourceText) {
  issues.push('ALREADY_APPLIED_V25_'+p.id);
 }
}
if(issues.length){gateFail(issues);return;}
const rows=[];
for(const p of printed){
 const i=index.get(p.id),old=catalog[i];
 if(p.action==='KEEP_ALREADY_MATCHES_PDF'){
  rows.push(Object.freeze({id:p.id,year:p.year,points:p.points,
    oldChars:old.sourceText.length,newChars:old.sourceText.length,
    changed:false,verdict:'AI_PDF_VISUAL_MATCH_NO_CORRECTION',pdf:p.originalPDF,page:p.page,
    independentProofread:'HOLD'}));continue;
 }
 catalog[i]={...old,sourceText:p.sourceText,sourceTextBeforeV25:old.sourceText,
   sourceReviewV25:Object.freeze({status:'PDF_VISUAL_TRANSCRIBED_AI_REVIEW',
     originalPDF:p.originalPDF,page:p.page,sourceTextBeforePreserved:true,
     independentHumanProofread:'HOLD',expertApproval:'HOLD'}),
   scoringApproved:false};
 rows.push(Object.freeze({id:p.id,year:p.year,points:p.points,
   oldChars:old.sourceText.length,newChars:p.sourceText.length,
   changed:true,verdict:'OCR_FOOTER_AND_SPACING_REMOVED_AI_REVIEW',pdf:p.originalPDF,
   page:p.page,independentProofread:'HOLD'}));
}
window.NOMUSA_V25_MEDIUM_GATE=Object.freeze({
 schema:'NOMUSA_V25_MEDIUM_3_PDF_VISUAL_CROSSCHECK/1',
 status:'PASS_THREE_PRIMARY_PAGE_AI_VISUAL_2_CORRECTED_EXPERT_HOLD',
 count:3,corrected:2,unchanged:1,rows:Object.freeze(rows),
 questionIdsChanged:false,sourcePDFsChanged:false,
 answerTextsChanged:false,learnerStorageKeysChanged:false,
 independentExpertApproved:0,finalApproval:'HOLD',
 mainChanged:false,productionChanged:false,previewDeployed:false
});
})();
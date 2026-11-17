/* NOMUSA V28: 2022-hr-1 source-backed surgical editorial correction.
 * Preserve 327 existing answers and all 328 question IDs, points, local keys.
 * Old Goldstein 'Human Relations' reference is incorrect: 1978 Human Factors.
 * Keep six manager training techniques consistent with existing detailed/compact
 * answer (sixth = action learning), while not changing the problem statement.
 * No professional signoff; only research/editorial draft correction.
 */
(function(){'use strict';
const list=window.N27_CATALOG?.items;
const last=window.NOMUSA_V25_MEDIUM_GATE;
const fail=(why)=>{window.NOMUSA_V28_EDITORIAL_GATE=Object.freeze({
 status:'HOLD_V28_EDITORIAL_PREFLIGHT',issues:why,changed:0,
 independentExpertApproved:0,finalApproval:'HOLD',previewDeployed:false
});};
if(!Array.isArray(list)||!String(last?.status||'').startsWith('PASS_')){
 fail(['V25_GATE_OR_CATALOG_MISSING']);return;
}
const matches=list.map((q,i)=>({q,i})).filter(x=>x.q.id==='2022-hr-1');
if(matches.length!==1){fail(['TARGET_NOT_UNIQUE']);return;}
const item=matches[0],prior=item.q;
if(Number(prior.year)!==2022 || prior.subject!=='인사노무관리론' ||
 Number(prior.points)!==50 || !prior.detailed || !prior.compressed ||
 prior.scoringApproved!==false){
 fail(['TARGET_YEAR_SUBJECT_SCORE_OR_APPROVAL_MISMATCH']);return;
}
const changes=[
 ['Human Relations, 20(2).','Human Factors, 20(2), 131–144.'],
 ['는 Human Relations가 아니라 Human Factors, 20(2), 131–144에 게재되었다.',
  '는 Human Factors, 20(2), 131–144에 게재되었다.'],
 ['이전 V16.2 주석에서 Human Relations로 적은 출판지 표기는 오류이므로 이 교정이 우선한다.',
  '출판사 공식 서지와 네 단계 타당도 용어를 사용하되, 원저 전문의 모든 주장에 대한 검증은 별도로 진행한다.'],
 ['⑥ 경영 시뮬레이션: 시장·재무·인사 의사결정과 피드백을 반복하나 모형의 단순화 한계가 있다.',
  '⑥ 액션러닝: 실제 경영문제를 학습팀이 설계·해결·실행하며 현장 적용을 높일 수 있으나, 후원·실행권한·시간이 부족하면 형식적으로 끝날 수 있다.'],
 ['직무순환·코칭·멘토링·사례연구·역할연기·경영시뮬(각 효과+한계)',
  '직무순환·코칭·멘토링·사례연구·역할연기·액션러닝(각 효과+한계)']
];
const issues=[];
for(const [a,b] of changes){
 const n=prior.detailed.split(a).length-1;
 if(n!==1)issues.push('EXPECTED_EXACTLY_ONCE_'+a.slice(0,45)+'_FOUND_'+n);
}
if(issues.length){fail(issues);return;}
let after=prior.detailed;
for(const [from,to] of changes)after=after.replace(from,to);
if(after.includes('Human Relations')||after.includes('⑥ 경영 시뮬레이션')||
 !after.includes('Human Factors, 20(2), 131–144') ||
 !after.includes('⑥ 액션러닝')||after===prior.detailed){
 fail(['POSTCONDITION_FAILED']);return;
}
list[item.i]={...prior,detailed:after,detailedBeforeV28:prior.detailed,
 editorialReviewV28:Object.freeze({
   source:'https://journals.sagepub.com/doi/10.1177/001872087802000202',
   sourceScope:'PUBLISHER_BIBLIOGRAPHY_AND_ABSTRACT_NOT_FULL_ARTICLE',
   modification:'REMOVE_OLD_JOURNAL_NAME_AND_ALIGN_SIX_TECHNIQUES',
   substantiveExpertApproval:'HOLD',
   independentAcademicProofread:'HOLD',
   previousDraftPreserved:true
 }),
 scoringApproved:false};
window.NOMUSA_V28_EDITORIAL_GATE=Object.freeze({
 schema:'NOMUSA_V28_ONE_2022_HR1_EDITORIAL_CORRECTION/1',
 status:'PASS_GOLDSTEIN_HUMAN_FACTORS_AND_TECHNIQUE_SIX_EDITORIAL_ONLY',
 affected:['2022-hr-1'],count:1,replacements:changes.length,
 beforeChars:prior.detailed.length,afterChars:after.length,
 questionUnchanged:true,compressedAnswerUnchanged:true,
 other327ManuscriptsUnchanged:true,studentKeysChanged:false,
 pdfOriginalsChanged:false,independentExpertApproved:0,
 finalApproval:'HOLD',productionDeployed:false,previewDeployed:false
});
})();
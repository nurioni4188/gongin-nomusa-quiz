/* NOMUSA V28 — surgical correction in CANONICAL ESSAY MODEL.
 * Raw N27_CATALOG stores printed questions, not the detailed model answers.
 * Preserve 328 learner question IDs, Q-Net PDF and local storage keys.
 */
(function(){'use strict';
const model=window.NOMUSA_CANONICAL_SELECTION_V1;
const catalog=window.N27_CATALOG?.items||[];
const gate25=window.NOMUSA_V25_MEDIUM_GATE;
const fail=(why)=>{window.NOMUSA_V28_EDITORIAL_GATE=Object.freeze({
 status:'HOLD_V28_EDITORIAL_PREFLIGHT',issues:why,changed:0,
 independentExpertApproved:0,finalApproval:'HOLD',previewDeployed:false
});};
if(!model?.items||!Array.isArray(catalog)||!String(gate25?.status||'').startsWith('PASS_')){
 fail(['MISSING_CANONICAL_MODEL_CATALOG_OR_V25_GATE']);return;
}
const paper=catalog.filter(q=>q.id==='2022-hr-1');
const before=model.items['2022-hr-1'];
if(paper.length!==1||!before||Number(paper[0].year)!==2022||
 Number(paper[0].points)!==50||paper[0].subject!=='인사노무관리론'||
 !before.detailed||!before.compressed||before.scoringApproved===true ||
 before.detailedBeforeV28||before.compressedBeforeV28){
 fail(['TARGET_YEAR_SUBJECT_SCORE_OR_APPROVAL_MISMATCH']);return;
}
const corrections=[
 ['Human Relations, 20(2).','Human Factors, 20(2), 131–144.'],
 ['는 Human Relations가 아니라 Human Factors, 20(2), 131–144에 게재되었다.',
  '는 Human Factors, 20(2), 131–144에 게재되었다.'],
 ['이전 V16.2 주석에서 Human Relations로 적은 출판지 표기는 오류이므로 이 교정이 우선한다.',
  '출판사 공식 서지와 네 단계 타당도 용어를 사용하되, 원저 전문의 모든 주장에 대한 검증은 별도로 진행한다.'],
 ['⑥ 경영 시뮬레이션: 시장·재무·인사 의사결정과 피드백을 반복하나 모형의 단순화 한계가 있다.',
  '⑥ 액션러닝: 실제 경영문제를 학습팀이 설계·해결·실행하며 현장 적용을 높일 수 있으나, 후원·실행권한·시간이 부족하면 형식적으로 끝날 수 있다.']
];
const compactCorrection=[
 '직무순환·코칭·멘토링·사례연구·역할연기·경영시뮬(각 효과+한계)',
 '직무순환·코칭·멘토링·사례연구·역할연기·액션러닝(각 효과+한계)'
];
const issues=[];
for(const [from] of corrections)
 if(before.detailed.split(from).length-1!==1)issues.push('DETAILED_ANCHOR_MISMATCH_'+from.slice(0,45));
if(before.compressed.split(compactCorrection[0]).length-1!==1)
 issues.push('COMPRESSED_TRAINING_SIX_ANCHOR_MISMATCH');
if(issues.length){fail(issues);return;}
let detailed=before.detailed;
for(const [from,to] of corrections)detailed=detailed.replace(from,to);
const compressed=before.compressed.replace(...compactCorrection);
if(detailed===before.detailed||compressed===before.compressed||
 detailed.includes('Human Relations')||detailed.includes('⑥ 경영 시뮬레이션')||
 compressed.includes('경영시뮬')||
 !detailed.includes('Human Factors, 20(2), 131–144')||
 !detailed.includes('⑥ 액션러닝')||
 !compressed.includes('액션러닝(각 효과+한계)')){
 fail(['GOLDSTEIN_OR_TECHNIQUE_SIX_POSTCONDITION']);return;
}
const patched=Object.freeze({...before,detailed,compressed,
 detailedBeforeV28:before.detailed,compressedBeforeV28:before.compressed,
 sourceBackedEditorialV28:Object.freeze({
  publisher:'https://journals.sagepub.com/doi/10.1177/001872087802000202',
  verification:'PUBLISHER_METADATA_AND_ABSTRACT_ONLY',
  correction:'Human Factors bibliographic name and action-learning training method six',
  fullPaperExpertApproval:'HOLD',humanIndependentProofread:'HOLD'
 }),scoringApproved:false});
const newItems=Object.freeze({...model.items,['2022-hr-1']:patched});
const gate=Object.freeze({
 schema:'NOMUSA_V28_2022_HR1_CANONICAL_DETAIL_CORRECTION/1',
 status:'PASS_GOLDSTEIN_HUMAN_FACTORS_AND_ACTION_LEARNING_CANONICAL_1_ONLY',
 count:1,changeCount:corrections.length+1,editedId:'2022-hr-1',
 sourceQuestionUnchanged:true,pointsUnchanged:true,studentKeyUnchanged:true,
 oldDetailedPreserved:true,oldCompressedPreserved:true,other327Unchanged:true,
 expertApproval:0,independentExpertApproved:0,finalApproval:'HOLD',
 previewDeployed:false,productionChanged:false,mainChanged:false});
window.NOMUSA_CANONICAL_SELECTION_V1=Object.freeze({...model,items:newItems,qualityV28:gate});
window.NOMUSA_V28_EDITORIAL_GATE=gate;
})();
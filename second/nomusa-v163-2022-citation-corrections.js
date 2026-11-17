/* NOMUSA V16.3 — precise historical citation corrections and statutory issue separation.
 * Preserve 2022 IDs, old texts, scoring and saved answers. No deployment.
 */
(function(){'use strict';
const b=window.NOMUSA_CANONICAL_SELECTION_V1;
if(!b?.items){window.NOMUSA_V163_GATE={status:'HOLD_BASE'};return;}
const changes=[
{id:'2022-hr-1',subject:'인사노무관리론',note:'【서지 검증 교정 V16.3】 Goldstein, I. L. (1978), "The Pursuit of Validity in the Evaluation of Training Programs"는 Human Relations가 아니라 Human Factors, 20(2), 131–144에 게재되었다. DOI 10.1177/001872087802000202. 네 단계는 training validity → performance validity → intra-organizational validity → interorganizational validity이다. 이전 V16.2 주석에서 Human Relations로 적은 출판지 표기는 오류이므로 이 교정이 우선한다. 공개 학술지 원문초록 대조 PASS, 원문 전체 및 교육훈련 ROI 출처의 독립 검증 HOLD.',url:'https://journals.sagepub.com/doi/10.1177/001872087802000202'},
{id:'2022-admin-2',subject:'행정쟁송법',note:'【시험일 이전 판례 확인 V16.3】 대법원 2020. 2. 20. 선고 2019두52386 전원합의체는 부당해고 구제신청·재심판정을 다투던 중 정년 또는 계약기간 만료로 원직복직이 불가능해졌어도 해고기간 임금상당액 지급의 구제명령을 구할 실익이 남으면 소의 이익이 유지된다고 판단하였다. 2022. 7. 14. 선고된 대법원 판례는 구제신청 전에 이미 근로관계가 종료된 경우와 구제절차 진행 중 종료된 경우를 구별한다. 이 기출은 금전보상명령을 구한 채 소송계속 중 신설 정년규정이 시행된 상황이므로, 소제기일(2022.7.22)과 개정 시행일(2022.8.1), 근로자의 만60세 도달일(2022.4.15)을 분리하고 구제신청 당시 적법한 근로자 지위·보상구제의 독자성을 확인한다. 판례의 일반적 법리를 사안에 적용할 여지는 크지만 본건과 사실·청구 유형의 완전한 일치 여부는 판결문 전문 검토 HOLD.',url:'https://jifi.scourt.go.kr/portal/news/NewsViewAction.work?gubun=4&seqnum=7000'}
];const n={...b.items},results=[];
for(const v of changes){const o=n[v.id];if(!o||o.year!==2022||o.subject!==v.subject||!o.detailed||o.detailed.includes('【서지 검증 교정 V16.3】')||o.detailed.includes('【시험일 이전 판례 확인 V16.3】')){results.push({id:v.id,status:'HOLD_ID_OR_DUPLICATE'});continue;}n[v.id]=Object.freeze({...o,detailed:o.detailed+'\n\n'+v.note,detailedBeforeV163:o.detailed,sourceCorrectionsV163:[v.url],finalAcademicApproval:'HOLD',scoringApproved:false});results.push({id:v.id,status:'SOURCE_CORRECTED_FINAL_HOLD',originalPreserved:true});}
const gate=Object.freeze({status:results.length===2&&results.every(x=>x.status==='SOURCE_CORRECTED_FINAL_HOLD')?'TWO_CITATIONS_CORRECTED_HOLD':'PARTIAL_HOLD',rows:results,finalApproval:'HOLD',productionMutated:false,previewDeployed:false});window.NOMUSA_CANONICAL_SELECTION_V1=Object.freeze({...b,items:Object.freeze(n),qualityV163:gate});window.NOMUSA_V163_GATE=gate;
})();
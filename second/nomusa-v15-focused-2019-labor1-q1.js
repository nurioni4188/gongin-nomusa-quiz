/* V15 2019 노동법Ⅰ 50점 1문: 원문 사실과 시험 이전 판례에 기초한 보충 논증.
 * 이전 상세/압축답안 및 원장 ID·배점·저장키 보존, 내용 최종승인 HOLD.
 */
(function () {
'use strict';
const id='2019_p5_q1', b=window.NOMUSA_CANONICAL_SELECTION_V1, old=b?.items?.[id];
const stop=status=>{window.NOMUSA_V15_FOCUSED_CASE_GATE=Object.freeze({status,id});};
if(!old?.detailed?.includes('2019 노동법(1교시) 문제1')||!old.compressed?.includes('사이닝보너스'))return stop('HOLD_SOURCE_MISMATCH');
const a1='Ⅳ. 소결\nA회사의 선정기준',a2='Ⅳ. 소결\n사이닝보너스는';
if(!old.detailed.includes(a1)||!old.detailed.includes(a2))return stop('HOLD_ANCHOR_MISMATCH');
const supplement1=[
'4. 선정기준 설정과 실제 적용의 단계적 심사',
'근로기준법 제24조의 정리해고 요건 중 이 물음은 대상자 선정의 합리성·공정성만을 다룬다. 경영상 필요가 있다는 사정만으로 선정기준의 공정성이 자동으로 인정되지는 않는다. 반대로 근무태도와 같은 주관적 요소가 있다는 이유만으로 반드시 위법한 것도 아니다.',
'대법원 2012. 5. 24. 선고 2011두11310 판결은 객관적 합리성과 사회적 상당성을 가진 기준의 설정뿐 아니라 그 기준의 실질적 공정한 적용을 요구한다. 이에 따라 첫째 기준의 설계, 둘째 실제 대상자 선정을 구분해 논증해야 한다.',
'설계 측면에서 근무태도평가 40점은 노동자의 업무상 책임감 등을 평가할 수 있으나, 근거·평가자 편차 통제 장치가 중요하다. 근속·부양가족 30점을 포함했다는 사용자 반론이 가능하지만 사회경제적 보호요소가 형식적으로 존재한다는 점만으로 주관평가의 영향이 상쇄되는 것은 아니다.',
'적용 측면에서 해고자 12명 중 10명이 객관 항목 상위권이면서 주관평가 최하위권이고, 잔존자 12명은 반대인 결과의 역전을 구체적인 판단 자료로 제시해야 한다. 다만 점수 역전만으로 개별 평가가 허위였다고 단정하기보다는 각 평가의 객관적 근거와 절차를 사용자에게 요구하는 논증이 더 엄밀하다. 제공된 사실관계에서는 이 같은 근거가 제시되지 않았으므로 대상자 선정의 합리성·공정성이 인정되기 어렵다.'
].join('\n')+'\n\n';
const supplement2=[
'4. 계약해석과 청구원인별 검토',
'대법원 2015. 6. 11. 선고 2012다55518 판결은 사이닝보너스가 단순 이직·계약체결 대가인지 전속근무와 임금 선급의 성격도 갖는지를 지급 동기·경위, 계약 목적과 당사자 의사, 조건부 지급 또는 반환 문언, 거래관행으로 판단한다. 따라서 7년 고용보장 문구만으로 7년간 근무할 의무나 전액 반환의무를 도출할 수 없다.',
'반환청구의 판단에서는 금원 자체가 어떠한 반대급부에 대응하는지 먼저 보아야 한다. 입사·계약체결의 대가라면 근로자가 입사해 근무를 시작함으로써 그 반대급부가 실현된다. 손해배상청구는 별도로 전속근무 의무의 존재, 위반, 손해 및 인과관계를 논증해야 하며, 조기퇴직 사실만으로 모두 충족되는 것이 아니다.',
'사용자는 고액의 지급과 단기 퇴사에 비추어 장기근속 약정이 있었을 것이라고 반론할 수 있다. 그러나 본 사례에 제시된 계약문언과 7년이라는 기간을 정한 경위는 그 주장을 충분히 뒷받침하지 못한다. 가령 별도 명시적 반환조항이 있는 사안이라면 그 약정의 성격과 근로기준법 제20조의 제한을 추가 검토해야 하나, 현재 사안에는 그 문언이 없다. 따라서 반환·손해배상청구 모두 인정하기 어렵다.'
].join('\n')+'\n\n';
const detailed=old.detailed.replace(a1,supplement1+a1).replace(a2,supplement2+a2);
const compressed=old.compressed.replace('Ⅳ. 결론: 합리성·공정성 결여, 甲의 주장 타당.','Ⅳ. 결론: 2011두11310의 기준 설정·실질 적용의 2단계 심사상, 주관평가 40점의 영향과 결과 역전, 평가 근거 부족을 종합하면 합리성·공정성이 인정되기 어렵다. 甲의 주장 타당.')
.replace('Ⅳ. 결론: 반환의무 없음, A회사의 청구는 타당하지 않다.','Ⅳ. 결론: 계약 문언·지급동기·당사자 의사상 입사 대가로 보아 반환의무 없음(2012다55518). 단순 조기퇴직만으로 별도 손해배상도 성립하지 않는다.');
if(detailed===old.detailed||compressed===old.compressed)return stop('HOLD_UNCHANGED');
const updated=Object.freeze({...old,detailed,compressed,detailedBeforeV15:old.detailed,compressedBeforeV15:old.compressed,finalAcademicApproval:'HOLD',scoringApproved:false,paperPagesVerified:false});
const items=Object.freeze({...b.items,[id]:updated});
const gate=Object.freeze({status:'DRAFT_SUBSTANTIVELY_ENHANCED_CONTENT_HOLD',id,year:2019,pointsVerifiedFromV12:50,parts:[25,25],beforeChars:old.detailed.length,afterChars:detailed.length,
precedents:['2011두11310','2012다55518'],sourceTextStatus:'V12_REPOSITORY_PDF_TEXT',officialFullTextIndependentApproval:'HOLD',
handwritingPageCount:'HOLD',catalogChanged:false,storageKeyChanged:false,previewDeployed:false});
window.NOMUSA_CANONICAL_SELECTION_V1=Object.freeze({...b,items,qualityV15Focused:gate});
window.NOMUSA_V15_FOCUSED_CASE_GATE=gate;
})();
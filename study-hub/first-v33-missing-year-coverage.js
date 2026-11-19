/* NOMUSA FIRST V33 · original source-only year inventory, not a question bank.
   2013/16/18/20/21 have 300 A+B answer CANDIDATES each; no rendered
   question text in RC35; never insert blank/guessed questions into QDATA.
*/
(function(){
  'use strict';
  const absent=Object.freeze([
    {year:2013, candidateA:150,candidateB:150,officialBookletIndexed:false,sourceNote:'정답표 A·B형 보유 · 문제지 원본 연결 미완료'},
    {year:2016, candidateA:150,candidateB:150,officialBookletIndexed:false,sourceNote:'정답표 A·B형·기존 문제지 파일명 보유 · 본문/쪽수 미연결'},
    {year:2018, candidateA:150,candidateB:150,officialBookletIndexed:false,sourceNote:'정답표 A·B형·기존 ZIP 파일명 보유 · 본문/쪽수 미연결'},
    {year:2020, candidateA:150,candidateB:150,officialBookletIndexed:true,sourceNote:'Q-Net A·B 문제지 PDF·정답표 연결 · 전체 지문 검증 대기'},
    {year:2021, candidateA:150,candidateB:150,officialBookletIndexed:true,sourceNote:'Q-Net A·B 문제지 PDF·정답표 연결 · 전체 지문 검증 대기'}
  ].map(row=>Object.freeze({...row,scoringApproved:false,actualRenderedQuestions:0})));
  const partial=Object.freeze({2010:25,2011:1,2012:1,2017:6,2019:8});
  window.NOMUSA_FIRST_V33_COVERAGE=Object.freeze({
    schema:'NOMUSA_FIRST_V33_PRIOR_WORK_GAP_GATE/1',
    range:[2008,2026],
    missingYears:absent,
    partialYearMissingA:partial,
    candidateYearTotal:1500,
    candidateRecordTotal:3400,
    originalIndexedSourceRecords:900,
    registeredLegacyQuestions:1259,
    originalRC35Questions:1020,
    totalRenderedQuestions:2279,
    partialUnrenderedQuestionsA:41,
    fullMissingUnrenderedQuestionsA:750,
    scoringPromoted:0
  });
})();
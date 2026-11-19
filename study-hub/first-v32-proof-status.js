/* NOMUSA FIRST V32 — evidence-aware badges, no scoring promotion.
 * Reuse immutable V61 Q-Net source ledger and V62/V71 prior examination.
 * PDF page location is not full question/stem/formula proofreading.
 * 2020/2021 answer grid image comparison is not expert approval.
 */
(function(){
  'use strict';
  const V62 = Object.freeze({
    'legacy1-2020-A-labor1-013': [5,4],
    'legacy1-2021-A-economics-113': [36,36],
    'legacy1-2021-B-economics-111': [36,36]
  });
  const V71 = Object.freeze({
    'legacy1-2020-A-civil-072':24,
    'legacy1-2020-A-civil-075':25,
    'legacy1-2020-A-social-078':26,
    'legacy1-2020-A-economics-114':36,
    'legacy1-2020-B-labor1-004':3,
    'legacy1-2020-B-labor1-005':3,
    'legacy1-2020-B-labor1-006':3,
    'legacy1-2020-B-labor1-010':4,
    'legacy1-2020-B-labor2-036':12,
    'legacy1-2020-B-civil-075':25,
    'legacy1-2020-B-social-078':26,
    'legacy1-2020-B-management-112':34,
    'legacy1-2020-B-management-117':35,
    'legacy1-2021-A-management-102':34
  });
  const specials=new Set([
    'legacy1-2021-A-labor2-026','legacy1-2021-A-civil-070',
    'legacy1-2021-B-labor2-026','legacy1-2021-B-civil-072'
  ]);
  const requiredFields = ['source','answerSource','answerPdfPage','status'];
  const classify = function(id) {
    const sources=window.NOMUSA_FIRST_V61_SOURCES;
    const rec=sources&&sources.records&&sources.records[id];
    if(!rec) return Object.freeze({
      sourceStatus:'원전 개별연결 대기', answerStatus:'정답 후보',
      sourceKind:'MISSING', answerKind:'CANDIDATE', scoringApproved:false,
      pdfPage:null, printedPage:null, exactQuestionVisuallyProofread:false,
      fullAnswerKeyHumanApproved:false
    });
    const year=Number(id.split('-')[1]);
    const v62=V62[id],v71=V71[id];
    let sourceStatus,sourceKind;
    if(v62){
      sourceKind='PDF_PAGE_VISUAL_V62';
      sourceStatus='PDF 위치·인쇄쪽 확인';
    }else if(Number.isInteger(v71)){
      sourceKind='PDF_PAGE_VISUAL_V71';
      sourceStatus='PDF 문항번호 시각확인';
    }else if(rec.status==='TEXT_AND_FIVE_MARKERS'){
      sourceKind='PDF_TEXT_FIVE_MARKERS';
      sourceStatus='PDF 텍스트 위치 연결';
    }else if(rec.status==='OCR_PAGE_CANDIDATE'){
      sourceKind='PDF_OCR_CANDIDATE';
      sourceStatus='PDF 위치 자동판독 후보';
    }else{
      sourceKind='PDF_PAGE_HOLD';
      sourceStatus='PDF 쪽수 미확정';
    }
    const answerKind=(year===2020||year===2021)?
      (specials.has(id)?'GRID_2021_SPECIAL_VISUALLY_CHECKED':'GRID_2020_21_AUTOMATED_IMAGE_MATCH'):
      'OFFICIAL_PDF_LINK_ONLY';
    const answerStatus=answerKind==='GRID_2021_SPECIAL_VISUALLY_CHECKED'?
      '정답표 특수셀 시각대조':answerKind==='GRID_2020_21_AUTOMATED_IMAGE_MATCH'?
      '정답표 이미지 자동대조':'정답 PDF 연결·추가검증';
    return Object.freeze({
      sourceStatus,answerStatus,sourceKind,answerKind,scoringApproved:false,
      pdfPage:v62?v62[0]:Number.isInteger(v71)?v71:rec.pdfPage||null,
      printedPage:v62?v62[1]:rec.printedPage||null,
      exactQuestionVisuallyProofread:false,
      fullAnswerKeyHumanApproved:false,
      originalSourceStatus:rec.status,
      originalAnswerSource:rec.answerSource
    });
  };
  window.NOMUSA_FIRST_V32_STATUS=Object.freeze({
    schema:'NOMUSA_FIRST_V32_UI_EVIDENCE/1',
    v62PageIds:Object.freeze(Object.keys(V62)),
    v71PageIds:Object.freeze(Object.keys(V71)),
    specials:Object.freeze([...specials]),
    classify,
    counts:Object.freeze({
      answerCandidateRecords:3400,
      independentScoringApproved:0,
      originalBookletsLinked:900,
      originalPdfTextMarkers:300,
      originalOcrCandidates:556,
      originalPageHold:44,
      visuallyConfirmedV62:3,
      visuallyConfirmedV71:14,
      officialAnswerCells2020to2021ImageCompared:600,
      manuallyVisuallyComparedSpecialCells:4
    })
  });
})();
/* Full 2008-2026 first-stage and 2007-2026 second-stage catalog expansion.
 * This is an index, not a claim that source documents, answer keys or academic
 * content are independently approved. Never turn legacy answer candidates into keys. */
window.NOMUSA_COMPLETE_LOAD = async function(){
  'use strict';
  const paths={
    first103:'/review/NOMUSA_FIRST_V43_103_SECOND_PASS_515_CHOICES_AND_LAW_QA_20261118.json',
    first686:'/review/NOMUSA_FIRST_V54_686_UNIFIED_PRIMARY_SOURCE_LEDGER_20261118.json',
    essay328:'/review/NOMUSA_V23_VALIDATION_LEDGER.json',
    laneA1:'/review/NOMUSA_FIRST_V80_LANE_A_BATCH1_25Q_LABOR_LAW_20261119.json'
  };
  const failures=[];
  const fetchJSON=async path=>{
    try{
      const r=await fetch(path,{cache:'no-store'});
      if(!r.ok)throw Error('HTTP '+r.status);
      return await r.json();
    }catch(err){failures.push(path+': '+err.message);return null}
  };
  const [a,b,c,laneA1]=await Promise.all([fetchJSON(paths.first103),fetchJSON(paths.first686),fetchJSON(paths.essay328),fetchJSON(paths.laneA1)]);
  if(!Array.isArray(a?.rows)||a.rows.length!==103)failures.push('103 원장 행수 불일치');
  if(!Array.isArray(b?.rows)||b.rows.length!==686)failures.push('686 원장 행수 불일치');
  if(!Array.isArray(c?.rows)||c.rows.length!==328)failures.push('328 원장 행수 불일치');
  if(!Array.isArray(laneA1?.rows)||laneA1.rows.length!==25)failures.push('V80 Lane A 1차 배치(25문항) 원장 행수 불일치');
  // Overlay only: never mutates the 686 ledger itself, only supplies transcribed
  // stem/options/reasoned-candidate content for rows whose id matches.
  const laneA1ById=new Map((laneA1?.rows||[]).filter(row=>typeof row?.id==='string').map(row=>[row.id,row]));
  const sourcePaths=[...new Set((a?.rows||[]).map(row=>row.originalRecord).filter(path=>/^review\/[A-Za-z0-9_./-]+\.json$/.test(path)))];
  const sources=await Promise.all(sourcePaths.map(async path=>[path,await fetchJSON('/'+path)]));
  const sourceById=new Map();
  const findRows=x=>{
    if(Array.isArray(x))return x;
    if(!x||typeof x!=='object')return [];
    for(const key of ['rows','records','items','questions','drafts']){
      if(Array.isArray(x[key]))return x[key];
    }
    return [];
  };
  for(const [path,data] of sources){
    for(const row of findRows(data)){
      const id=row.id||row.questionId||row.k;
      if(typeof id==='string')sourceById.set(id,{...row,_sourcePath:path});
    }
  }
  const take=(o,names)=>names.find(k=>typeof o?.[k]==='string'&&o[k].trim())||'';
  const val=(o,names)=>{
    for(const key of names)if(o?.[key]!=null&&typeof o[key]==='string')return o[key];
    return '';
  };
  const five=o=>{
    for(const key of ['options','optionTexts','allFiveOptionsFromImageDraft','originalFiveOptionsDraft','sourceFiveOptionsDraft','choices','o','allFiveChoices']){
      if(Array.isArray(o?.[key])&&o[key].length===5)return o[key].map(v=>typeof v==='string'?v:String(v?.text||v?.option||''));
    }
    return [];
  };
  const first=[];
  for(const row of (a?.rows||[])){
    const src=sourceById.get(row.id)||{};
    const stem=val(src,['question','exactStemFromImageDraft','exactOriginalStemDraft','sourceStemDraft','stem','sourceText','questionText','q','questionStem']);
    const opts=five(src);
    first.push({
      k:row.id,y:row.year,s:row.subject||src.subject||'',n:Number(src.questionNumber||String(row.id).split('-').pop())||null,
      q:stem,o:opts,a:[],form:'A',
      fullStage:'source103',provisional:!stem||opts.length!==5,
      sourceOriginal:row.originalRecord||'',sourceCrop:val(src,['sourceImage','sourceCropImage','originalCropImage']),
      sourceEvidence:row.explanationEvidence||'',originalPage:src.sourcePdfPage||src.officialPDFPage||src.originalPage||null,
      learningExplanationDraft:val(src,['explanationDraft','detailedExplanationDraft','substantiveLawExplanationDraft','lawExplanationDraft','legalExplanationDraft']),
      learningOptionNotes:(Array.isArray(src.optionExplanations)?src.optionExplanations:Array.isArray(src.eachOptionExplanation)?src.eachOptionExplanation:[]).slice(0,5),
      sourceReviewStatus:'103 원문·선택지 교열 대기 · 정답/해설 승인 HOLD'
    });
  }
  for(const row of (b?.rows||[])){
    const laneA=laneA1ById.get(row.id)||null;
    const laneAOpts=laneA&&Array.isArray(laneA.originalFiveOptionsDraft)&&laneA.originalFiveOptionsDraft.length===5?laneA.originalFiveOptionsDraft:[];
    first.push({
      k:row.id,y:row.year,s:row.subject,n:row.questionNumber,
      q:laneA?.exactStemFromImageDraft||'',o:laneAOpts,
      // Reasoned candidate from independent statute-text analysis, NOT an official
      // key. chk/sourceReviewStatus below deliberately do NOT say MATCH/CHECKED,
      // so confirmKey() in app.js keeps this hidden behind the HOLD gate.
      a:laneA&&Number.isInteger(laneA.reasonedCandidateAnswer)?[laneA.reasonedCandidateAnswer]:[],
      form:'A',
      fullStage:'source686',provisional:!laneA,
      visuallyTranscribedFromCrop:!!laneA,
      reasonedConfidence:laneA?.reasonedConfidence||null,
      learningExplanationDraft:laneA?.explanationDraft||'',
      learningOptionNotes:Array.isArray(laneA?.optionExplanations)&&laneA.optionExplanations.length===5?laneA.optionExplanations:[],
      sourceOriginal:paths.first686.slice(1),
      sourceCrop:row.originalCropProvisional?.path||'',
      sourceCropSHA:row.originalCropProvisional?.sha256||'',
      sourceOfficialURL:row.officialAFormOriginalBooklet?.officialQNetSourceURL||row.knownQNetNoticeOrOriginalURL||'',
      sourceOfficialSHA:row.officialAFormOriginalBooklet?.officialSourcePdfSha256||'',
      sourceOfficialGroup:row.officialAFormOriginalBooklet?.sourceGroup||'',
      sourcePageCandidate:Number.isInteger(row.officialAFormOriginalBooklet?.candidateOriginalPDFPage)&&
        row.officialAFormOriginalBooklet.candidateOriginalPDFPage>0?row.officialAFormOriginalBooklet.candidateOriginalPDFPage:null,
      sourcePageIndependentlyVerified:row.independentQuestionNumberAndOriginalPDFPageProof===true,
      sourceCandidateURL:row.thirdPartyMirrorOnly?.candidateURL||'',
      sourceEvidence:row.knownQNetNoticeOrOriginalURL||'',
      sourceReviewStatus:laneA?'VISUALLY_TRANSCRIBED_REASONED_CANDIDATE_OFFICIAL_KEY_CROSSCHECK_PENDING':(row.sourceGrade||'원문·5개 선택지·정답 검증 필요')
    });
  }
  // Original authored records take priority in the caller; 328 ledger provides
  // stable ID, source provenance and writing entry points, not fabricated text.
  const essay=(c?.rows||[]).map(row=>({
    id:row.id,year:row.year,subject:row.subject,points:row.points,
    topic:'원문 연결 점검 · '+row.id,
    sourceText:'',sections:[],
    origin:'V23_LEDGER_SOURCE_ONLY',sourceOnly:true,
    sourceFile:row.source?.repoFile||'',sourceUrl:row.source?.qnetPostUrl||'',
    answerStatus:'HOLD_INDEPENDENT_EXPERT_APPROVAL',
    fullStage:'ledger328'
  }));
  return Object.freeze({
    first,essay,failures,
    report:{expectedFirstMissing:789,first103:(a?.rows||[]).length,first686:(b?.rows||[]).length,
      essay328:(c?.rows||[]).length,sourceFileCount:sourcePaths.length,
      first686VisuallyTranscribedBatchV80LaneA1: first.filter(x=>x.fullStage==='source686' && x.visuallyTranscribedFromCrop).length,
      first686ProvisionalCrop: first.filter(x=>x.fullStage==='source686' && !!x.sourceCrop).length,
      first686WithOfficialBooklet: (b?.rows||[]).filter(x=>x.sourceGrade==='OFFICIAL_QNET_A_PDF_AT_BOOKLET_LEVEL').length,
      first686ThirdPartyOnly: (b?.rows||[]).filter(x=>x.sourceGrade==='THIRD_PARTY_2013_MIRROR_ONLY_HOLD').length,
      first686NoVerifiedOfficialA: (b?.rows||[]).filter(x=>x.sourceGrade==='NO_VERIFIED_OFFICIAL_A_PDF_HOLD').length,
      firstOfficialOriginalFileIntegrityProved: first.filter(x=>x.fullStage==='source686'&&window.NOMUSA_QNET_SOURCE_AUDIT?.[x.sourceOfficialSHA]?.integrity==='SHA256_MATCH').length,
      originalPDFsSHAConfirmed: Object.values(window.NOMUSA_QNET_SOURCE_AUDIT||{}).filter(x=>x.integrity==='SHA256_MATCH').length,
      originalPDFPageCandidate169:first.filter(x=>x.fullStage==='source686'&&
        Number.isInteger(x.sourcePageCandidate)&&
        x.sourcePageCandidate<=Number(window.NOMUSA_QNET_SOURCE_AUDIT?.[x.sourceOfficialSHA]?.pdfPageCount||0)).length,
      sourcePageCandidateOutOfRange:first.filter(x=>x.fullStage==='source686'&&
        Number.isInteger(x.sourcePageCandidate)&&
        x.sourcePageCandidate>Number(window.NOMUSA_QNET_SOURCE_AUDIT?.[x.sourceOfficialSHA]?.pdfPageCount||0)).length,
      originalStems103:first.filter(x=>x.fullStage==='source103'&&!!x.q).length,
      fiveOptions103:first.filter(x=>x.fullStage==='source103'&&x.o.length===5).length,
      textExplanationDraft103:first.filter(x=>x.fullStage==='source103'&&x.learningExplanationDraft).length,
      fiveOptionLearningReasonDraft103:first.filter(x=>x.fullStage==='source103'&&x.learningOptionNotes?.length===5).length}
  });
};
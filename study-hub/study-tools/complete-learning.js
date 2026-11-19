/* Full 2008-2026 first-stage and 2007-2026 second-stage catalog expansion.
 * This is an index, not a claim that source documents, answer keys or academic
 * content are independently approved. Never turn legacy answer candidates into keys. */
window.NOMUSA_COMPLETE_LOAD = async function(){
  'use strict';
  const paths={
    first103:'/review/NOMUSA_FIRST_V43_103_SECOND_PASS_515_CHOICES_AND_LAW_QA_20261118.json',
    first686:'/review/NOMUSA_FIRST_V54_686_UNIFIED_PRIMARY_SOURCE_LEDGER_20261118.json',
    essay328:'/review/NOMUSA_V23_VALIDATION_LEDGER.json'
  };
  const failures=[];
  const fetchJSON=async path=>{
    try{
      const r=await fetch(path,{cache:'no-store'});
      if(!r.ok)throw Error('HTTP '+r.status);
      return await r.json();
    }catch(err){failures.push(path+': '+err.message);return null}
  };
  const [a,b,c]=await Promise.all([fetchJSON(paths.first103),fetchJSON(paths.first686),fetchJSON(paths.essay328)]);
  if(!Array.isArray(a?.rows)||a.rows.length!==103)failures.push('103 원장 행수 불일치');
  if(!Array.isArray(b?.rows)||b.rows.length!==686)failures.push('686 원장 행수 불일치');
  if(!Array.isArray(c?.rows)||c.rows.length!==328)failures.push('328 원장 행수 불일치');
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
    for(const key of ['options','optionTexts','allFiveOptionsFromImageDraft','choices','o','allFiveChoices']){
      if(Array.isArray(o?.[key])&&o[key].length===5)return o[key].map(v=>typeof v==='string'?v:String(v?.text||v?.option||''));
    }
    return [];
  };
  const first=[];
  for(const row of (a?.rows||[])){
    const src=sourceById.get(row.id)||{};
    const stem=val(src,['question','exactStemFromImageDraft','stem','sourceText','questionText','q','questionStem']);
    const opts=five(src);
    first.push({
      k:row.id,y:row.year,s:row.subject||src.subject||'',n:Number(src.questionNumber||String(row.id).split('-').pop())||null,
      q:stem,o:opts,a:[],form:'A',
      fullStage:'source103',provisional:!stem||opts.length!==5,
      sourceOriginal:row.originalRecord||'',sourceCrop:val(src,['sourceImage','sourceCropImage','originalCropImage']),
      sourceEvidence:row.explanationEvidence||'',originalPage:src.sourcePdfPage||src.officialPDFPage||src.originalPage||null,
      sourceReviewStatus:'103 원문·선택지 교열 대기 · 정답/해설 승인 HOLD'
    });
  }
  for(const row of (b?.rows||[])){
    first.push({
      k:row.id,y:row.year,s:row.subject,n:row.questionNumber,
      q:'',o:[],a:[],form:'A',
      fullStage:'source686',provisional:true,
      sourceOriginal:paths.first686.slice(1),sourceCrop:row.originalCropProvisional||'',
      sourceEvidence:row.knownQNetNoticeOrOriginalURL||row.officialAFormOriginalBooklet||'',
      sourceReviewStatus:row.sourceGrade||'원문·5개 선택지·정답 검증 필요'
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
      originalStems103:first.filter(x=>x.fullStage==='source103'&&!!x.q).length,
      fiveOptions103:first.filter(x=>x.fullStage==='source103'&&x.o.length===5).length}
  });
};
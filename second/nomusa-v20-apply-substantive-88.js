/* NOMUSA V20 — apply 88 source-specific supplemental draft paragraphs.
 * Scope: existing canonical learning-draft model only. No original questions, storage keys,
 * official approval, scoring, or deployment. Fail closed if a source ID or score is different.
 */
(function(){'use strict';
const c=window.NOMUSA_CANONICAL_SELECTION_V1;
const input=[...(window.NOMUSA_V20_50||[]),...(window.NOMUSA_V20_25_A||[]),...(window.NOMUSA_V20_25_B||[])];
const fail=(code)=>{window.NOMUSA_V20_CONTENT_GATE=Object.freeze({status:'HOLD_'+code,expected:88,received:input.length,contentApproval:'HOLD',deployment:false});};
if(!c?.items||input.length!==88||!window.NOMUSA_V181_ECON_GATE){fail('BASE_OR_COUNT');return;}
const catalog=new Map((window.N27_CATALOG?.items||[]).map(q=>[q.id,q]));
const index=new Map(), issues=[];
for(const x of input){
  if(index.has(x.id))issues.push('DUPLICATE_'+x.id);
  index.set(x.id,x);
  const q=c.items[x.id], src=catalog.get(x.id);
  if(!q||!q.detailed||!q.compressed||!(src?.sourceText||q.sourceText)){
    issues.push('NO_SOURCE_OR_ANSWER_'+x.id);continue;
  }
  const p=Number(q.verifiedPointsV18||src?.points);
  if(![25,50].includes(p))issues.push('INVALID_POINT_'+x.id+'_'+p);
  if((window.NOMUSA_V20_50||[]).includes(x)&&p!==50)issues.push('FIFTY_SCORE_'+x.id);
  if((window.NOMUSA_V20_25_A||[]).includes(x)&&p!==25)issues.push('TWENTYFIVE_SCORE_'+x.id);
  if((window.NOMUSA_V20_25_B||[]).includes(x)&&p!==25)issues.push('TWENTYFIVE_SCORE_'+x.id);
  if(x.analysis.length<180||x.compact.length<15)issues.push('SUBSTANCE_TOO_SHORT_'+x.id);
  if(q.detailedBeforeV20||q.compressedBeforeV20)issues.push('PREVIOUSLY_APPLIED_'+x.id);
  if(q.scoringApproved)issues.push('UNEXPECTED_APPROVAL_'+x.id);
}
if(index.size!==88||issues.length){window.NOMUSA_V20_CONTENT_GATE=Object.freeze({
 status:'HOLD_SOURCE_MISMATCH',issues:Object.freeze(issues),expected:88,received:input.length,contentApproval:'HOLD',deployment:false});return;
}
const updated={...c.items},rows=[];
for(const x of input){
  const q=updated[x.id],p=Number(q.verifiedPointsV18||catalog.get(x.id)?.points);
  const detail='\n\n## V20 원문 연동 심화논증 — '+x.topic+' ('+p+'점)\n\n'+x.analysis+
   '\n\n> 검토 상태: 학습용 내용보강. 시험연도 법령·판례·학술 원전 독립검토, 실제 수기분량 및 전문가 승인 HOLD.';
  const compact='\n\n[V20 추가 핵심] '+x.compact;
  const after=q.detailed+detail,compressed=q.compressed+compact;
  updated[x.id]=Object.freeze({...q,detailed:after,compressed:compressed,
    detailedBeforeV20:q.detailed,compressedBeforeV20:q.compressed,
    v20SpecificTopic:x.topic,v20SubstantiveSupplement:x.analysis,
    contentStatus:'SOURCE_SPECIFIC_DRAFT_SUPPLEMENT_APPROVAL_HOLD',
    handwrittenPages:'HOLD',finalAcademicApproval:'HOLD',scoringApproved:false});
  rows.push(Object.freeze({id:x.id,year:q.year,subject:q.subject,points:p,
    previousDetailedChars:q.detailed.length,addedDetailedChars:detail.length,
    currentDetailedChars:after.length,compressedAddedChars:compact.length,
    preserved:true,contentApproval:'HOLD'}));
}
const points50=rows.filter(r=>r.points===50).length,points25=rows.filter(r=>r.points===25).length;
if(points50!==32||points25!==56){fail('POINT_COUNT');return;}
const gate=Object.freeze({schema:'nomusa-v20-substantive-supplements/1',
 status:'88_SOURCE_SPECIFIC_SUPPLEMENTS_ADDED_CONTENT_APPROVAL_HOLD',
 total:88,points50,points25,
 rows:Object.freeze(rows),legalAcademicApproval:'HOLD',
 originalPaperVisualReview:'HOLD',handwrittenPages:'HOLD',expertApproval:'HOLD',
 storageKeysChanged:false,originalCatalogChanged:false,mainChanged:false,productionChanged:false,previewDeployed:false});
window.NOMUSA_CANONICAL_SELECTION_V1=Object.freeze({...c,items:Object.freeze(updated),qualityV20:gate});
window.NOMUSA_V20_CONTENT_GATE=gate;
})();
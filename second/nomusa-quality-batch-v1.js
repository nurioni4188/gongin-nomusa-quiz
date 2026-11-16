/* NOMUSA 20YEAR QUALITY BATCH V1: source-derived draft extension.
 * Never changes original catalog items, PDFs, question IDs, points, storage keys, scoring status or approvals.
 * This is NOT independent academic/legal verification or a handwriting-page certification. */
(function(){'use strict';
 const current=window.NOMUSA_CANONICAL_SELECTION_V1;
 const catalog=window.N27_CATALOG;
 if(!current||!catalog||current.gate?.catalogCount!==377||
    current.gate?.candidateCount!==328||current.gate?.uniqueIds!==true) {
   window.NOMUSA_20YEAR_QUALITY_BATCH_V1=Object.freeze({status:'HOLD_REGISTRY_MISMATCH'});return;
 }
 const records=new Map(catalog.items.map(r=>[r.id,r]));
 const clean=x=>String(x==null?'':x).replace(/\\r\\n|\\n|\\r/g,'\n').trim();
 const flat=x=>clean(x).replace(/[\s.,，·:;()\[\]ⅠⅡⅢⅣⅤⅥⅦⅧ\-]/g,'');
 const normalizeSubject=s=>/노동법/.test(s)?'노동법':/행정쟁송/.test(s)?'행정쟁송법':/민사소송/.test(s)?'민사소송법':/노동경제/.test(s)?'노동경제학':/인사노무/.test(s)?'인사노무관리론':'경영조직론';
 const numericPoints=p=>Number.isFinite(Number(p))&&Number(p)>0?Number(p):null;
 const target=p=>p>=50?1400:p>=30?1100:p>=25?950:p>=20?760:p>=15?620:p>=12?530:p>=10?440:310;
 const blacklist=/^(?:Ⅰ|Ⅱ|Ⅲ|Ⅳ|Ⅴ|Ⅵ|Ⅶ|Ⅷ|Ⅸ|Ⅹ)[.．\s]|^(?:제\d+[장절]|[0-9]{1,2}[.．]\s*[^.!?]{0,55}$)/;
 const stop=new Set(['하시오','대하여','관하여','설명하시오','다음','문제','설명','논하시오','검토하시오','대상','근거','내용','경우','것이다','여부','대한','있다']);
 function qWords(r) {
   const s=String(r.topic||'')+' '+String(r.sourceText||'').slice(-2000);
   return [...new Set(s.match(/[가-힣]{3,}/g)||[])].filter(w=>!stop.has(w)&&w.length<18).slice(0,80);
 }
 function overlap(a,b) {
   const x=flat(a),y=flat(b);if(!x||!y)return 0;
   if(x.includes(y)||y.includes(x))return 1;
   let hit=0,total=0,seen=new Set();
   for(let i=0;i<x.length-7;i+=6){const seg=x.slice(i,i+8);if(seen.has(seg))continue;seen.add(seg);total++;if(y.includes(seg))hit++;}
   return total?hit/total:0;
 }
 function chunks(raw,terms,subject) {
   const out=[];let i=0;
   for(const line of clean(raw).split(/\n+/)){
     const s=line.trim();i++;
     if(s.length<75||s.length>1100||blacklist.test(s))continue;
     if(/(?:공식 모범답안|자동작성 틀|검증이 필요|원본 확인 필요|분량 검증 HOLD)/.test(s))continue;
     let score=0;
     for(const w of terms){if(s.includes(w))score+=2;if(score>=16)break;}
     if(/대법원|판례|제\d+조|요건|예외|위법|재량|처분/.test(s))score+=/노동법|행정쟁송|민사소송/.test(subject)?4:1;
     if(/학자|이론|모형|연구|분석|효과|한계|전략|절차|관리|가정|조건/.test(s))score+=2;
     if(/[A-Za-z]{4,}/.test(s))score+=1;
     if(s.length>=100&&s.length<=460)score+=2;
     out.push({s,score,i});
   }
   return out;
 }
 const next={};const audit=[];const statuses={};
 for(const [id,original] of Object.entries(current.items)){
   const r=records.get(id),p=numericPoints(r?.points),category=normalizeSubject(r?.subject||'');
   const existing=clean(original.compressed), detailed=clean(original.detailed),desired=p?target(p):null;
   let revised=existing, status='PRESERVED', addedParagraphs=0;
   if(!r||!r.sourceText||String(r.sourceText).trim().length<20)status='HOLD_SOURCE_TEXT';
   else if(!p)status='HOLD_POINTS_UNKNOWN';
   else if(existing.length>=desired)status='PRESERVED_TARGET_MET';
   else if(detailed.length<Math.max(500,Math.round(desired*0.72)))status='HOLD_THIN_DETAIL';
   else {
     const base=existing.length>55&&!/^(?:미수록|없음|학습용 압축답안 없음|별도 확인)/.test(existing)?existing:'';
     const terms=qWords(r);let pool=chunks(detailed,terms,category);
     pool=pool.filter(x=>!base||overlap(x.s,base)<0.55);
     pool.sort((a,b)=>b.score-a.score||a.i-b.i);
     const chosen=[],limit=Math.min(2200,desired+420);
     let n=base.length;
     for(const x of pool){
       if(chosen.some(y=>overlap(x.s,y.s)>=0.58))continue;
       if(chosen.length>=10||n>=desired)break;
       if(n+x.s.length>limit+250&&chosen.length>=2)continue;
       chosen.push(x);n+=x.s.length+2;
     }
     chosen.sort((a,b)=>a.i-b.i);
     addedParagraphs=chosen.length;
     const add=chosen.map(x=>x.s).join('\n\n');
     revised=(base?[base,add].filter(Boolean).join('\n\n'):add);
     if(revised.length>=existing.length+140&&addedParagraphs>=1)status='EXPANDED_SOURCE_DERIVED';
     else{status='HOLD_NO_DISTINCT_BASIS';revised=existing;addedParagraphs=0;}
   }
   const variant=status==='EXPANDED_SOURCE_DERIVED'
     ?Object.freeze({...original,compressed:revised,batchStatus:status,batchSource:'existing detailed draft only',contentStatus:'DRAFT_UNVERIFIED',citationApproval:'HOLD',scoringApproved:false,handwrittenPages:'HOLD'})
     :original;
   next[id]=variant;
   statuses[status]=(statuses[status]||0)+1;
   audit.push(Object.freeze({id,year:r?.year??null,subject:category,points:p,sourceStatus:r?.sourceStatus||'UNSPECIFIED',status,existingChars:existing.length,currentChars:variant.compressed.length,addedParagraphs,sourcePageVerified:false,contentApproval:'HOLD',handwritingPageVerified:false}));
 }
 const changed=audit.filter(x=>x.status==='EXPANDED_SOURCE_DERIVED').length;
 const report=Object.freeze({schema:'nomusa-20year-quality-batch/1',status:'DRAFT_SOURCE_DERIVED_CONTENT_HOLD',totalCatalog:catalog.items.length,candidateCount:audit.length,changed,unchanged:audit.length-changed,counts:Object.freeze(statuses),rows:Object.freeze(audit),sourceVerification:'NOT_INDEPENDENTLY_VERIFIED',contentApproval:'HOLD',pageCountApproval:'HOLD',storageKeyChanged:false});
 window.NOMUSA_CANONICAL_SELECTION_V1=Object.freeze({...current,items:Object.freeze(next),qualityBatch:report});
 window.NOMUSA_20YEAR_QUALITY_BATCH_V1=report;
})();
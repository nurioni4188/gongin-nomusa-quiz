/* NOMUSA V16.9 — parallel 2023 + 2025 full editorial candidates.
 * Reproduce the tested V16.8 2022 method. No law/academic or handwriting approval.
 * Original problem IDs, point allocations, source drafts and storage all preserved.
 */
(function(){'use strict';
const c=window.NOMUSA_CANONICAL_SELECTION_V1;
const catalog=window.N27_CATALOG?.items;
if(!c?.items||!Array.isArray(catalog)){window.NOMUSA_V169_GATE={status:'HOLD_MISSING_INPUT'};return;}
const spec=Object.freeze({2023:{questions:19,parts:32},2025:{questions:19,parts:37}});
const items={...c.items},audits={},identity=s=>String(s||'').replace(/\s+/g,' ').trim();
for(const year of [2023,2025]){
 const rows=catalog.filter(q=>q.year===year);
 const displayed=Object.values(c.items).filter(x=>x.year===year);
 if(rows.length!==spec[year].questions||displayed.length!==spec[year].questions)throw Error('V169_CATALOG_COUNT_'+year);
 const audit=[];let partCount=0;
 for(const q of rows){
   const o=items[q.id];if(!o?.renderable||!o.detailed||!o.compressed||o.year!==year||o.subject!==q.subject||o.detailedBeforeV169)throw Error('V169_SOURCE_OR_DUPLICATE_'+q.id);
   const sections=(q.sections||[]).filter(x=>/^(?:물음\s*\d+|대문제\s*\d+)/.test(String(x.title||'')));
   const parts=sections.map(x=>{const m=String(x.title||'').match(/(\d+)점/);
     const points=m?Number(m[1]):q.points,low=q.points===50?8:4,high=q.points===50?10:4;
     return Object.freeze({title:x.title,points,minimumPages:Math.round(low*points/q.points*10)/10,maximumPages:Math.round(high*points/q.points*10)/10});});
   if(parts.reduce((a,x)=>a+x.points,0)!==q.points)throw Error('V169_SCORE_'+q.id);
   partCount+=parts.length;
   const seen=new Set(),kept=[];let removed=0;
   for(const paragraph of String(o.detailed).replace(/\r\n?/g,'\n').split(/\n\s*\n/)){
     const key=identity(paragraph);if(!key)continue;
     if(key.length>=180&&seen.has(key)){removed++;continue;}
     if(key.length>=180)seen.add(key);
     kept.push(paragraph.trim());
   }
   const detailed=kept.join('\n\n');
   items[q.id]=Object.freeze({...o,detailed,detailedBeforeV169:o.detailed,compressedBeforeV169:o.compressed,
     examPartRubricV169:Object.freeze(parts),editorialStatusV169:'FULL_MANUSCRIPT_CANDIDATE_APPROVAL_HOLD',
     finalAcademicApproval:'HOLD',citationApproval:'HOLD',handwrittenPages:'HOLD',scoringApproved:false});
   audit.push(Object.freeze({id:q.id,points:q.points,parts:parts.length,sourceChars:o.detailed.length,
     editorialChars:detailed.length,exactRepeatedParagraphsRemoved:removed,oldTextPreserved:true}));
 }
 if(partCount!==spec[year].parts)throw Error('V169_PARTS_'+year+'_'+partCount);
 audits[year]=Object.freeze({year,questions:rows.length,subquestions:partCount,
   rows:Object.freeze(audit),contentApproval:'HOLD',actualHandwriting:'HOLD',sourcePDFVisual:'HOLD'});
}
const gate=Object.freeze({status:'TWO_YEARS_38_QUESTIONS_69_SUBQUESTIONS_EDITORIAL_CANDIDATE_HOLD',
 years:Object.freeze(audits),questionCount:38,partCount:69,approvals:0,
 duplicateMode:'EXACT_SAME_LONG_PARAGRAPHS_ONLY',storageKeysChanged:false,
 mainChanged:false,productionChanged:false,previewDeployed:false});
window.NOMUSA_CANONICAL_SELECTION_V1=Object.freeze({...c,items:Object.freeze(items),qualityV169:gate});
window.NOMUSA_V169_GATE=gate;
})();
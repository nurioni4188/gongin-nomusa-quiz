/* NOMUSA V16.8: 2022 nineteen-question editorial display edition.
 * No new feature, no catalog mutation, no change to scoring, keys, or 2007-2026 source IDs.
 * Removes ONLY exactly repeating long paragraphs, preserving a complete prior snapshot.
 * This is a candidate manuscript pending historical-law, handwriting, independent review.
 */
(function(){'use strict';
const base=window.NOMUSA_CANONICAL_SELECTION_V1;
const catalog=window.N27_CATALOG?.items;
if(!base?.items||!Array.isArray(catalog)){window.NOMUSA_V168_2022_GATE={status:'HOLD_BASE'};return;}
const rows=catalog.filter(q=>q.year===2022);
const expected=Object.values(base.items).filter(x=>x.year===2022);
if(rows.length!==19||expected.length!==19)throw Error('V168_2022_EXPECT_19');
const pickExamParts=q=>(q.sections||[]).filter(s=>/^(?:물음\s*\d+|대문제\s*\d+)/.test(String(s.title||'')));\nconst countPart=rows.reduce((n,q)=>n+pickExamParts(q).length,0);
if(countPart!==32)throw Error('V168_2022_EXPECT_32');
const n={...base.items},audit=[];
const identity=s=>String(s||'').replace(/\s+/g,' ').trim();
for(const q of rows){
 const o=n[q.id];
 if(!o?.renderable||!o.detailed||!o.compressed||o.year!==2022||o.subject!==q.subject||o.detailedBeforeV168)throw Error('V168_2022_SOURCE_OR_DUPLICATE_'+q.id);
 const paragraphs=o.detailed.replace(/\r\n?/g,'\n').split(/\n\s*\n/);
 const seen=new Set(),kept=[];let removed=0;
 for(const para of paragraphs){
   const k=identity(para);
   // A short repeated heading may be meaningful; only exact duplicates of long paragraphs go.
   if(k.length>=180&&seen.has(k)){removed++;continue;}
   if(k.length>=180)seen.add(k);
   if(k)kept.push(para.trim());
 }
 const detailed=kept.join('\n\n');
 const subpoints=pickExamParts(q).map(s=>{
   const match=String(s.title||'').match(/(\d+)점/);
   const points=match?Number(match[1]):q.points;
   const basePages=q.points===50?8:4,highPages=q.points===50?10:4;
   return Object.freeze({title:s.title,points,minimumPages:Math.round(basePages*points/q.points*10)/10,maximumPages:Math.round(highPages*points/q.points*10)/10});
 });
 if(subpoints.reduce((a,b)=>a+b.points,0)!==q.points)throw Error('V168_PART_SCORE_'+q.id);
 n[q.id]=Object.freeze({...o,detailed,compact:o.compressed,
 detailedBeforeV168:o.detailed,compressedBeforeV168:o.compressed,
 examPartRubricV168:Object.freeze(subpoints),editorialStatusV168:'EDITORIAL_CANDIDATE_NOT_EXAM_APPROVED',
 finalAcademicApproval:'HOLD',citationApproval:'HOLD',handwrittenPages:'HOLD',scoringApproved:false});
 audit.push(Object.freeze({id:q.id,subject:q.subject,points:q.points,parts:subpoints.length,
   sourceChars:o.detailed.length,editorialChars:detailed.length,exactRepeatedParagraphsRemoved:removed,
   originalsPreserved:true,approval:'HOLD'}));
}
const gate=Object.freeze({status:'NINETEEN_EDITORIAL_CANDIDATES_THIRTYTWO_PARTS_CONTENT_HOLD',
 questions:audit.length,subquestions:countPart,rows:Object.freeze(audit),
 duplicateRemovalMode:'ONLY_IDENTICAL_LONG_PARAGRAPHS',originalCatalogChanged:false,storageKeysChanged:false,
 finalApproved:0,handwritingMeasured:false,productionMutated:false,previewDeployed:false});
window.NOMUSA_CANONICAL_SELECTION_V1=Object.freeze({...base,items:Object.freeze(n),qualityV168:gate});
window.NOMUSA_V168_2022_GATE=gate;
})();
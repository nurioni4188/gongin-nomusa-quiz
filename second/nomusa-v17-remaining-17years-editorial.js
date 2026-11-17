/* NOMUSA V17 — all remaining 17 years (2007-2021, 2024, 2026), source-safe editorial batch.
 * This is a content display/editorial step, not new study features.
 * Two source structures: legacy question parents and independent scored subquestions.
 * Keep all existing source IDs, baselines, preserved manuscripts and storage keys.
 */
(function(){'use strict';
const canonical=window.NOMUSA_CANONICAL_SELECTION_V1,catalog=window.N27_CATALOG?.items;
const expected={"2007":13,"2008":14,"2009":14,"2010":17,"2011":17,"2012":19,"2013":19,"2014":19,"2015":6,"2016":6,"2017":6,"2018":6,"2019":19,"2020":19,"2021":6,"2024":34,"2026":37};
if(!canonical?.items||!Array.isArray(catalog)){window.NOMUSA_V17_REMAINING_GATE={status:'HOLD_SOURCE_MISSING'};return;}
const pickParts=q=>{
 const sections=(q?.sections||[]).filter(s=>/^(?:물음\s*\d+|대문제\s*\d+)/.test(String(s.title||'')));
 const parts=sections.map(s=>({title:s.title,points:Number((String(s.title).match(/(\d+)점/)||[])[1])||0}));
 return parts.length&&parts.every(x=>x.points>0)&&parts.reduce((a,x)=>a+x.points,0)===Number(q?.points)?parts:null;
};
const targetYears=Object.keys(expected).map(Number),source=new Map(catalog.map(r=>[r.id,r]));
const original=canonical.items,entries=Object.values(original),out={...original},reports={};
const pageTarget=n=>{if(n===50)return [8,10];if(n===25)return [4,4];if(n<=10)return [2,2];if(n===15)return [3,3];const estimate=Math.round(n*4/25*10)/10;return [estimate,estimate];};
for(const year of targetYears){
 const candidates=entries.filter(q=>Number(q.year)===year);
 const audit=[],issues=[];
 if(candidates.length!==expected[year])issues.push('CANONICAL_YEAR_COUNT_'+candidates.length+'_EXPECTED_'+expected[year]);
 for(const old of candidates){
   const q=source.get(old.id),prior=String(old.detailed||''),brief=String(old.compressed||'');
   if(!q)issues.push(old.id+':SOURCE_ROW_MISSING');
   if(!old.renderable||!prior.trim()||!brief.trim())issues.push(old.id+':DRAFT_NOT_RENDERABLE');
   if(old.detailedBeforeV17)issues.push(old.id+':ALREADY_APPLIED');
   const paragraphs=prior.replace(/\r\n?/g,'\n').split(/\n\s*\n/),seen=new Set(),kept=[];
   let duplicates=0;
   for(const p of paragraphs){const key=p.replace(/\s+/g,' ').trim();if(!key)continue;
     if(key.length>=180&&seen.has(key)){duplicates++;continue;}
     if(key.length>=180)seen.add(key);kept.push(p.trim());
   }
   const score=Number(q?.points),knownPoints=Number.isFinite(score)&&score>0;
   const hasParts=knownPoints&&q&&pickParts(q),partBasis=!knownPoints?'POINTS_UNVERIFIED':hasParts?'VERIFIED_SECTION_SCORE_SUM':'SINGLE_SCORING_UNIT_UNSPLIT';
   // Never invent historical subquestion scores. When unstructured, preserve the original unit.
   const parts=!knownPoints?[Object.freeze({title:'원문 배점 확인 필요',points:null,
       minimumPages:null,maximumPages:null,splitVerified:false})]:
       (hasParts||[{title:(q?.topic||old.id)+' — 원장 전체 배점',points:score}]).map(p=>{
         const points=Number(p.points),goal=pageTarget(score);
         return Object.freeze({title:p.title,points,
           minimumPages:Math.round(goal[0]*points/score*10)/10,
           maximumPages:Math.round(goal[1]*points/score*10)/10,
           splitVerified:!!hasParts});
       });
   if(!knownPoints)issues.push(old.id+':POINTS_UNVERIFIED');
   else if(parts.some(p=>!p.points)||parts.reduce((a,p)=>a+p.points,0)!==score){
     issues.push(old.id+':SCORING_MISMATCH');
   }
   const detail=kept.join('\n\n');
   if(q&&old.renderable&&prior.trim()&&brief.trim()&&!old.detailedBeforeV17&&(knownPoints?parts.every(p=>p.points>0):true)){
     out[old.id]=Object.freeze({...old,detailed:detail,
       detailedBeforeV17:old.detailed,compressedBeforeV17:old.compressed,
       examPartRubricV17:Object.freeze(parts),editorialStatusV17:'BATCH_EDITORIAL_CONTENT_APPROVAL_HOLD',
       scoringApproved:false,finalAcademicApproval:'HOLD',citationApproval:'HOLD',handwrittenPages:'HOLD'});
   }
   audit.push(Object.freeze({id:old.id,year,subject:old.subject,
     points:knownPoints?score:null,partBasis,parts:parts.length,
     oldChars:prior.length,newChars:detail.length,
     removedExactLongParagraphs:duplicates,hasSourceText:!!q?.sourceText,
     renderable:!!old.renderable,priorPreserved:!!out[old.id]?.detailedBeforeV17,
     approval:'HOLD'}));
 }
 const totalParts=audit.reduce((a,x)=>a+x.parts,0);
 reports[year]=Object.freeze({year,expected:expected[year],count:audit.length,
   scoringUnits:totalParts,issues:Object.freeze(issues),rows:Object.freeze(audit),
   status:issues.length?'EDITORIAL_PARTIAL_HOLD':'EDITORIAL_SOURCE_CONNECTED_CONTENT_HOLD'});
}
const total=Object.values(reports).reduce((a,y)=>a+y.count,0);
const issues=Object.values(reports).reduce((a,y)=>a+y.issues.length,0);
const gate=Object.freeze({status:issues?'SEVENTEEN_YEAR_EDITORIAL_PARTIAL_HOLD':'SEVENTEEN_YEAR_EDITORIAL_CONNECTED_HOLD',
 years:Object.freeze(reports),yearCount:targetYears.length,questionCount:total,issues,
 duplicatesRemovedMode:'IDENTICAL_LONG_PARAGRAPHS_ONLY',originalAnswerSnapshots:true,
 contentApproved:0,sourceVisualVerified:false,handwritingVerified:false,
 productionChanged:false,previewDeployed:false,storageKeysChanged:false});
window.NOMUSA_CANONICAL_SELECTION_V1=Object.freeze({...canonical,items:Object.freeze(out),qualityV17:gate});
window.NOMUSA_V17_REMAINING_GATE=gate;
})();
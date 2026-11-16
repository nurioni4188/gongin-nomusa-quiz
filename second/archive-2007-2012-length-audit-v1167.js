/* V11.67: factual runtime inventory of 2007-2012 50-point academic answers.
 * Character counts are NOT handwritten pages and cannot imply academic approval.
 */
(function(){'use strict';const c=window.N27_CATALOG;if(!c||!Array.isArray(c.items))return;
const list=c.items.filter(x=>x.year>=2007&&x.year<=2012&&x.points===50&&/인사노무관리론|경영조직론/.test(x.subject||'')).map(x=>({
id:x.id,year:x.year,subject:x.subject,points:x.points,sourceTextAvailable:!!x.sourceText,
fullEssayChars:(x.examFullLengthDraft||'').length,sectionCount:x.sections?.length||0,
composite25Plus25:/25점/.test(x.sourceText||'')&&(/1\)/.test(x.sourceText||'')||/1\./.test(x.sourceText||'')),
partLongformAddon:x.independent25PointLongform?.map(p=>({part:p.part,addedChars:p.characters}))||null,
actualWrittenPageCount:null,sourceVisualVerified:false,contentApproved:false
}));
list.sort((a,b)=>a.fullEssayChars-b.fullEssayChars||a.year-b.year||a.id.localeCompare(b.id));
window.NOMUSA_V1167_LENGTH_AUDIT=Object.freeze({count:list.length,expectedCount:20,coverageComplete:list.length===20&&list.every(x=>x.fullEssayChars>0),priorities:list,
rule:'length is characters of full exam draft; never convert to handwriting page PASS',priority:'shortest 50-point first; next 25-point halves and 8 independent 25-point essays',allApprovals:'HOLD'});
})();
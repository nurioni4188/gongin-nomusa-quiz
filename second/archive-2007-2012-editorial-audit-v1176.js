/* V11.76 compact source-grounded editorial readiness audit: all 20 historical 50pt academic essays.
 * Never turn word count into handwritten page PASS.
 */
(function(){'use strict';const catalog=window.N27_CATALOG;if(!catalog||!Array.isArray(catalog.items))throw Error('V1176_CATALOG');
const rows=catalog.items.filter(r=>r.year>=2007&&r.year<=2012&&r.points===50&&/인사노무관리론|경영조직론/.test(r.subject||'')).map(r=>{
const original=String(r.sourceText||''),isComposite=/25점/.test(original),split=r.rebuiltIndependent25EssaysV1175||r.standalone25PointEssays||r.independent25PointLongform||r.independent25PointExpansions||null;
return {id:r.id,year:r.year,subject:r.subject,totalPoints:50,sourceQuestionAvailable:!!r.sourceText,essayCharacters:String(r.examFullLengthDraft||'').length,sectionCount:r.sections?.length||0,composite:isComposite,explicitPartCount:split?.length||0,reconstructedFullEssay:!!r.rebuilt50PointFullTextV1175,handwritingTarget:isComposite?'25점당 4장':'50점 8~10장',verifiedHandwritingPages:null,contentApproval:'HOLD',originalPrintVerification:'HOLD'};});
rows.sort((a,b)=>a.essayCharacters-b.essayCharacters||a.year-b.year||a.id.localeCompare(b.id));
window.NOMUSA_V1176_EDITORIAL_AUDIT=Object.freeze({count:rows.length,questionIdsUnique:new Set(rows.map(r=>r.id)).size===rows.length,all20Present:rows.length===20,allAnswered:rows.every(r=>r.essayCharacters>0),rows,priorityRule:'shortest by actual full essay characters, composite parts treated individually',handwritingCompleted:false,approval:'HOLD'});
})();
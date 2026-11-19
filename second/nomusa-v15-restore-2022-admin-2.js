/* NOMUSA V16.6 — preserve 2022 administrative 25pt V9 verified backbone,
 * while retaining focused V16.5 fact-specific legal supplements.
 * Previous complete final overlay text is snapshotted. All approval remains HOLD.
 * This read-only projection changes no catalog identifiers, scoring or saved data.
 */
(function(){'use strict';
const c=window.NOMUSA_CANONICAL_SELECTION_V1,id='2022-admin-2',it=c?.items?.[id];
if(!it?.detailedBeforeV16||!it?.compressedBeforeV16)throw Error('NOMUSA_V166_RESTORE_BASE_MISSING');
if(!/2019두52386/.test(it.detailedBeforeV16))throw Error('NOMUSA_V166_VERIFIED_V9_MISSING');
const marker='【V16.5 판례·사안포섭 교정】',summaryMarker='【V16.5 답안압축】';
if(!it.detailed.includes(marker)||!it.compressed.includes(summaryMarker))throw Error('NOMUSA_V166_RECENT_ENHANCEMENT_MISSING');
const recent=it.detailed.slice(it.detailed.lastIndexOf(marker));
const summary=it.compressed.slice(it.compressed.lastIndexOf(summaryMarker));
const detailed=it.detailedBeforeV16.trim()+'\n\n'+recent;
const compressed=it.compressedBeforeV16.trim()+'\n\n'+summary;
const items=Object.assign(Object.create(null),c.items);
items[id]=Object.freeze({...it,detailed,compressed,
 detailedBeforeV166:it.detailed,compressedBeforeV166:it.compressed,
 detailedV16Replaced:it.detailed,compressedV16Replaced:it.compressed,
 restoreNoteV15:'V9 precedent-backed base retained with V16.5 verified issue analysis; earlier V16 variants preserved as snapshots',
 contentStatus:'RESTORED_V9_PLUS_V165_ANALYSIS_CONTENT_HOLD',scoringApproved:false,finalAcademicApproval:'HOLD'});
window.NOMUSA_CANONICAL_SELECTION_V1=Object.freeze({...c,items:Object.freeze(items),
 restoreV15:Object.freeze({id,restored:true,latestSupplementPreserved:true,finalApproval:'HOLD'})});
})();
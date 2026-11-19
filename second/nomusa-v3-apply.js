/* NOMUSA 20YEAR V3: read-only projection for seven independently outlined study essays.
 * Manuscript ≠ exam-handwriting completeness, legal/academic approval, or PDF visual certification. */
(function(){'use strict';
const c=window.NOMUSA_CANONICAL_SELECTION_V1;
const b=window.NOMUSA_20YEAR_QUALITY_BATCH_V1;
const thin=window.NOMUSA_THIN_ENRICHMENT_V2;
const audit=window.NOMUSA_V3_SOURCE_POINTS_AUDIT;
const authored=window.NOMUSA_V3_AUTHORED_ESSAYS||{};
if(!c||c.gate?.catalogCount!==377||b?.candidateCount!==328||
   thin?.authored!==61||audit?.total!==29||audit?.unverifiedNumeric!==26)
   throw Error('NOMUSA_V3_BASELINE_MISMATCH');
const manuscripts=Object.entries(authored);
if(manuscripts.length!==7)throw Error('NOMUSA_V3_SEVEN_ESSAYS_REQUIRED');
const map=Object.assign(Object.create(null),c.items);
const rows=[];
for(const [id,x] of manuscripts){
 const before=c.items[id];
 if(!before||!before.renderable||typeof x.full!=='string'||typeof x.compact!=='string'||x.full.length<750||x.compact.length<150)
   throw Error('NOMUSA_V3_MANUSCRIPT_INVALID_'+id);
 const catalogue=window.N27_CATALOG.items.find(r=>r.id===id);
 if(!catalogue||!catalogue.sourceText)throw Error('NOMUSA_V3_SOURCE_MISSING_'+id);
 map[id]=Object.freeze({...before,detailed:x.full,compressed:x.compact,
    priorDetailedV3:before.detailed,priorCompressedV3:before.compressed,
    qualityV3:'ISSUE_SPECIFIC_MANUSCRIPT_DRAFT',modelAnswerStatus:'DRAFT_UNVERIFIED',
    manuscriptSourceUrls:x.sourceUrl||[],contentApproval:'HOLD',scoringApproved:false,
    examYearVerification:x.examYearVerification||'HOLD',
    handwritingPageVerification:'HOLD',sourcePageVerification:'HOLD'});
 rows.push(Object.freeze({id,year:catalogue.year,subject:catalogue.subject,points:catalogue.points,
    detailChars:x.full.length,compactChars:x.compact.length,
    preservedEarlierVersions:true,
    sourceLinks:x.sourceUrl?.length||0,contentApproval:'HOLD',
    handwritingPageVerification:'HOLD'}));
}
const allIds=Object.keys(map);
if(allIds.length!==328||rows.length!==7||new Set(allIds).size!==328)throw Error('V3_INTEGRITY_BREAK');
const gate=Object.freeze({schema:'nomusa-20year-writing-gate/3',totalCatalog:377,candidates:328,
    previousV1Expanded:208,previousV2IssueDrafts:61,v3Manuscripts:7,
    auditSourcePoints:29,unverifiedNumericPoints:26,originalPDFVerified:0,
    contentFinalApproved:0,handwritingPageVerified:0,
    rawCatalogAndStoredKeysChanged:false,
    paragraphsAuthored:true,sourceTextComparison:'SELECTED_ISSUES_ONLY',
    contentApproval:'HOLD',rows:Object.freeze(rows)});
window.NOMUSA_CANONICAL_SELECTION_V1=Object.freeze({...c,items:Object.freeze(map),qualityV3:gate});
window.NOMUSA_20YEAR_V3_GATE=gate;
})();
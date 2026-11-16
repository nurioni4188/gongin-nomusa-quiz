/* NOMUSA V3 audit only. Never changes catalog points. 2019/2020 text still needs PDF visual validation. */
(function(){'use strict';
const source=window.N27_CATALOG?.items||[],batch=window.NOMUSA_20YEAR_QUALITY_BATCH_V1,lookup=new Map(source.map(r=>[r.id,r]));
if(source.length!==377||batch?.candidateCount!==328)throw Error('V3_POINTS_AUDIT_INVARIANT');
const missing=batch.rows.filter(r=>r.status.startsWith('HOLD'));
if(missing.length!==90)throw Error('V3_POINTS_EXPECT_90');
const targets=missing.filter(r=>r.status!=='HOLD_THIN_DETAIL');
if(targets.length!==29)throw Error('V3_POINTS_EXPECT_29');
const rows=targets.map(rec=>{
 const r=lookup.get(rec.id),text=String(r?.sourceText||'');
 const all=Array.from(text.matchAll(/(?<!\d)(\d{1,2})\s*점/g),m=>Number(m[1]));
 const numeric=(rec.status==='HOLD_POINTS_UNKNOWN');
 const candidates=[...new Set(all.filter(v=>v>0&&v<=50))];
 const parentCandidate=numeric?(candidates.includes(50)?50:candidates.includes(25)?25:null):Number(r.points);
 const consistency=numeric
  ?!parentCandidate?'HOLD_NO_CANDIDATE':
   (all.length>7||all.filter(x=>x===50).length>1)?'HOLD_MIXED_OR_OVERLAPPED_EXTRACTED_TEXT':
    'HOLD_PDF_VISUAL_CONFIRM_REQUIRED'
  :rec.status;
 return Object.freeze({id:rec.id,year:r?.year,subject:rec.subject,sourceStatus:r?.sourceStatus,originalPoints:r?.points,
   extractedScoreTokens:all,provisionalParentPoints:parentCandidate,
   subquestionRecords:r?.subquestions?.map(s=>({id:s.id,points:s.points,text:s.text}))||[],
   sourceTextChars:text.length,originalReason:rec.status,verdict:consistency,
   sourceFile:r?.pdfPath||null,originalPDFVisualVerified:false,
   catalogPointsUnchanged:true,contentApproval:'HOLD'});
});
if(rows.filter(r=>r.originalReason==='HOLD_POINTS_UNKNOWN').length!==26||
 rows.some(r=>r.catalogPointsUnchanged!==true))throw Error('V3_AUDIT_POINTS_SOURCE_BREAK');
window.NOMUSA_V3_SOURCE_POINTS_AUDIT=Object.freeze({schema:'nomusa-source-points/3',
 total:29,unverifiedNumeric:26,other:3,
 parentCandidatesResolvedFromExtractedText:rows.filter(r=>r.originalReason==='HOLD_POINTS_UNKNOWN'&&r.provisionalParentPoints).length,
 verifiedAgainstOriginalPDF:0,changedCatalogPoints:0,rows:Object.freeze(rows),
 sourceOnly:'CATALOG_EXTRACTED_TEXT',approval:'HOLD'});
})();
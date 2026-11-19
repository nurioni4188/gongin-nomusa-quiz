/* NOMUSA V18 — 26 verified examination score annotations, no new app feature.
 * Mirrors PDF read visually and original question text matched. Historical law/content HOLD.
 * Preserve all original IDs, question rows, scoring approval flags and learner storage.
 */
(function(){'use strict';
const prior=window.NOMUSA_CANONICAL_SELECTION_V1;
const source=window.N27_CATALOG?.items;
const evidence=[{"id":"2019_p1_q1","year":2019,"points":50,"parts":[{"title":"물음 1","points":25},{"title":"물음 2","points":25}],"pdf":"https://cbtexam.kr/file/6a5fa6b998/"},{"id":"2019_p1_q2","year":2019,"points":25,"parts":[{"title":"전체 문제","points":25}],"pdf":"https://cbtexam.kr/file/6a5fa6b998/"},{"id":"2019_p1_q3","year":2019,"points":25,"parts":[{"title":"전체 문제","points":25}],"pdf":"https://cbtexam.kr/file/6a5fa6b998/"},{"id":"2019_p3_q1","year":2019,"points":50,"parts":[{"title":"물음 1","points":20},{"title":"물음 2","points":5},{"title":"물음 3","points":5},{"title":"물음 4","points":10},{"title":"물음 5","points":10}],"pdf":"https://cbtexam.kr/file/1063401adc/"},{"id":"2019_p3_q2","year":2019,"points":25,"parts":[{"title":"물음 1","points":10},{"title":"물음 2","points":15}],"pdf":"https://cbtexam.kr/file/1063401adc/"},{"id":"2019_p3_q3","year":2019,"points":25,"parts":[{"title":"물음 1","points":15},{"title":"물음 2","points":10}],"pdf":"https://cbtexam.kr/file/1063401adc/"},{"id":"2019_p4_q1","year":2019,"points":50,"parts":[{"title":"물음 1","points":30},{"title":"물음 2","points":20}],"pdf":"https://cbtexam.kr/file/3ae16e2dfd/"},{"id":"2019_p4_q2","year":2019,"points":25,"parts":[{"title":"전체 문제","points":25}],"pdf":"https://cbtexam.kr/file/3ae16e2dfd/"},{"id":"2019_p4_q3","year":2019,"points":25,"parts":[{"title":"전체 문제","points":25}],"pdf":"https://cbtexam.kr/file/3ae16e2dfd/"},{"id":"2019_p5_q1","year":2019,"points":50,"parts":[{"title":"물음 1","points":25},{"title":"물음 2","points":25}],"pdf":"https://cbtexam.kr/file/4423284e58/"},{"id":"2019_p5_q2","year":2019,"points":25,"parts":[{"title":"전체 문제","points":25}],"pdf":"https://cbtexam.kr/file/4423284e58/"},{"id":"2019_p6_q1","year":2019,"points":50,"parts":[{"title":"물음 1","points":25},{"title":"물음 2","points":25}],"pdf":"https://cbtexam.kr/file/7f0250d0fa/"},{"id":"2019_p6_q2","year":2019,"points":25,"parts":[{"title":"전체 문제","points":25}],"pdf":"https://cbtexam.kr/file/7f0250d0fa/"},{"id":"2020_p1_q1","year":2020,"points":50,"parts":[{"title":"물음 1","points":20},{"title":"물음 2","points":30}],"pdf":"https://cbtexam.kr/file/99dafd07b9/"},{"id":"2020_p1_q2","year":2020,"points":25,"parts":[{"title":"전체 문제","points":25}],"pdf":"https://cbtexam.kr/file/99dafd07b9/"},{"id":"2020_p2_q1","year":2020,"points":50,"parts":[{"title":"물음 1","points":30},{"title":"물음 2","points":20}],"pdf":"https://cbtexam.kr/file/f084b4f1ea/"},{"id":"2020_p2_q2","year":2020,"points":25,"parts":[{"title":"전체 문제","points":25}],"pdf":"https://cbtexam.kr/file/f084b4f1ea/"},{"id":"2020_p4_q1","year":2020,"points":50,"parts":[{"title":"물음 1","points":30},{"title":"물음 2","points":20}],"pdf":"https://cbtexam.kr/file/bab6cf58dd/"},{"id":"2020_p4_q2","year":2020,"points":25,"parts":[{"title":"전체 문제","points":25}],"pdf":"https://cbtexam.kr/file/bab6cf58dd/"},{"id":"2020_p4_q3","year":2020,"points":25,"parts":[{"title":"전체 문제","points":25}],"pdf":"https://cbtexam.kr/file/bab6cf58dd/"},{"id":"2020_p6_q1","year":2020,"points":50,"parts":[{"title":"물음 1","points":10},{"title":"물음 2","points":30},{"title":"물음 3","points":10}],"pdf":"https://cbtexam.kr/file/39c183c53c/"},{"id":"2020_p6_q2","year":2020,"points":25,"parts":[{"title":"물음 1","points":5},{"title":"물음 2","points":10},{"title":"물음 3","points":10}],"pdf":"https://cbtexam.kr/file/39c183c53c/"},{"id":"2020_p6_q3","year":2020,"points":25,"parts":[{"title":"물음 1","points":5},{"title":"물음 2","points":14},{"title":"물음 3","points":6}],"pdf":"https://cbtexam.kr/file/39c183c53c/"},{"id":"2020_p7_q1","year":2020,"points":50,"parts":[{"title":"물음 1","points":25},{"title":"물음 2","points":25}],"pdf":"https://cbtexam.kr/file/f35def1941/"},{"id":"2020_p7_q2","year":2020,"points":25,"parts":[{"title":"전체 문제","points":25}],"pdf":"https://cbtexam.kr/file/f35def1941/"},{"id":"2020_p7_q3","year":2020,"points":25,"parts":[{"title":"전체 문제","points":25}],"pdf":"https://cbtexam.kr/file/f35def1941/"}];
if(!prior?.items||!Array.isArray(source)){window.NOMUSA_V18_POINTS_GATE={status:'HOLD_SOURCE_MISSING'};return;}
const catalog=new Map(source.map(x=>[x.id,x])),items={...prior.items},audit=[];
for(const e of evidence){
 const q=catalog.get(e.id),old=items[e.id],src=String(q?.sourceText||'');
 if(!old?.detailed||!old?.compressed||Number(old.year)!==e.year||!q||Number(q.points||0)>0||old.verifiedPointsV18)throw Error('V18_MISMATCH_'+e.id);
 const start=src.match(/\(\s*(\d+)\s*점\s*\)/);
 if(!start||Number(start[1])!==e.points)throw Error('V18_PARENT_SCORE_'+e.id);
 const headers=[...src.matchAll(/(?:^|\s)물음\s*(\d+)\)\s+/g)];
 const parsed=[];
 for(let i=0;i<headers.length;i++){
   const h=headers[i],end=headers[i+1]?.index??src.length;
   const seg=src.slice(h.index+h[0].length,end);
   const all=[...seg.matchAll(/\(\s*(\d+)\s*점\s*\)/g)].map(x=>Number(x[1]));
   if(!all.length)throw Error('V18_PART_NO_POINTS_'+e.id);
   parsed.push({title:'물음 '+h[1],points:all[all.length-1]});
 }
 if(!parsed.length)parsed.push({title:'전체 문제',points:e.points});
 if(JSON.stringify(parsed)!==JSON.stringify(e.parts))throw Error('V18_PART_MISMATCH_'+e.id);
 if(parsed.reduce((n,x)=>n+x.points,0)!==e.points)throw Error('V18_SCORE_SUM_'+e.id);
 const pages=e.points===50?[8,10]:[4,4];
 const rubric=e.parts.map(p=>Object.freeze({...p,
    minimumPages:Math.round(pages[0]*p.points/e.points*10)/10,
    maximumPages:Math.round(pages[1]*p.points/e.points*10)/10,
    splitVerified:true,proof:'MIRRORED_PDF_VISUAL_MATCH_SOURCE_TEXT'}));
 items[e.id]=Object.freeze({...old,
   verifiedPointsV18:e.points,examPartRubricV18:Object.freeze(rubric),
   sourceScoringProofV18:Object.freeze({origin:'REPRODUCED_EXAM_PAPER_PDF_AND_EXISTING_SOURCE_TEXT',url:e.pdf}),
   contentStatus:old.contentStatus||'DRAFT_UNVERIFIED',
   scoringApproved:false,finalAcademicApproval:'HOLD',handwrittenPages:'HOLD'});
 audit.push(Object.freeze({id:e.id,points:e.points,parts:rubric.length,priorAnswersPreserved:old.detailed===items[e.id].detailed,
 pdf:e.pdf,status:'EXAM_POINT_EVIDENCE_MATCHED_CONTENT_HOLD'}));
}
const gate=Object.freeze({status:'26_EXAM_POINT_EVIDENCES_MATCHED_CONTENT_HOLD',
 count:audit.length,year2019:audit.filter(x=>x.id.startsWith('2019_')).length,year2020:audit.filter(x=>x.id.startsWith('2020_')).length,
 rows:Object.freeze(audit),originalCatalogMutated:false,
 finalLegalApproval:'HOLD',handwritingVerified:false,scoringApproved:false,productionChanged:false,previewDeployed:false});
window.NOMUSA_CANONICAL_SELECTION_V1=Object.freeze({...prior,items:Object.freeze(items),qualityV18:gate});
window.NOMUSA_V18_POINTS_GATE=gate;
})();
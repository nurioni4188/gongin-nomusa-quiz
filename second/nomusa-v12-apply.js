/* NOMUSA V12 — 2019·2020 법률과목(노동법·행정쟁송법·민사소송법) 20개 문항 render-only overlay.
 * 원장상 배점이 '원문 배점 확인'(HOLD)이던 문항을 저장소 원본 PDF로 문항·배점 대조 후 집필.
 * 원장(rc27_essay_catalog.js)의 points 필드·ID·localStorage 키·원본 PDF 불변. 확인 배점은 pointsVerifiedV12로만 기록.
 * 직전 텍스트는 detailedBeforeV12/compressedBeforeV12로 보존. 공식 모범답안·채점·수기분량 승인 아님. */
(function(){'use strict';
const prev=window.NOMUSA_CANONICAL_SELECTION_V1;
const v11=window.NOMUSA_V11_QUALITY_GATE;
const cases=window.NOMUSA_V12_MANUSCRIPTS||{};
const questions=window.N27_CATALOG?.items||[];
// 원본 PDF SHA-256 (로컬 저장소 바이트 기준, Q-Net 게시본과의 동일성은 미확인)
const PDF_SHA={
 'source_pdf/2019/2019_p1_administrative.pdf':'dfeb464372a3dfa828ba75a7b58cc8d9e2eaa3bf20d39fae268ae86246d2e2b1',
 'source_pdf/2019/2019_p4_civil_procedure.pdf':'b6114ab718601f8fb27490a13c748a79262a07b6a50b07dd3d491cdde03c8bd8',
 'source_pdf/2019/2019_p5_labor1.pdf':'88c77bd7f1e61a29292ae67de48f41301e3c015a47f5c0e3794df2f0ae49791e',
 'source_pdf/2019/2019_p6_labor2.pdf':'1049a762068dc905140f6a87ee381a815b26b5393792554daf0a23748f23e3db',
 'source_pdf/2020/2020_p1_labor1.pdf':'74e1682a426bec50f8b57b75708865174445ed2638cf5f870f06adcfaebb70ea',
 'source_pdf/2020/2020_p2_labor2.pdf':'f2dadb65da5da74d1ed5bf060cdc4061198a3bd5af9607f74c77bb049457dad4',
 'source_pdf/2020/2020_p4_administrative.pdf':'4bb770a0a6e482af20cd6b73e3efddc363958b63dede28672c88bc140badd71a',
 'source_pdf/2020/2020_p7_civil_procedure.pdf':'fcad6a6d982be7bab61a040595b8c2b5d0eeb41d78ed8a929c87d64fda743135'};
const expected=['2019_p5_q1','2019_p5_q2','2019_p6_q1','2019_p6_q2','2020_p1_q1','2020_p1_q2','2020_p2_q1','2020_p2_q2',
 '2019_p1_q1','2019_p1_q2','2019_p1_q3','2020_p4_q1','2020_p4_q2','2020_p4_q3',
 '2019_p4_q1','2019_p4_q2','2019_p4_q3','2020_p7_q1','2020_p7_q2','2020_p7_q3'];
if(!prev?.items||v11?.v11Rewritten!==17||questions.length!==377||Object.keys(prev.items).length!==328)
  throw Error('NOMUSA_V12_BASELINE_MISMATCH');
if(Object.keys(cases).length!==expected.length||expected.some(id=>!cases[id])||
   Object.keys(cases).some(id=>!expected.includes(id)))
  throw Error('NOMUSA_V12_CASE_REGISTRY_MISMATCH');
const qmap=new Map(questions.map(q=>[q.id,q]));
const items=Object.assign(Object.create(null),prev.items),rows=[];
const seeds=window.N1071_SEEDS=window.N1071_SEEDS||{};
for(const id of expected){
 const q=qmap.get(id),before=prev.items[id],v=cases[id];
 if(!q?.sourceText||!before?.renderable||!before.detailed||!before.compressed)
  throw Error('NOMUSA_V12_BASE_MISSING_'+id);
 // 원장 배점은 미확정 문자열이어야 하고(불변), 확인 배점은 PDF 문항 표기와 일치해야 함
 if(typeof q.points==='number')throw Error('NOMUSA_V12_POINTS_ALREADY_NUMERIC_'+id);
 if(!PDF_SHA[v.pdf]||!new RegExp('\('+v.points+'점\)').test(q.sourceText.replace(/\s+/g,'')))
  throw Error('NOMUSA_V12_SOURCE_POINTS_MISMATCH_'+id);
 if(v.parts&&v.parts.reduce((a,b)=>a+b,0)!==v.points)throw Error('NOMUSA_V12_PARTS_MISMATCH_'+id);
 if(!v.full||!v.compact||v.full.length<before.detailed.length*1.5||v.compact.length<400||
    v.compact.length>=v.full.length*0.5||!/Ⅰ\.[\s\S]*Ⅱ\.[\s\S]*Ⅲ\.[\s\S]*Ⅳ\./.test(v.compact)||!/결론/.test(v.compact))
  throw Error('NOMUSA_V12_NOT_ENHANCED_'+id);
 const next=Object.freeze({...before,detailed:v.full,compressed:v.compact,
   detailedBeforeV12:before.detailed,compressedBeforeV12:before.compressed,
   pointsVerifiedV12:v.points,subPointsVerifiedV12:v.parts?Object.freeze([...v.parts]):null,
   sourcePdfV12:v.pdf,sourcePdfSha256V12:PDF_SHA[v.pdf],
   memorySeedsV12:Object.freeze([...v.seeds]),
   verifiedPrecedentUrlsV12:Object.freeze([...v.evidence]),
   precedentAuditStatusV12:v.status,
   contentStatusV12:'A_LEARNING_DRAFT_COMPLETE',
   finalAcademicApproval:'HOLD',officialScoreApproval:'HOLD',
   paperPagesVerified:false,scoringApproved:false});
 items[id]=next;
 if(!seeds[id])seeds[id]=[v.seeds];
 rows.push(Object.freeze({id,year:q.year,subject:q.subject,catalogPoints:q.points,pointsVerified:v.points,
   subPoints:v.parts||null,pdf:v.pdf,
   priorDetailedChars:before.detailed.length,revisedDetailedChars:v.full.length,
   priorCompactChars:before.compressed.length,revisedCompactChars:v.compact.length,
   previousVersionPreserved:true,precedentUrls:Object.freeze([...v.evidence]),
   manualPageCountVerified:false,finalApproval:'HOLD'}));
}
if(Object.keys(items).length!==328||rows.length!==20)throw Error('NOMUSA_V12_ID_SET_CHANGED');
const gate=Object.freeze({schema:'nomusa-20year-essay-law-2019-2020/12',
  sourceQuestions:377,representativeCandidates:328,v12Rewritten:20,
  pointsVerifiedFromRepoPdf:20,
  scope:'2019·2020 노동법(8)·행정쟁송법(6)·민사소송법(6) — 원장 배점 HOLD 26개 중 20개를 원본 PDF로 배점 확인',
  originalCatalogChanged:false,originalPointsChanged:false,originalStorageKeysChanged:false,
  productionMutated:false,previewDeployed:false,handwritingPageTargetReached:false,
  qnetOfficialPdfHashVerified:false,finalContentApprovals:0,
  reviewStatus:'REVIEW_ONLY_V12_LAW_2019_2020_CONTENT_HOLD',
  rows:Object.freeze(rows)});
window.NOMUSA_CANONICAL_SELECTION_V1=Object.freeze({...prev,items:Object.freeze(items),qualityV12:gate});
window.NOMUSA_V12_QUALITY_GATE=gate;
})();

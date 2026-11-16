/* NOMUSA V11.38 — de-duplicated examiner-oriented working drafts.
 * Preserves source sections, question IDs, point values, memory-card section indices and saved keys.
 * These are review drafts, NOT verified handwriting page counts or academic approval. */
(function(){'use strict';
const c=window.N27_CATALOG, prior=window.NOMUSA_V1137_LENGTH_GATE;
if(!c||!prior||prior.total!==24)throw Error('V1138_DEPENDENCY_MISSING');
const registry=new Set(prior.rows.map(r=>r.id));
const original=c.items.map(r=>({id:r.id,points:r.points,year:r.year,subject:r.subject,sections:r.sections}));
const norm=s=>String(s||'').replace(/\s+/g,' ').trim();
const threshold=points=>points>=50?4000:points>=25?1600:points>=15?1100:800;
const pageTarget=points=>points>=50?'8~10장':points>=25?'4장':points>=15?'3장':'2장';
const stats=[];
for(const id of registry){
 const row=c.items.find(r=>r.id===id);if(!row||!row.sections||!row.examFullLengthDraft)throw Error('V1138_TARGET_MISSING_'+id);
 const base=row.sections.filter(s=>!/^시험장 독립 압축답안|^V11\.37 시험장 분량형 논술|^V11\.38/.test(s.title||''));
 const unique=[],seen=new Set(),paragraphs=[];
 for(const s of base){
   const value=norm(s.detailed);if(!value)continue;
   const fingerprint=value.replace(/[\s.,，·:;()\[\]ⅠⅡⅢⅣⅤⅥⅦⅧ]/g,'').slice(0,160);
   if(seen.has(fingerprint))continue;
   seen.add(fingerprint);unique.push(s);
 }
 // The original first source-linked answer is retained verbatim; added longform blocks
 // remain in order. V11.36/V11.37 concatenated restatements are excluded from display.
 const detailed=unique.map((s,i)=>(i===0?'Ⅰ. 기출 요구와 기본 논증':'Ⅱ-'+i+'. '+norm(s.title))+'\n'+String(s.detailed||'').trim()).join('\n\n');
 const compact=[row.sections.find(s=>/^시험장 독립 압축답안/.test(s.title||''))?.detailed||''].filter(Boolean).join('\n\n');
 const study=compact||norm(row.examCompressedAnswer);
 const specific=id==='2026-경영조직론|3|1'?'국제기업은 본사와 해외자회사 사이의 권한 배분, 국가별 법률과 문화 차이, 지리적 분산에 따른 정보지연, 글로벌 표준과 현지 고객요구의 충돌을 동시에 관리해야 한다. 이를 해결하기 위해 권한의 범위와 보고체계를 명확히 하고, 지역별 정보공유 및 기능 간 협업을 설계해야 한다.':'';
 const body=detailed+(specific?'\n\nⅡ. 국제기업의 조직적 과제에 대한 보충\n'+specific:'')+'\n\nⅢ. 논점 정리\n'+study;
 const estimate=norm(detailed).length,bodyLength=norm(body).length;
 const corrected={...row,examFullLengthDraft:body,examCompressedAnswer:study,examOutlineVersion:'V11.38_DEDUP_V1',examHandwritingTarget:pageTarget(row.points),examCharacterCount:bodyLength,examCharacterWarning:bodyLength<threshold(row.points)?'SHORT_OF_HEURISTIC':'HEURISTIC_MET_NOT_HANDWRITING_VERIFIED',contentRevision:'V11.38_DEDUP_STUDY_DRAFT',approved:false,scoringApproved:false,contentApproval:'HOLD',citationReview:'HOLD'};
 c.items=c.items.map(v=>v.id===id?corrected:v);
 stats.push({id,points:row.points,sectionCount:row.sections.length,displaySections:unique.length,previousChars:norm(row.examFullLengthDraft).length,dedupChars:bodyLength,compressedChars:study.length,target:pageTarget(row.points),heuristicMet:bodyLength>=threshold(row.points),pagesVerified:false});
}
if(c.items.length!==original.length||original.some((r,i)=>{const n=c.items[i];return n.id!==r.id||n.year!==r.year||n.points!==r.points||n.subject!==r.subject||n.sections!==r.sections;}))throw Error('V1138_SOURCE_OR_SECTIONS_MODIFIED');
window.NOMUSA_V1138_GATE=Object.freeze({targetCount:stats.length,rows:stats,idsPreserved:true,sectionIndicesPreserved:true,storageKeyChange:false,actualBrowserTest:'NOT_RUN',handwritingPageCount:'HOLD',contentApproval:'HOLD'});
})();
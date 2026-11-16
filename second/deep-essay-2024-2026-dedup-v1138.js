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
 const previousCompactStudy=compact||norm(row.examCompressedAnswer);
 // 2026 organization Q1(1), 12pt. Additional academic learning draft; original remains archived.
 // Four dimensions match the catalog question; source PDF and actual handwriting pages remain HOLD.
 const refinedCompact=id==='2026-경영조직론|1|1'?"Ⅰ. 협상전략의 개념\n1. 분배적 협상(distributive negotiation)은 교섭 대상을 크기가 정해진 자원으로 보고, 합의가능영역 안에서 자기 몫을 최대한 확보하는 경쟁적 협상이다. 대표적으로 한정된 임금인상 재원의 배분처럼 한쪽의 추가 획득이 상대의 양보로 이어지는 경우이다.\n2. 통합적 협상(integrative negotiation)은 당사자의 표면적 요구 뒤에 있는 이해관계와 우선순위를 탐색하여 새로운 선택지를 조합함으로써 공동이익을 확대하는 문제해결형 협상이다. 임금 외에 근무시간·교육·생산성 등을 함께 논의할 때 가능성이 커진다.\n\nⅡ. 네 가지 비교\n1. 지향 목표: 분배적 협상은 주어진 가치에서 자신의 몫을 최대화하는 가치배분(value claiming)을, 통합적 협상은 이해관계 조정을 통해 전체 가치를 증대하는 가치창출(value creation)을 우선한다. 다만 통합적 협상에서도 창출된 이익을 최종적으로 어떻게 배분할지는 남는다.\n2. 정보공유 수준: 분배적 협상은 유보점·양보한계 등의 노출을 경계하고 제한적·전략적으로 정보를 공개한다. 통합적 협상은 상대의 필요와 우선순위를 파악하기 위해 질문·경청과 선택적 정보공유를 중시한다. 그러나 통합적 방식도 모든 정보의 무조건적 공개를 뜻하지는 않는다.\n3. 관계의 지속가능성: 분배적 협상은 단기·단일 쟁점에서 효율적일 수 있으나 강한 압박이나 불신은 향후 협력관계를 훼손할 위험이 있다. 통합적 협상은 공동 문제해결과 신뢰구축을 통해 반복적 관계에 유리할 수 있으나, 상호성·이행능력이 없으면 그 효과는 제한된다.\n4. 분배구조: 분배적 협상은 고정된 파이를 나누는 제로섬적 구조이고, 통합적 협상은 쟁점을 결합하고 교환하여 파이를 키우는 비제로섬적 구조이다. 후자도 가치창출 후 배분 교섭은 필요하므로 두 전략은 현실에서 병존한다.\n\nⅢ. 적용과 결론\n예컨대 노사가 임금인상률만 다투면 분배적 교섭이 중심이지만, 임금·유연근무·직무교육·생산성 향상을 함께 논의하면 서로 비용과 편익이 다른 대안을 조합할 수 있다. 따라서 협상자는 유보점과 협상결렬 시 대안(BATNA)을 점검하면서도 공통이익 탐색과 객관적 기준을 병행해야 한다.\n\n학술근거: Walton & McKersie, A Behavioral Theory of Labor Negotiations(1965); Fisher & Ury, Getting to Yes(1981).":'';
 const study=refinedCompact||previousCompactStudy;
 const specific=id==='2026-경영조직론|3|1'?'국제기업은 본사와 해외자회사 사이의 권한 배분, 국가별 법률과 문화 차이, 지리적 분산에 따른 정보지연, 글로벌 표준과 현지 고객요구의 충돌을 동시에 관리해야 한다. 이를 해결하기 위해 권한의 범위와 보고체계를 명확히 하고, 지역별 정보공유 및 기능 간 협업을 설계해야 한다.':'';
 const body=detailed+(specific?'\n\nⅡ. 국제기업의 조직적 과제에 대한 보충\n'+specific:'')+'\n\nⅢ. 논점 정리\n'+study;
 const estimate=norm(detailed).length,bodyLength=norm(body).length;
 const corrected={...row,...(refinedCompact?{previousCompressedDraftV1138:previousCompactStudy}:{}),examFullLengthDraft:body,examCompressedAnswer:study,examOutlineVersion:'V11.38_DEDUP_V1',examHandwritingTarget:refinedCompact?'3장':pageTarget(row.points),examCharacterCount:bodyLength,examCharacterWarning:bodyLength<threshold(row.points)?'SHORT_OF_HEURISTIC':'HEURISTIC_MET_NOT_HANDWRITING_VERIFIED',contentRevision:'V11.38_DEDUP_STUDY_DRAFT',approved:false,scoringApproved:false,contentApproval:'HOLD',citationReview:'HOLD'};
 c.items=c.items.map(v=>v.id===id?corrected:v);
 stats.push({id,points:row.points,sectionCount:row.sections.length,displaySections:unique.length,previousChars:norm(row.examFullLengthDraft).length,dedupChars:bodyLength,compressedChars:study.length,target:refinedCompact?'3장':pageTarget(row.points),heuristicMet:bodyLength>=threshold(row.points),pagesVerified:false});
}
if(c.items.length!==original.length||original.some((r,i)=>{const n=c.items[i];return n.id!==r.id||n.year!==r.year||n.points!==r.points||n.subject!==r.subject||n.sections!==r.sections;}))throw Error('V1138_SOURCE_OR_SECTIONS_MODIFIED');
window.NOMUSA_V1138_GATE=Object.freeze({targetCount:stats.length,rows:stats,idsPreserved:true,sectionIndicesPreserved:true,storageKeyChange:false,actualBrowserTest:'NOT_RUN',handwritingPageCount:'HOLD',contentApproval:'HOLD'});
})();
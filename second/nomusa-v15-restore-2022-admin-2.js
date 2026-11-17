/* NOMUSA V15 — 2022 행정쟁송법 제2문(25점) 표시본 복원(render-only, 단일 문항).
 * 다른 세션의 V16 2022 law25 재작성(1,120자, 판례 인용 없음·결론 유보)이 V9에서 공개자료로 확인한
 * 대법원 2020. 2. 20. 2019두52386 전원합의체 기반 답안(2,150자)을 대체하여 V9 회귀검사가 실패함.
 * 저장된 detailedBeforeV16(V9 원고)을 다시 표시본으로 하고, V16 원고는 detailedV16Replaced로 보존. 원장·ID·배점·저장키 불변. */
(function(){'use strict';
const c=window.NOMUSA_CANONICAL_SELECTION_V1,id='2022-admin-2',it=c?.items?.[id];
if(!it||!it.detailedBeforeV16||!it.compressedBeforeV16)throw Error('NOMUSA_V15_RESTORE_BASE_MISSING');
if(!/2019두52386/.test(it.detailedBeforeV16))throw Error('NOMUSA_V15_RESTORE_UNEXPECTED_PRIOR');
const items=Object.assign(Object.create(null),c.items);
items[id]=Object.freeze({...it,detailed:it.detailedBeforeV16,compressed:it.compressedBeforeV16,
  detailedV16Replaced:it.detailed,compressedV16Replaced:it.compressed,
  restoreNoteV15:'V9 verified 2019두52386 answer restored as display text; V16 draft preserved'});
window.NOMUSA_CANONICAL_SELECTION_V1=Object.freeze({...c,items:Object.freeze(items),restoreV15:Object.freeze({id,restored:true})});
})();

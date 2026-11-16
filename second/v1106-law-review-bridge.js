/* V11.0.6: optional, no writes to answer data, app state, or localStorage */
(()=>{'use strict';
const NS='N1106_LAW_REVIEW_BRIDGE';
const data=window.N1105_LAW_REVIEW;
if(!data||data.status!=='REVIEW_ONLY_HOLD'||data.approvedCount!==0||data.correctionCount!==18||data.questionCount!==47){
  window[NS]=Object.freeze({version:'V11.0.6',status:'HOLD_MISSING_OR_INVALID_SIDECAR'});return;
}
const style=document.createElement('style');style.textContent="\n.n1106-review{margin:20px 0;padding:16px;border:1px solid #b8c8c3;background:#f5f9f8;color:#172b28;border-radius:12px;line-height:1.65;overflow-wrap:anywhere;font-family:system-ui,-apple-system,'Segoe UI',sans-serif;font-size:14px}\n.n1106-review h3{font-size:17px;margin:0 0 6px;color:#174b43}\n.n1106-review p{margin:5px 0 10px}.n1106-review .n1106-muted{color:#586c68;font-size:12px}\n.n1106-review details{border-top:1px solid #d3dfd9;padding:10px 0;margin:0}.n1106-review summary{font-weight:650;cursor:pointer;color:#174b43}\n.n1106-review .n1106-quote{padding:10px 12px;background:#fff;border-left:3px solid #7eaca0;border-radius:5px;white-space:pre-line;margin:9px 0}\n.n1106-review .n1106-proposal{border-left-color:#bc8b4a}.n1106-review a{color:#126855;text-decoration:underline;font-size:13px;margin-right:12px;display:inline-block}\n.n1106-review .n1106-alert{font-weight:700;color:#875019}\n@media(max-width:390px){.n1106-review{padding:11px;font-size:13px}.n1106-review a{display:block;margin:4px 0}}\n@media print {.n1106-review{break-inside:avoid}}\n";style.dataset.n1106Style='1';document.head.appendChild(style);
function txt(tag,value,cls){const e=document.createElement(tag);e.textContent=String(value??'');if(cls)e.className=cls;return e;}
function link(url,label){if(!/^https:\/\//.test(url||''))return null;const a=document.createElement('a');a.href=url;a.target='_blank';a.rel='noopener noreferrer';a.textContent=label;return a;}
function panel(id){
  const corrections=data.byQuestionId[id]||[];
  if(corrections.length!==3)return null;
  const section=document.createElement('section');section.className='n1106-review';section.dataset.n1106Question=id;
  section.setAttribute('aria-label','미승인 법률 교정안 3건');
  section.append(txt('h3','V11.0.6 · 문항별 교정 검토 3건'));
  section.append(txt('p','이 문항의 원본 학습답안은 그대로 유지됩니다. 아래 문장은 미승인 검토용 교정 후보입니다.','n1106-alert'));
  section.append(txt('p',`문항 ID ${id} · 교정 3건 · 최종 내용승인 0/47 HOLD`,'n1106-muted'));
  corrections.forEach((c,i)=>{
    const d=document.createElement('details');if(i===0)d.open=true;
    d.append(txt('summary',`${i+1}. ${c.sourcePartHeading} — ${c.correctionDisposition} / HOLD`));
    d.append(txt('p','기존 답안 단락 (원문 보존)','n1106-muted'));
    d.append(txt('div',c.sourceExcerpt,'n1106-quote'));
    d.append(txt('p','검토용 교정 문장 (자동 반영 금지)','n1106-muted'));
    d.append(txt('div',c.proposedCorrectionV1104,'n1106-quote n1106-proposal'));
    d.append(txt('p',`검토 범위: ${c.principleReview} · ${c.reviewReason}`,'n1106-muted'));
    const a=link(c.statuteUrl,'관련 법령 원문');const b=link(c.precedentUrl,'관련 판례 원문');
    if(a)d.append(a);if(b)d.append(b);
    section.append(d);
  });
  return section;
}
const isHub=!!document.getElementById('app');
const isEssay=!!document.getElementById('n27-essay-root')&&!isHub;
const target=isHub?document.getElementById('app'):document.getElementById('n27-essay-root');
function locked(){
  if(isHub){const exp=Math.max(Number(window.HubState?.essay?.examEnd)||0,Number(window.HubState?.hub?.exam?.end)||0);return exp>Date.now()||!!document.querySelector('[data-trace="4"][disabled]');}
  if(isEssay)return !!window.N27_ESSAY_TEST?.locked;
  return true;
}
function locate(){
  if(isHub){const tag=target.querySelector('[data-selected-id]');const detail=tag?.closest('.study-detail');return {id:tag?.dataset.selectedId,container:detail};}
  if(isEssay){return {id:window.N27_ESSAY_TEST?.selected,container:target.querySelector('.n27-detail')};}
  return {};
}
let painting=false;
function update(){
  if(painting)return;
  const {id,container}=locate();
  if(!container)return;
  const current=container.querySelector('.n1106-review');
  const allowed=id && !locked() && (data.byQuestionId[id]||[]).length===3;
  if(!allowed){if(current){painting=true;current.remove();painting=false;}return;}
  if(current?.dataset.n1106Question===id)return;
  painting=true;
  if(current)current.remove();
  const p=panel(id);if(p)container.append(p);
  painting=false;
}
let queued=false;
const obs=new MutationObserver(()=>{if(queued||painting)return;queued=true;queueMicrotask(()=>{queued=false;update()});});
if(target)obs.observe(target,{childList:true,subtree:true});
update();
window[NS]=Object.freeze({version:'V11.0.6',status:target?'REVIEW_ONLY_HOLD':'HOLD_MISSING_APP_ROOT',type:isHub?'study-hub':isEssay?'second':'unknown',get selected(){return locate().id||'';},get displayed(){return !!target?.querySelector('.n1106-review');}});
})();
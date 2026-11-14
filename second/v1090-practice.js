/* V10.9.0 - non-destructive second-stage handwritten-practice module.
   Enhances existing V10.7.9; retains original catalog, user storage key, original paper evidence and source-only HOLD statuses.
   No external AI/automatic grading service. All comparisons are simple on-device text checks. */
(()=>{'use strict';
const root=document.getElementById('n27-essay-root');
const api=window.N27_ESSAY_TEST, catalog=window.N27_CATALOG;
if(!root||!api||!Array.isArray(catalog?.items))return;
const items=[...catalog.items,...(window.N27_ARCHIVE?.items||[])];
const byId=new Map(items.map(r=>[r.id,r]));
const KEY='nomusa_rc27_v103_essay_records_v1';
const states={};
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const charCount=s=>Array.from(String(s||'')).length;
const allowedDensity=[300,400,500,600,700,800];
function defPages(v){const n=Number(v)||0;return n<=5?1:n<=10?2:n<=15?3:n<=25?4:n<=30?5:n<=40?7:n<=50?9:Math.min(12,Math.max(1,Math.ceil(n/6)));}
function plan(r){const x=api.saved?.writingPlans?.[r.id]||{};return {pages:Number.isInteger(x.pages)&&x.pages>=1&&x.pages<=12?x.pages:defPages(r.points),density:allowedDensity.includes(x.perPage)?x.perPage:500};}
function kind(r){return /노동경제학/.test(r.subject)?'economy':/노동법|행정쟁송법|민사소송법/.test(r.subject)?'law':'management';}
function buckets(r){switch(kind(r)){
 case 'law':return [['쟁점과 문제의 소재',10],['적용 조문·판례 및 판단기준',35],['사실관계 포섭과 법적 평가',45],['결론',10]];
 case 'economy':return [['모형의 조건과 가정',15],['수식·그래프·계산',50],['경제적 해석과 한계',25],['결론',10]];
 default:return [['문제 요구와 개념',15],['학자·이론·구성요소',35],['비교·사례 적용',40],['결론과 시사점',10]];
}}
function substantive(r){if(r.sourceOnly)return {text:'',status:'SOURCE_ONLY'};
 const ex=window.N1078_ESSAYS?.items?.[r.id];
 if(ex?.parts?.length)return {text:ex.parts.map(p=>p.heading+'\n'+p.text).join('\n\n'),status:'EXPANDED_DRAFT'};
 const q=window.N1074_QUALITY?.items?.[r.id];
 if(q?.improvedDraft)return {text:q.improvedDraft,status:'CURATED_DRAFT'};
 return {text:(r.sections||[]).map(p=>[p.title,p.detailed].filter(Boolean).join('\n')).join('\n\n'),status:'ORIGINAL_DRAFT'};
}
function segments(s,limit){
 const all=Array.from(String(s||''));if(!all.length)return [''];
 const out=[];let start=0;
 while(start<all.length){
  let end=Math.min(all.length,start+limit);
  if(end<all.length){
   // Prefer nearby paragraph/word boundary while keeping pages close to the selected density.
   const min=Math.max(start+Math.floor(limit*.9),start+1);
   for(let i=end-1;i>=min;i--){if(all[i]==='\n'||all[i]===' '){end=i+1;break;}}
  }
  out.push(all.slice(start,end).join(''));start=end;
 }
 return out;
}
function save(draft,id){let saved=api.saved;
 if(!saved?.drafts)return false;
 saved.drafts[id]=draft;
 try{localStorage.setItem(KEY,JSON.stringify(saved));return true;}catch(e){return false;}
}
function modelIndex(r){const ans=substantive(r);return {text:ans.text,length:charCount(ans.text),status:ans.status};}
function allocation(r,p){return buckets(r).map(([label,percent])=>`<tr><th scope="row">${esc(label)}</th><td>${percent}%</td><td>${(p.pages*percent/100).toFixed(1)}장</td><td>${Math.round(p.pages*p.density*percent/100).toLocaleString('ko-KR')}자</td></tr>`).join('');}
function shell(r){const p=plan(r),ans=modelIndex(r),actual=charCount(api.saved?.drafts?.[r.id]||''),goal=p.pages*p.density,complete=ans.length>=goal;
 return `<section class="v1090-shell" data-v1090-id="${esc(r.id)}" aria-label="V10.9.0 실전 답안지 및 내용 검토">
 <div class="v1090-head"><div><div class="v1090-overline">V10.9.0 · 2차 논술 실전 고도화</div><h3>시험장 답안지 연습</h3></div><span class="v1090-label">${esc(r.points)}점 · ${p.pages}장 목표</span></div>
 <p class="v1090-intro">실제 기출 요구사항에 맞춰 답안 장수를 설정하고 손글씨용 연습 답안지를 출력합니다. 장수는 <b>개인 학습 목표</b>이며 Q-Net 공식 분량·채점기준이 아닙니다.</p>
 <div class="v1090-kpis"><div><small>권장 목표</small><strong>${p.pages}장</strong></div><div><small>환산 글자 수</small><strong>${goal.toLocaleString('ko-KR')}자</strong></div><div><small>내 작성</small><strong data-v1090-count>${actual.toLocaleString('ko-KR')}자</strong></div><div><small>모범 초안</small><strong>${ans.length.toLocaleString('ko-KR')}자</strong></div></div>
 <p class="v1090-audit">${r.sourceOnly?'원문 연습 항목: 검토된 상세답안 없음 · 답안 생성·승인 금지':complete?'초안의 글자 수가 설정 목표 이상입니다. 내용 정확성은 별도 검증해야 합니다.':`기존 학습답안이 분량 목표보다 ${Math.max(0,goal-ans.length).toLocaleString('ko-KR')}자 부족합니다. 실제 논점 보강 필요.`}</p>
 <div class="v1090-config"><label>목표 장수 <select data-v1090-pages>${Array.from({length:12},(_,i)=>`<option value="${i+1}" ${p.pages===i+1?'selected':''}>${i+1}장</option>`).join('')}</select></label><label>장당 글자 수 <select data-v1090-density>${allowedDensity.map(n=>`<option value="${n}" ${p.density===n?'selected':''}>${n}자</option>`).join('')}</select></label></div>
 <details class="v1090-allocation"><summary>과목별 논점·분량 배분표</summary><div class="v1090-table-wrap"><table><thead><tr><th>논점</th><th>비중</th><th>분량</th><th>글자 수</th></tr></thead><tbody>${allocation(r,p)}</tbody></table></div></details>
 <div class="v1090-actions"><button type="button" data-v1090-tab="editor" aria-pressed="${states[r.id]?.tab!=='preview'&&states[r.id]?.tab!=='compare'}">답안 작성</button><button type="button" data-v1090-tab="preview" aria-pressed="${states[r.id]?.tab==='preview'}">답안지 미리보기</button><button type="button" data-v1090-tab="compare" aria-pressed="${states[r.id]?.tab==='compare'}" ${api.locked?'disabled':''}>논점 비교</button><button type="button" data-v1090-print>인쇄 / PDF 저장</button></div>
 <div class="v1090-panel" data-v1090-content></div><p class="v1090-foot">개인 작성 내용은 기존 브라우저 저장키를 사용합니다. 파일·서버 전송 및 AI 채점은 하지 않습니다. 공식 모범답안·전문가 승인 여부는 별도 HOLD로 관리합니다.</p>
 </section>`;
}
function renderContent(r){const host=root.querySelector('.v1090-shell[data-v1090-id="'+CSS.escape(r.id)+'"]');if(!host)return;const p=plan(r),state=states[r.id]||(states[r.id]={tab:'editor'});if(api.locked&&state.tab==='compare')state.tab='editor';const text=String(api.saved?.drafts?.[r.id]||'');const el=host.querySelector('[data-v1090-content]');
 host.querySelectorAll('[data-v1090-tab]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.v1090Tab===state.tab)));
 if(state.tab==='preview'){
  const pg=segments(text,p.density),pages=Math.max(p.pages,pg.length);
  el.innerHTML=`<p class="v1090-summary">개인 작성 ${charCount(text)}자 · 예상 ${Math.max(1,pg.length)}장 / 목표 ${p.pages}장. 실제 출력 페이지 수는 브라우저 글꼴·줄바꿈에 따라 달라질 수 있습니다.</p><div class="v1090-page-list">${Array.from({length:pages},(_,i)=>paper(r,i+1,pages,pg[i]||'',false)).join('')}</div>`;
 } else if(state.tab==='compare'){
  const a=modelIndex(r);const basis=[...new Set([r.topic,...(r.sections||[]).map(x=>x.title||'')].flatMap(x=>String(x).split(/[·,／:：()\s]+/)).filter(x=>x.length>1&&!/^물음|문제|제\d+문$/.test(x)))].slice(0,16);
  const matches=basis.filter(w=>text.includes(w)),missing=basis.filter(w=>!text.includes(w));
  const outlineTests=buckets(r).map(([l])=>({label:l,checked:l.split(/[·과 ]/).some(x=>x.length>=2&&text.includes(x))}));
  el.innerHTML=`<h4>내 답안과 학습 초안의 논점 점검</h4><p>기계적인 키워드 문자열 대조입니다. AI 채점·공식 채점은 제공하지 않으며, 판례·학설의 적합성도 판단하지 않습니다. 표현이 달라도 실제로는 같은 내용일 수 있습니다.</p>
  <p><b>표현 포함 ${matches.length}/${basis.length}</b> · 누락 후보 ${missing.length}개</p><div class="v1090-words">${basis.map(w=>`<span class="${text.includes(w)?'present':'absent'}">${esc(w)} ${text.includes(w)?'✓':'· 검토'}</span>`).join('')}</div>
  <h5>과목별 작성 구조 점검</h5><ul>${outlineTests.map(x=>`<li>${x.checked?'✓':'□'} ${esc(x.label)} — ${x.checked?'제목 표현 발견':'관련 내용 직접 확인'}</li>`).join('')}</ul>
  <p class="v1090-warning">${a.status==='SOURCE_ONLY'?'대조할 승인 답안 없음 · 원문과 수동 비교 필요':'기존 학습답안도 검증 전 초안입니다. 자동 비교 결과를 점수·정답으로 사용하지 마세요.'}</p>`;
 } else {
  el.innerHTML=`<label class="v1090-editor-label" for="v1090-editor">나의 답안 (자동저장 · ${esc(r.year)}년 ${esc(r.subject)})</label><textarea id="v1090-editor" data-v1090-editor spellcheck="false" rows="13" maxlength="300000" placeholder="Ⅰ. 문제의 제기\n\nⅡ. 관련 법리·학설·모형\n\nⅢ. 사안의 분석과 적용\n\nⅣ. 결론">${esc(text)}</textarea><div class="v1090-edit-foot"><span data-v1090-status role="status">${charCount(text)}자 / ${p.pages*p.density}자(학습 목표)</span><button type="button" data-v1090-outline>과목별 답안 틀 넣기</button></div><p class="v1090-warning">답안지 페이지 수는 필기량 추정치이며 문항별 공식 분량 규정이 아닙니다. 원본·법령·판례의 정확성은 직접 확인하세요.</p>`;
 }
}
function paper(r,n,total,content,print){return `<article class="v1090-paper" aria-label="연습용 논술 답안지 ${n}쪽"><header><strong>공인노무사 2차 논술 연습용 답안지</strong><small>공식 양식 아님</small></header><div class="v1090-meta"><span>${esc(r.year)}년 · ${esc(r.subject)}</span><span>${esc(r.points)}점 · 제 ${n} / ${total}쪽</span></div><div class="v1090-lines">${content?`<div class="v1090-text">${esc(content)}</div>`:`<div class="v1090-empty">${print?'':'답안 작성 후 글자가 표시됩니다.'}</div>`}</div><footer>개인 연습용 · 글자 수 기준 추정 분할 · 검증된 공식 채점자료 아님</footer></article>`;}
function doPrint(r){const p=plan(r),text=String(api.saved?.drafts?.[r.id]||''),pg=segments(text,p.density),count=Math.max(p.pages,pg.length);
 document.querySelector('.v1090-print-layer')?.remove();
 const lay=document.createElement('div');lay.className='v1090-print-layer';lay.innerHTML=Array.from({length:count},(_,i)=>paper(r,i+1,count,pg[i]||'',true)).join('');document.body.appendChild(lay);
 const clear=()=>{lay.remove();window.removeEventListener('afterprint',clear)};window.addEventListener('afterprint',clear);window.print();setTimeout(clear,1800);
}
function mount(){const r=byId.get(api.selected);const detail=root.querySelector('.n27-detail');if(!r||!detail)return;
 if(detail.querySelector('.v1090-shell[data-v1090-id="'+CSS.escape(r.id)+'"]'))return;
 const old=detail.querySelector('.v1090-shell');if(old)old.remove();
 const tpl=document.createElement('div');tpl.innerHTML=shell(r);const v=tpl.firstElementChild;const after=detail.querySelector('.n1079-question')||detail.querySelector('.n1077-plan');if(after)after.insertAdjacentElement('afterend',v);else detail.prepend(v);renderContent(r);
}
let pending=false;const observer=new MutationObserver(()=>{if(pending)return;pending=true;queueMicrotask(()=>{pending=false;mount()});});observer.observe(root,{childList:true,subtree:true});mount();
root.addEventListener('click',event=>{
 const b=event.target.closest('button[data-v1090-tab],button[data-v1090-print],button[data-v1090-outline]');if(!b)return;
 const r=byId.get(api.selected);if(!r)return;
 if(b.dataset.v1090Tab){if(api.locked&&b.dataset.v1090Tab==='compare')return;states[r.id]={tab:b.dataset.v1090Tab};renderContent(r);}
 else if(b.hasAttribute('data-v1090-print'))doPrint(r);
 else if(b.hasAttribute('data-v1090-outline')){const ta=root.querySelector('[data-v1090-editor]');if(!ta)return;
 const parts=buckets(r).map(([n],i)=>`${['Ⅰ','Ⅱ','Ⅲ','Ⅳ'][i]}. ${n}\n`).join('\n');
 if(ta.value.trim()&&!confirm('작성한 답안 끝에 논술 구성 틀을 추가하시겠습니까?'))return;
 ta.value+=(ta.value.trim()?'\n\n':'')+parts;ta.dispatchEvent(new Event('input',{bubbles:true}));ta.focus();}
});
root.addEventListener('input',event=>{if(!event.target.matches('[data-v1090-editor]'))return;const id=api.selected, val=event.target.value;const ok=save(val,id),r=byId.get(id);if(!r)return;
 const p=plan(r),chars=charCount(val),s=root.querySelector('[data-v1090-status]'),count=root.querySelector('[data-v1090-count]');if(s)s.textContent=ok?`${chars}자 / ${p.pages*p.density}자 · 자동저장 완료`:'저장 실패: JSON 내보내기로 기록 보호 필요';if(count)count.textContent=chars.toLocaleString('ko-KR')+'자';
});
root.addEventListener('change',event=>{const t=event.target;if(!t.matches('[data-v1090-pages],[data-v1090-density]'))return;const id=api.selected,r=byId.get(id);if(!r)return;const pg=root.querySelector('[data-v1090-pages]'),dn=root.querySelector('[data-v1090-density]');const pages=Number(pg?.value),density=Number(dn?.value);if(!Number.isInteger(pages)||pages<1||pages>12||!allowedDensity.includes(density))return;
 const st=api.saved;st.writingPlans=st.writingPlans||{};st.writingPlans[id]={pages,perPage:density};try{localStorage.setItem(KEY,JSON.stringify(st));}catch(e){}const prev=states[id]?.tab||'editor';root.querySelector('.v1090-shell')?.remove();states[id]={tab:prev};mount();
});
window.N1090_TEST={version:'V10.9.0',get selected(){return api.selected},get currentPlan(){const r=byId.get(api.selected);return r?plan(r):null},get answerCount(){return catalog.items.filter(x=>!x.sourceOnly).length},get archiveCount(){return catalog.items.filter(x=>x.sourceOnly).length},targetFor:defPages,get saved(){return api.saved}};
})();

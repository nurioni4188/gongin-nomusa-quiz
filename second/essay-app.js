/* V10.7.7 answer-length study targets; all years/subjects, nonofficial. RC35 1st-stage untouched. */
(()=>{'use strict';
const data=window.N27_CATALOG, root=document.getElementById('n27-essay-root');
if(!data||!root||!Array.isArray(data.items)){console.error('HOLD_RC27_ESSAY_CATALOG');return;}
const rows=data.items, byId=new Map(rows.map(r=>[r.id,r]));
if(byId.size!==rows.length)throw Error('DUPLICATED_STUDY_IDS');
const sk='nomusa_rc27_v103_essay_records_v1';
const defaultState=()=>({drafts:{},flags:{},bookmarks:{},checks:{},memoryCards:{},sourceChecks:{},researchCards:{},writingPlans:{},examEnd:0});
let saved=defaultState();
try{const x=JSON.parse(localStorage.getItem(sk)||'null');if(x&&typeof x==='object') saved={drafts:x.drafts||{},flags:x.flags||{},bookmarks:x.bookmarks||{},checks:x.checks||{},memoryCards:x.memoryCards||{},sourceChecks:x.sourceChecks||{},researchCards:x.researchCards||{},writingPlans:x.writingPlans||{},examEnd:Number(x.examEnd)||0};}catch(e){}
let selected=rows.find(r=>r.year===2026)?.id||rows[0]?.id, year='all',subject='all',answerType='all',query='',message='',pane='detail', pdfOpen=false;
try{const fromHub=new URLSearchParams(location.search).get('item');if(fromHub&&byId.has(fromHub))selected=fromHub;}catch(e){}
const recallHidden={}, recallInput={};
const esc=x=>String(x??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const locked=()=>saved.examEnd>Date.now();
const years=[...new Set(rows.map(r=>r.year))].sort((a,b)=>b-a);
const subjects=[...new Set(rows.map(r=>r.subject))].sort((a,b)=>a.localeCompare(b,'ko'));
const answerCount=rows.filter(r=>Array.isArray(r.sections)&&r.sections.length>0).length;
const sourceCount=rows.filter(r=>r.sourceOnly).length;
function store(){try{localStorage.setItem(sk,JSON.stringify(saved));return true;}catch(e){message='브라우저 저장이 차단되었습니다. 기록 내보내기를 이용하세요.';return false;}}
function stopExpired(){if(saved.examEnd&&saved.examEnd<=Date.now()){saved.examEnd=0;store();}}
function toast(t){message=t;const a=root.querySelector('#n27-status');if(a)a.textContent=t;}
function matches(r){const q=query.trim().toLowerCase();return (year==='all'||String(r.year)===year)&&(subject==='all'||r.subject===subject)&&(answerType==='all'||(answerType==='draft'?!r.sourceOnly:!!r.sourceOnly))&&(!q||[r.topic,r.subject,r.id,r.sourceText].join(' ').toLowerCase().includes(q));}
function getRows(){return rows.filter(matches);}
const opt=(v,t,c)=>`<option value="${esc(v)}" ${c===v?'selected':''}>${esc(t)}</option>`;
function download(){const value={schema:'nomusa-rc27-essay-records/1',saved:{drafts:saved.drafts,flags:saved.flags,bookmarks:saved.bookmarks,checks:saved.checks,memoryCards:saved.memoryCards,sourceChecks:saved.sourceChecks,researchCards:saved.researchCards,writingPlans:saved.writingPlans,examEnd:0}};const url=URL.createObjectURL(new Blob([JSON.stringify(value,null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='nomusa_2cha_2013_2026_study_backup.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),2000);}
// V10.6: all learning views reuse the existing 128 draft answers, never promote them to official answers.
const panes=[['detail','상세답안'],['compact','시험장 압축'],['memory','핵심암기'],['write','직접 작성'],['compare','비교·복습']];
const isLegal=r=>/노동법|행정쟁송|민사소송/.test(r.subject||'');
function outline(r){return isLegal(r)?'Ⅰ. 문제의 소재\n\nⅡ. 관련 법리·판례\n\nⅢ. 사안의 검토\n\nⅣ. 결론\n':'Ⅰ. 문제 요구사항\n\nⅡ. 관련 개념·이론\n\nⅢ. 분석 및 적용\n\nⅣ. 결론\n';}
// V10.7: mnemonic hints are editable learning aids, never official keywords or scoring criteria.
const mnemonicKey=(r,i)=>`${r.id}::${i}`;
const keywordsFrom=x=>[...new Set(String(x||'').split(/[,\n;|]+|\s+·\s+/).map(t=>t.trim()).filter(t=>t.length>0&&t.length<75))].slice(0,12);
const acronymOf=words=>words.map(w=>(w.match(/[가-힣A-Za-z0-9]/)||[])[0]||'').join('');
// V10.7.2: three-word mnemonic chunks; exact-string self-recall is not legal/academic scoring.
const chunk3=words=>Array.from({length:Math.ceil(words.length/3)},(_,i)=>words.slice(i*3,i*3+3));
const normalized=x=>String(x||'').normalize('NFKC').replace(/[\s·.,;:()·-]+/g,'').toLowerCase();
function recallAccuracy(words,answer){const typed=keywordsFrom(answer);const matches=words.filter((w,i)=>normalized(w)===normalized(typed[i])).length;return {matches,total:words.length,percent:words.length?Math.round(100*matches/words.length):0};}
const quality=window.N1074_QUALITY||{items:{}};
const qualityFor=r=>quality.items?.[r.id]||null;
const sectionsFor=r=>r.sections?.length?r.sections:[{title:'내 키워드',detailed:''}];
const cardState=k=>saved.memoryCards[k]?.review||'';
function questionReviewed(r){return saved.flags[r.id]===true&&!sectionsFor(r).some((_,i)=>cardState(mnemonicKey(r,i))==='retry');}
function setQuestionReviewed(r,done){saved.flags[r.id]=done;sectionsFor(r).forEach((s,i)=>{const k=mnemonicKey(r,i);saved.memoryCards[k]={...cardFor(r,s,i),review:done?'known':'retry'};});}
function syncQuestionReview(r){saved.flags[r.id]=sectionsFor(r).every((_,i)=>cardState(mnemonicKey(r,i))==='known');}

function seedKeywords(r,s,i=0){
 if(r.sourceOnly)return [];
 const curated=qualityFor(r)?.mnemonic;if(i===0&&Array.isArray(curated)&&curated.length)return curated;
 const hints=window.N1071_SEEDS?.[r.id]?.[i];
 if(Array.isArray(hints)&&hints.length)return hints;
 const t=(r.topic||'')+' '+(s?.detailed||'');
 if(/갈등의 개념/.test(t)&&/개인 차원/.test(t)&&/업무 차원/.test(t)&&/조직 차원/.test(t))return ['개인차원','업무차원','조직차원'];
 if(/역기능적 갈등/.test(t)&&/상위목표/.test(t)&&/자원확충/.test(t))return ['상위목표','자원확충','부서교류','역할명료화','중재협상'];
 if(/라힘/.test(t)&&/통합/.test(t)&&/순응/.test(t)&&/지배/.test(t)&&/회피/.test(t)&&/타협/.test(t))return ['통합','순응','지배','회피','타협'];
 if(/가용성 편향/.test(t)&&/고착 편향/.test(t)&&/확증 편향/.test(t)&&/사후확신 편향/.test(t)&&/몰입의 심화/.test(t))return ['가용성','고착','확증','사후확신','몰입의 심화'];
 // Title-based candidates only; generic placeholders and scoring instructions are excluded.
 const terms=String(r.topic||'').split(/[·,/→:：]+/).map(t=>t.trim()).filter(t=>t.length>=2&&!/^제\d+문|^물음/.test(t));
 return [...new Set(terms)].slice(0,6);
}
function cardFor(r,s,i){const k=mnemonicKey(r,i), x=saved.memoryCards[k];return x&&typeof x==='object'&&!Array.isArray(x)?x:{words:seedKeywords(r,s,i).join(', '),story:'',review:''};}
function sourceRequirements(r){const text=String(r.sourceText||'');const parts=text.split(/\n+/).map(x=>x.trim()).filter(Boolean);const requests=parts.filter(x=>/(?:하시오|답하시오|기술하시오|설명하시오|논하시오|제시하시오|검토하시오)[.。\s]*$/.test(x));return (requests.length?requests.slice(-3):parts.slice(-1)).map(x=>x.length>330?x.slice(-330):x);}
function draftHeadingCandidates(r){const lines=(r.sections||[]).flatMap(s=>String(s.detailed||'').split(/\n/)).map(x=>x.trim()).filter(x=>/^([ⅠⅡⅢⅣⅤⅥⅦⅧ]|[1-9])\s*[.)．]|^(?:가|나|다|라)\s*[.)．]/.test(x)&&x.length<110);return [...new Set(lines)].slice(0,36);}
function curatedAnswerGuide(r,q){
 const source=sourceRequirements(r),checks=saved.checks[r.id]||{};
 const names=['요구사항','개념·이론','분석·적용','결론'];
 return `<section class="n107-answer-plan n1072-answer-flow n1074-answer-guide" aria-label="문항별 답안 요구사항"><h3>문항별 요구사항 → 답안 구조 점검</h3><p class="n27-note">${esc(q.label)} · 배점 ${esc(r.points)}점 · 학습용 직접 검토 안내, 공식 채점기준 아님</p><div class="n1072-req"><strong>문제에서 가져온 질문 (원본문제지 독립대조 필요)</strong>${source.map(x=>`<p>${esc(x)}</p>`).join('')}</div><h4>이 문제에서 확인할 내용</h4><ul class="n1074-requests">${q.requirements.map((v,i)=>`<li>${esc(v)}</li>`).join('')}</ul><div class="n1072-flow-grid">${q.stages.map(([title,prompt],i)=>{const key='flow-'+names[i];return `<section class="n1072-stage"><h4>${esc(title)}</h4><p>${esc(prompt)}</p><label class="n1072-stage-check"><input type="checkbox" data-flow-check="${esc(key)}" ${checks[key]?'checked':''}> 직접 원문·답안을 대조함</label></section>`;}).join('')}</div></section>`;
}
/* V10.7.5: source-linked 128-item quality audit; no fictitious citations or approvals. */

// V10.7.7: user-adjustable study-length targets, NOT official exam sheet allocations.
const pageDefaults=points=>{
 const n=Number(points)||0;
 if(n<=5)return {pages:1,range:'1~2장'};
 if(n<=10)return {pages:2,range:'1~2장'};
 if(n<=15)return {pages:3,range:'2~4장'};
 if(n<=20)return {pages:4,range:'3~5장'};
 if(n<=25)return {pages:4,range:'3~5장'};
 if(n<=30)return {pages:5,range:'4~7장'};
 if(n<=40)return {pages:7,range:'6~8장'};
 if(n<=50)return {pages:9,range:'8~10장'};
 return {pages:Math.min(12,Math.max(1,Math.round(n*0.18))),range:'자율 설정'};
};
function writingPlan(r){
 const p=pageDefaults(r.points),x=saved.writingPlans?.[r.id]||{};
 const pages=Number.isInteger(x.pages)&&x.pages>=1&&x.pages<=12?x.pages:p.pages;
 const perPage=[300,400,500,600,700,800].includes(x.perPage)?x.perPage:500;
 return {...p,pages,perPage,custom:Number.isInteger(x.pages)&&x.pages>=1&&x.pages<=12};
}
const lengthOf=x=>Array.from(String(x||'')).length;
function lengthParts(r){return (r.sections||[]).map(x=>String(x.detailed||'')).join('\n\n');}
const oneDecimal=n=>Number(n).toFixed(1);
function subjectAllocation(r){
 if(/노동법|행정쟁송법|민사소송법/.test(r.subject||''))return {names:['쟁점·문제의 소재','조문·판례·학설','사안 포섭·검토','결론'],weights:[.10,.35,.45,.10]};
 if(/노동경제학/.test(r.subject||''))return {names:['문제 조건·목적','경제모형·가정','수식·그래프·해석','결론'],weights:[.10,.30,.50,.10]};
 return {names:['문제 요구사항','학자·원전·이론','비교표·사례 적용','결론·시사점'],weights:[.10,.35,.45,.10]};
}
function writingPlanPanel(r,lock){
 const p=writingPlan(r),draftLen=lengthOf(saved.drafts[r.id]||''),draftPages=draftLen/p.perPage,
       targetChars=p.pages*p.perPage,detailLen=lengthOf(lengthParts(r)),detailPages=detailLen/p.perPage,
       percent=Math.min(100,Math.round(draftLen/targetChars*100)),
       distribution=subjectAllocation(r), parts=distribution.weights.map((w,i)=>i<3?Math.round(p.pages*w*10)/10:0);
 parts[3]=Math.round((p.pages-parts[0]-parts[1]-parts[2])*10)/10;
 const options=Array.from({length:12},(_,i)=>`<option value="${i+1}" ${p.pages===i+1?'selected':''}>${i+1}장</option>`).join('');
 const density=[300,400,500,600,700,800].map(x=>`<option value="${x}" ${p.perPage===x?'selected':''}>${x}자/장</option>`).join('');
 const detailedStatus=r.sourceOnly?'<span>원문 연습 항목 · 기존 상세답안 없음</span>':`<span>기존 상세 학습답안 ${detailLen.toLocaleString('ko-KR')}자 ≈ ${oneDecimal(detailPages)}장 환산 · <strong>${detailPages<p.pages?'목표 분량 미달 · 내용 보강 필요':'분량상 목표 도달 · 내용검증 별도'}</strong></span>`;
 const allocation=lock?'':`<div class="n1077-alloc" aria-label="과목별 분량 배분 예시">${distribution.names.map((n,i)=>`<div><b>${esc(n)}</b><span>약 ${oneDecimal(parts[i])}장</span></div>`).join('')}</div>`;
 return `<section class="n1077-plan" aria-label="배점별 답안지 목표 분량"><div class="n1077-plan-header"><h3>답안지 목표 분량 · ${esc(r.points)}점</h3><span class="n1077-goal">목표 ${p.pages}장</span></div><p class="n27-note"><b>권장 범위 ${p.range}</b> · 이 수치는 사용자 설정 학습 목표이며 공식 채점·답안지 분량 규정이 아닙니다.</p><div class="n1077-controls"><label>목표 장수<select id="n1077-pages">${options}</select></label><label>1장 환산 글자 수<select id="n1077-per-page">${density}</select></label></div><p class="n27-note">손글씨 글자 크기·줄 간격에 따라 실제 장수는 달라집니다. 본인의 답안지 작성량에 맞게 환산 기준을 조정하세요.</p>${allocation}<div class="n1077-progress" role="group" aria-label="작성량 목표 달성도"><div class="n1077-progress-text" id="n1077-progress-text"><b>내 작성 ${draftLen.toLocaleString('ko-KR')}자</b> · 약 ${oneDecimal(draftPages)}장 / ${p.pages}장 · 분량 기준 ${percent}%</div><div class="n1077-meter"><div id="n1077-meter-fill" style="width:${percent}%"></div></div><small>작성량 지표일 뿐 채점점수·답안 충실도가 아닙니다.</small></div>${!lock?`<p class="n1077-detail-status">${detailedStatus}</p>`:''}</section>`;
}
function updateWritingProgress(r){
 const p=writingPlan(r),len=lengthOf(saved.drafts[r.id]||''),ratio=Math.min(100,Math.round(len/(p.pages*p.perPage)*100));
 const t=root.querySelector('#n1077-progress-text'),f=root.querySelector('#n1077-meter-fill');
 if(t)t.textContent=`내 작성 ${len.toLocaleString('ko-KR')}자 · 약 ${oneDecimal(len/p.perPage)}장 / ${p.pages}장 · 분량 기준 ${ratio}%`;
 if(f)f.style.width=ratio+'%';
}

const qAudit=window.N1075_AUDIT||{items:{},academic:{},laws:{},cases:{}};
// V10.7.6: topic-aware learning guidance, research and law enacted-text review remain HOLD.
const ev1076=window.N1076_EVIDENCE||{academic:{},legal:{}};
function evidence1076Panel(r){
 const a=ev1076.academic?.[r.id], l=ev1076.legal?.[r.id]; if(!a&&!l)return '';
 if(a){
   const outline=(a.answerOutline||[]).map(p=>`<li>${esc(p)}</li>`).join('');
   const t=a.table||{};
   const table=t.headers?.length?`<div class="n1073-table-scroll" tabindex="0" role="region" aria-label="문항별 학습 비교표"><table class="n1073-table"><thead><tr>${t.headers.map(h=>`<th scope="col">${esc(h)}</th>`).join('')}</tr></thead><tbody>${(t.rows||[]).map(row=>`<tr>${row.map(x=>`<td>${esc(x)}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`:'';
   return `<section class="n1076-evidence" aria-label="V10.7.6 이론·원전 연계 학습"><details open><summary><strong>V10.7.6 · 문항별 이론·비교표·서술답안 보강</strong> <span class="n27-tag hold">학습 초안</span></summary><h4>${esc(a.title)}</h4><p class="n27-note">원전과의 연결 상태: ${esc(a.relation)} · 기존 상세답안 본문은 그대로입니다.</p><ol class="n1076-outline">${outline}</ol>${table}<p><b>핵심 두음자:</b> ${esc(a.mnemonic)}</p><p class="n27-note"><b>출처·내용 유의:</b> ${esc(a.caution)}</p><p class="n1074-caution">서술안·표는 시험문제의 핵심 논점을 정리한 학습 보조자료이며 채점기준이나 공식 모범답안이 아닙니다.</p></details></section>`;
 }
 const links=(l.officialLinks||[]).map(([title,url])=>`<li><a href="${esc(url)}" target="_blank" rel="noopener noreferrer">${esc(title)}</a></li>`).join('');
 return `<section class="n1076-evidence" aria-label="V10.7.6 법률근거 점검"><details open><summary><strong>V10.7.6 · 쟁점별 법령·판례 적용시점 점검</strong> <span class="n27-tag hold">시행본·판례 HOLD</span></summary><h4>이 문항의 핵심 법적 쟁점</h4><p>${esc(l.issue)}</p><p><b>조문 후보:</b> ${esc(l.candidateArticles.join(' · '))}</p><p><b>${esc(l.examYear)}년 2차 시험:</b> ${esc(l.examDate)}</p><p class="n27-note">조문 번호는 참고 후보입니다. 첨부 링크의 현행·참고 시행본이 시험 당시 적용법이라는 뜻이 아닙니다.</p><ul class="n1076-links">${links}</ul><h4>시험 당시 법리 검토</h4><ol class="n1076-outline">${l.review.map(x=>`<li>${esc(x)}</li>`).join('')}</ol>${l.caseWarning?`<p class="n1074-caution">${esc(l.caseWarning)}</p>`:''}<p class="n1074-caution">시행 당시 조문 원문 및 직접 판례 대조 미완료 · 공식 답안·사건번호 자동 생성하지 않음.</p></details></section>`;
}
function qualityAuditPanel(r){
 const x=qAudit.items?.[r.id];if(!x)return '';
 const a=(x.academicRefs||[]).map(id=>qAudit.academic?.[id]).filter(Boolean);
 const l=(x.lawRefs||[]).map(id=>qAudit.laws?.[id]).filter(Boolean);
 const c=(x.caseRefs||[]).map(id=>qAudit.cases?.[id]).filter(Boolean);
 const refs=a.map(y=>`<li><b>${esc(y.author)} (${esc(y.year)})</b> · <i>${esc(y.title)}</i> · ${esc(y.publication)} · <a target="_blank" rel="noopener noreferrer" href="${esc(y.url)}">서지 확인</a><small>${esc(y.focus)}</small></li>`).join('');
 const laws=l.map(y=>`<li><a href="${esc(y.url)}" target="_blank" rel="noopener noreferrer">${esc(y.title)}</a> · <b>${esc(y.effective)}</b><small>${esc(y.warning)}</small></li>`).join('');
 const cases=c.map(y=>`<li><a href="${esc(y.url)}" target="_blank" rel="noopener noreferrer">${esc(y.title)}</a> · ${esc(y.date)}<small>${esc(y.warning)}</small></li>`).join('');
 const aid=qAudit.aids?.[r.id];
 const aidHtml=aid?`<div class="n1075-aid"><h4>${esc(aid.label)} · 학습용 비교표</h4><div class="n1073-table-scroll"><table class="n1073-table"><thead><tr>${aid.headers.map(y=>`<th>${esc(y)}</th>`).join('')}</tr></thead><tbody>${aid.rows.map(row=>`<tr>${row.map(y=>`<td>${esc(y)}</td>`).join('')}</tr>`).join('')}</tbody></table></div><p><b>두음자 연결:</b> ${esc(aid.mnemonic)}</p><p class="n27-note">${esc(aid.caution)}</p></div>`:'';
 const note=x.legal?'법령은 참고 후보이며 시험 당시 시행본·관련 판례의 직접성은 HOLD입니다.':'학술 저자·연도는 서지 참고자료입니다. 이 문항에 대한 학설 적용은 HOLD입니다.';
 const want=('<ul class="n1075-demand">'+(x.requirements||[]).map(y=>`<li>${esc(y)}</li>`).join('')+'</ul>');
 const checks=(x.checks||[]).map(y=>`<li>${esc(y)}</li>`).join('');
 return `<section class="n1075-audit" aria-label="문항별 근거·답안 충실도 점검"><details open><summary><b>V10.7.5 · 문항별 근거·답안 충실도 점검</b> <span class="n27-tag hold">내용검증 HOLD</span></summary><p class="n27-note">${esc(r.year)}년 ${esc(r.subject)} · ${esc(r.points)}점 · 기존 답안 원문은 변경하지 않았습니다.</p><h4>원문에서 추출한 요구 문구</h4>${want}<p class="n27-note">자동 추출 문구입니다. 원본 PDF의 문장·물음 번호·배점과 직접 대조하세요.</p>${aidHtml}${a.length?`<h4>학자·원전 서지 후보 (${a.length})</h4><ul class="n1075-sources">${refs}</ul>`:x.legal?'':'<p class="n27-note">이 문항에 직접 연결된 검증 서지 후보는 없습니다. 학자·연도 임의 삽입 금지.</p>'}${l.length?`<h4>관련 법령 원문 링크 (${l.length})</h4><ul class="n1075-sources">${laws}</ul>`:''}${c.length?`<h4>판례 검토 후보 (직접 적용 미검증)</h4><ul class="n1075-sources">${cases}</ul>`:''}<h4>답안 품질 확인 순서</h4><ol class="n1075-checks">${checks}</ol><p class="n1074-caution"><b>현재 판정:</b> ${esc(note)} 법률·학술 승인 또는 채점 점수가 아닙니다.</p></details></section>`;
}
function curatedQualityPanel(r){
 const q=qualityFor(r);if(!q)return '';
 const link=q.source?`<p class="n27-note">참고 서지: ${esc(q.source.author)} (${esc(q.source.year)}), <i>${esc(q.source.title)}</i>. <a href="${esc(q.source.url)}" target="_blank" rel="noopener noreferrer">서지 확인</a>. 판본·사안 적용은 개인 검토 필요</p>`:'';
 return `<section class="n1074-curated" aria-label="문항별 답안 보강자료"><h3>문항별 답안 보강 · 학습용 비교표</h3><p class="n27-note">${esc(q.label)} · 실제 내용이 있는 학습용 도표입니다. 공식 출제·채점표 또는 원전의 원본 도표가 아닙니다.</p><div class="n1073-table-scroll" role="region" tabindex="0" aria-label="보강 이론 비교표"><table class="n1073-table"><thead><tr>${q.headers.map(v=>`<th scope="col">${esc(v)}</th>`).join('')}</tr></thead><tbody>${q.rows.map(row=>`<tr>${row.map(v=>`<td>${esc(v)}</td>`).join('')}</tr>`).join('')}</tbody></table></div>${q.improvedDraft&&pane==='detail'?`<details class="n1074-improved" open><summary>보강 학습답안 보기 (기존 원본 유지)</summary><div class="n27-answer">${esc(q.improvedDraft)}</div></details>`:''}<p><strong>암기 연결:</strong> ${esc(q.mnemonicHint||'')}</p><p class="n1074-caution"><strong>답안 검토 주의:</strong> ${esc(q.caution||'개별 문항의 원전과 적용 관계를 점검하세요.')}</p>${link}</section>`;
}


// V10.7.8: author-reviewed candidate expansions in a separate, non-destructive module.
// These texts do not replace the 128 original answers or imply official grading.
const expandedSet=window.N1078_ESSAYS?.items||{};
function expandedPanel(r,lock){
 if(lock||r.sourceOnly||pane!=='detail')return '';
 const x=expandedSet[r.id];if(!x)return '';
 const plan=writingPlan(r),n=x.chars||0,pc=Math.min(100,Math.round(n/(plan.pages*plan.perPage)*100));
 const tr=x.table,table=tr?`<div class="n1078-table-scroll" role="region" tabindex="0" aria-label="문항별 답안 비교표"><table class="n1073-table"><thead><tr>${tr.headers.map(y=>`<th scope="col">${esc(y)}</th>`).join('')}</tr></thead><tbody>${tr.rows.map(row=>`<tr>${row.map(v=>`<td>${esc(v)}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`:'';
 const sources=(x.sources||[]).length?`<details><summary>원전·참고 문헌 (${x.sources.length}건) · 서지 확인</summary><ul>${x.sources.map(y=>`<li>${esc(y.author)} (${esc(y.year)}). <i>${esc(y.title)}</i>. <a href="${esc(y.url)}" target="_blank" rel="noopener noreferrer">원문·서지 확인</a></li>`).join('')}</ul><p class="n27-note">서지 사실 확인은 각 문항 답안의 학술적 승인과 다릅니다.</p></details>`:'';
 return `<section class="n1078-expanded" aria-label="V10.7.8 실제 내용 확장 학습답안"><div class="n1078-head"><h3>심화 논술답안 · 내용 확장 학습 초안</h3><span class="n27-tag hold">공식 답안 아님 · 내용 검증 HOLD</span></div><p class="n27-note">${esc(x.year)}년 ${esc(x.subject)} · ${esc(x.points)}점 · ${esc(x.title)}. 기존 원본 초안과 분리 보존됩니다.</p><p class="n1078-length">보강 답안 ${n.toLocaleString('ko-KR')}자 ≈ ${(n/plan.perPage).toFixed(1)}장 · 설정 목표 ${plan.pages}장 (${pc}% 분량). <strong>분량 달성도는 채점·내용 검증과 무관</strong></p>${x.parts.map((p,i)=>`<section class="n1078-part"><h4>${esc(p.heading)}</h4><div class="n27-answer">${esc(p.text)}</div></section>`).join('')}${table}<p class="n1074-caution">${esc(x.caution)}</p>${sources}</section>`;
}

function answerGuide(r){const q=qualityFor(r);if(q)return curatedAnswerGuide(r,q);const legal=isLegal(r),source=sourceRequirements(r),heads=draftHeadingCandidates(r);
 const blocks=legal?[
  ['쟁점','어떤 권리·요건·쟁점을 물었는가?',/문제|쟁점|소재|서설|의의/],
  ['법리·판례','시험 당시 적용 법령·판례 및 견해를 확인했는가?',/법리|판례|법률|법규|기준|요건|학설|규범/],
  ['사안포섭','제시된 사실관계에 판단요소를 적용했는가?',/포섭|사안|적용|검토|분석|판단|비교/],
  ['결론','질문에 답하는 결론과 근거를 제시했는가?',/결론|소결|종합|해결|결과/]
 ]:[
  ['요구사항','물음의 요구 수량·비교 기준·배점을 분리했는가?',/문제|요구|서론|개념|의의/],
  ['개념·이론','모형·이론·정의와 가정을 정확히 썼는가?',/개념|이론|정의|모형|기준|가정/],
  ['분석·적용','사례·수식·그래프·비교를 문제 조건에 맞게 전개했는가?',/분석|적용|비교|검토|계산|수식|평가/],
  ['결론','요구사항에 대응한 결론을 작성했는가?',/결론|소결|종합|시사점|결과/]
 ];
 const checks=saved.checks[r.id]||{};
 return `<section class="n107-answer-plan n1072-answer-flow" aria-label="원문 요구사항과 답안 연결"><h3>원본문제 요구사항 → 4단계 답안 연결</h3><p>배점 ${esc(r.points)} · <strong>자동 구조안내 · 개인 확인용</strong>으로, 실제 출제·채점기준이나 판례 검증 결과가 아닙니다.</p><div class="n1072-req"><strong>문제에서 추출한 요구사항 (원본 전사 대조 필요)</strong>${source.length?source.map(t=>`<p>${esc(t)}</p>`).join(''):'<p>요구사항을 원본 PDF에서 확인해 주세요.</p>'}</div><div class="n1072-flow-grid">${blocks.map(([title,question,re])=>{const key='flow-'+title;const matches=heads.filter(h=>re.test(h)).slice(0,2);return `<section class="n1072-stage"><h4>${esc(title)}</h4><p>${esc(question)}</p><small>${matches.length?'기존 답안 초안의 소제목 후보: '+esc(matches.join(' / ')):'이 단계에 맞는 소제목은 직접 대조하세요.'}</small><label class="n1072-stage-check"><input type="checkbox" data-flow-check="${esc(key)}" ${checks[key]?'checked':''}> 직접 원문·답안을 대조함</label></section>`;}).join('')}</div></section>`;
}
function memoryBody(r){const sections=sectionsFor(r);
 return `<section class="n107-memory-area" aria-label="두음자 암기 학습"><h3>키워드·두음자 암기실 · 3개씩 묶음</h3><p class="n27-note">자동 후보는 <strong>검토 전 학습자료</strong>입니다. 원본·법령·판례를 대조하고 수정하세요. 아래 회상률은 <strong>순서별 문자열 일치율</strong>이며 내용 정답률이나 채점기준이 아닙니다.</p>${sections.map((s,i)=>{const k=mnemonicKey(r,i),c=cardFor(r,s,i),words=keywordsFrom(c.words),chunks=chunk3(words),ac=acronymOf(words),hide=!!recallHidden[k],review=c.review==='known'?'암기함':c.review==='retry'?'복습 필요':'미점검';const score=Number.isFinite(c.lastAccuracy)?`<p class="n1072-last-score" role="status">최근 회상 문자열 일치율 <strong>${c.lastAccuracy}%</strong> · 연습 ${Number(c.recallAttempts)||0}회 · 개념 이해 및 실제 채점과 별개</p>`:'';return `<article class="n107-memory-card" data-card="${esc(k)}"><h4>${esc(s.title||'핵심어')}</h4><div class="n27-actions"><button type="button" class="btn" data-mnem-suggest="${esc(k)}">자동 후보 불러오기</button><small class="n27-note">법령·판례 검증 전 학습용 키워드</small></div><label>핵심 키워드 (쉼표 또는 공백 있는 · 로 구분)<textarea data-mnem-words="${esc(k)}" rows="2" maxlength="1200" placeholder="예: 통합, 순응, 지배, 회피, 타협">${esc(c.words||'')}</textarea></label><div class="n107-acronym"><span>나의 두음자</span><strong class="n107-initials">${esc(ac||'키워드를 입력하세요')}</strong></div><ol class="n1072-groups" aria-label="세 개씩 나눈 두음자">${chunks.map((g,j)=>`<li><span>${j+1}묶음</span><strong>${esc(acronymOf(g))}</strong><small>${j*3+1}~${j*3+g.length}번</small></li>`).join('')||'<li>키워드 입력 후 묶음 생성</li>'}</ol><div class="n107-recall"><span class="n107-recall-words">${hide?'핵심어를 가렸습니다. 두음자만 보고 순서대로 회상하세요.':esc(words.join(' · ')||'키워드를 입력하면 암기카드가 생성됩니다.')}</span><button class="btn" type="button" data-recall-toggle="${esc(k)}" aria-pressed="${hide}">${hide?'정답 키워드 펼치기':'핵심어 가리고 회상'}</button></div>${hide?`<div class="n1072-recall-work"><label>기억나는 핵심어를 원래 순서대로 입력하세요<textarea data-recall-answer="${esc(k)}" rows="3" placeholder="쉼표로 구분하여 입력 · 순서별 문자 일치로 확인">${esc(recallInput[k]||'')}</textarea></label><button class="btn" type="button" data-recall-grade="${esc(k)}" ${words.length?'':'disabled'}>내 회상률 확인</button><small>회상 내용 자체는 저장하지 않으며 최근 일치율만 기록합니다.</small></div>`:''}${score}<label>연상문장 · 암기팁 (직접 작성)<textarea data-mnem-story="${esc(k)}" rows="2" maxlength="900" placeholder="내 기억에 남는 두음자 문장을 적어보세요.">${esc(c.story||'')}</textarea></label><div class="n107-review-buttons"><button class="btn ${c.review==='known'?'n1072-selected':''}" aria-pressed="${c.review==='known'}" type="button" data-mnem-rate="known" data-mnem-key="${esc(k)}">암기함</button><button class="btn ${c.review==='retry'?'n1072-selected':''}" aria-pressed="${c.review==='retry'}" type="button" data-mnem-rate="retry" data-mnem-key="${esc(k)}">복습 필요</button><small data-review-status="${esc(k)}">카드 상태: ${esc(review)}</small></div></article>`;}).join('')}<p class="n27-note">문항 전체 복습 완료: <strong>${questionReviewed(r)?'완료':'미완료'}</strong> · 개별 암기카드가 모두 ‘암기함’일 때 문항 완료로 동기화됩니다.</p></section>`;
}
function keywordComparison(r){const sections=r.sections?.length?r.sections:[{title:'직접 만든 키워드'}];
 const groups=sections.map((section,i)=>{const c=cardFor(r,section,i),words=keywordsFrom(c.words),mine=saved.drafts[r.id]||'';if(!words.length)return '';
 const matched=words.filter(w=>mine.includes(w));const unmatched=words.filter(w=>!mine.includes(w));return `<div class="n107-keyword-result"><b>${esc(section.title||'핵심어')}</b><p>문자열 포함 ${matched.length}/${words.length} · 의미·동의어·정답 여부는 판정하지 않습니다.</p><div>${words.map(w=>`<span class="n107-word ${mine.includes(w)?'seen':'unseen'}">${esc(w)} ${mine.includes(w)?'✓':'—'}</span>`).join('')}</div></div>`;}).filter(Boolean);
 return groups.length?`<section class="n107-keyword-review"><h3>내 답안의 키워드 확인</h3>${groups.join('')}</section>`:'';
}
function historicalSourcePanel(r){
 const qs=r.historicalSource;
 if(!qs?.length)return '';
 const file=window.NOMUSA_AUTO_SOURCE.sources.find(entry=>entry.year===r.year);
 const describe=q=>[
   q.points===null?'배점 HOLD':q.points+'점'+(q.pointBasis.startsWith('sum_')?' (표기 배점 합산)':''),
   '추출문 '+q.lines.join('–')+'행',
   q.graphPrompt?'도식·그래프 요구':'',
   q.formulaPrompt?'수식·조건 요구 후보':''
 ].filter(Boolean).join(' · ');
 return `<details class="n27-note" aria-label="문항별 원본 위치" style="overflow-wrap:anywhere"><summary>문항별 원본 위치와 배점</summary><p>${esc(file.filename)} · ${qs[0].page?'PDF '+qs[0].page+'쪽':'HWP 페이지 HOLD'} · 수식·그래프 시각 대조 HOLD</p><ol>${qs.map(q=>`<li>문제 ${esc(q.number)} · ${esc(describe(q))}${q.subquestions.length?`<ul>${q.subquestions.map(p=>`<li>소문항 ${esc(p.number)} · ${esc(describe(p))}</li>`).join('')}</ul>`:''}</li>`).join('')}</ol></details>`;
}
function sourcePanel(r){const rel=typeof r.pdfPath==='string'&&/^source_pdf\/\d{4}\/[a-zA-Z0-9_-]+\.pdf$/.test(r.pdfPath)?'../'+r.pdfPath:null;
 const link=rel?`<a href="${esc(rel)}#page=${Number(r.pdfPage)||1}" target="_blank" rel="noopener noreferrer">PDF 새 창으로 열기</a>`:`<a href="https://www.q-net.or.kr/cst003.do?gId=05&amp;gSite=L&amp;id=cst00309" target="_blank" rel="noopener noreferrer">Q-Net 공식 문제지 자료실</a>`;
 const check=saved.sourceChecks[r.id]===true;
 return `<section class="n107-source-panel" aria-label="원본문제지 검토"><h3>원본문제지 확인</h3><p class="n27-note">${rel?'보유 PDF 파일 · 첫 페이지부터 이동 가능':'앱에 PDF가 없어 공식 자료실에서 확인 필요'}${r.pdfPageVerification?' · 세부 문항의 시작 쪽 미확정':''} / <strong>문항별 전사·수식·페이지의 독립대조는 미완료</strong></p><div class="n107-source-actions">${link} <a href="https://www.q-net.or.kr/cst003.do?gId=05&amp;gSite=L&amp;id=cst00309" target="_blank" rel="noopener noreferrer">Q-Net 공식 게시목록</a>${rel?`<button type="button" class="btn" id="n107-pdf-toggle" aria-expanded="${pdfOpen}">${pdfOpen?'PDF 화면 닫기':'화면 안에서 PDF 보기'}</button>`:''}</div>${pdfOpen&&rel?`<iframe class="n107-pdf-frame" title="${esc(r.year+'년 '+r.subject+' 원본문제지')}" src="${esc(rel)}#page=${Number(r.pdfPage)||1}&toolbar=1" loading="lazy"></iframe><p class="n27-note">모바일에서 PDF가 보이지 않으면 위의 ‘PDF 새 창으로 열기’를 이용하세요.</p>`:''}<label class="n107-source-check"><input type="checkbox" id="n107-source-checked" ${check?'checked':''}> <span>내가 원본 PDF와 문제·수식·배점을 직접 대조했습니다 (개인 학습 기록, 공식 검증 아님)</span></label></section>`;
}
// V10.7.3: research citations are bibliographic facts; topical applicability and exam-year law remain HOLD.
const refs=window.N1073_REFERENCES||{academic:[],laws:[]};
const isStudyTheory=r=>/경영조직론|인사노무관리론/.test(r.subject||'');
const refText=r=>String(r.topic||'')+' '+String(r.sourceText||'');
const matchesRef=(r,item)=>item.subjects?.some(s=>r.subject===s||(s==='노동법'&&/^노동법/.test(r.subject||''))) && item.match?.some(word=>refText(r).toLowerCase().includes(String(word).toLowerCase()));
function academicPanel(r){
  const q=qualityFor(r);const matched=(refs.academic||[]).filter(x=>matchesRef(r,x));if(q?.source&&!matched.some(x=>x.id===q.source.id))matched.unshift(q.source);
  const compareReq=/(비교|유형|장단점|구분|차이|특성)/.test(refText(r));
  const custom=saved.researchCards?.[r.id]||{};
  const tableOf=item=>{if(!item?.table)return '';const t=item.table;return `<div class="n1073-table-scroll" role="region" aria-label="${esc(item.author)} 이론 비교표" tabindex="0"><table class="n1073-table"><thead><tr>${t.headers.map(v=>`<th scope="col">${esc(v)}</th>`).join('')}</tr></thead><tbody>${t.rows.map(row=>`<tr>${row.map(val=>`<td>${esc(val)}</td>`).join('')}</tr>`).join('')}</tbody></table></div><p class="n27-note">위 도표는 출처를 바탕으로 재구성한 <b>학습용 개념표</b>이며 원문 표·공식 채점표가 아닙니다.</p>`;};
  const bibliography=matched.length?matched.map(x=>`<article class="n1073-ref-citation"><b>${esc(x.author)} (${esc(x.year)})</b><span>${esc(x.type)} · <i>${esc(x.title)}</i> · ${esc(x.publication)}</span><a href="${esc(x.url)}" target="_blank" rel="noopener noreferrer">학술지·출판사 원전 서지 열기</a>${tableOf(x)}</article>`).join(''):'<p class="n27-note">이 문항과 연결이 확인된 서지 후보가 없습니다. 학자·문헌·연도는 임의 생성하지 않습니다.</p>';
  const compareTemplate=!q&&!matched.some(x=>x.table)&&compareReq?`<details class="n1073-generic-compare"><summary>비교표 작성 틀 (내용은 직접 확인)</summary><div class="n1073-table-scroll"><table class="n1073-table"><thead><tr><th>비교 기준</th><th>첫 번째 이론·제도</th><th>두 번째 이론·제도</th><th>학자·원전·연도</th></tr></thead><tbody>${['개념·목적','구성요소·절차','강점·한계','적용·시사점'].map(v=>`<tr><th scope="row">${v}</th><td>원문 대조 후 작성</td><td>원문 대조 후 작성</td><td>출처 확인 필요</td></tr>`).join('')}</tbody></table></div></details>`:'';
  const fields=[['author','학자·저자','예: 학자명'],['title','책자·논문명','원전 제목'],['year','발표·출판연도','예: 1983'],['locator','출처 식별자·쪽수','DOI, ISBN 또는 페이지'],['note','나의 출처·적용 메모','원문과 답안 대조 메모']];
  return `<section class="n1073-ref-box n1073-academic" aria-label="학술원전 및 비교표"><h3>학술원전 · 이론비교표</h3><p class="n27-note">학자·논문·저서 및 발표연도를 표시합니다. <strong>서지 확인 ≠ 답안 적용 검증</strong>이며 이론표는 시험장 답안의 학습용 구성 예시입니다.</p>${bibliography}${compareTemplate}<details><summary>내 참고문헌·도식 검토 메모 (브라우저 자동저장)</summary><div class="n1073-note-grid">${fields.map(([key,title,hint])=>`<label>${title}<input type="text" data-scholar-field="${key}" maxlength="${key==='note'?700:220}" value="${esc(custom[key]||'')}" placeholder="${esc(hint)}"></label>`).join('')}</div></details></section>`;
}
function lawPanel(r){
 const isLabor=/^노동법/.test(r.subject||''),isAdmin=/행정쟁송법/.test(r.subject||'');
 if(!isLabor&&!isAdmin)return '';
 const links=(refs.laws||[]).filter(x=>matchesRef(r,x)).slice(0,8);
 const fallback=isLabor?'https://law.go.kr/LSW/LsiJoLinkP.do?docType=JO&joNo=006700000&languageType=KO&lsNm=%EA%B7%BC%EB%A1%9C%EA%B8%B0%EC%A4%80%EB%B2%95&paras=1':'https://www.law.go.kr/lsInfoP.do?joNo=001800&lsId=001218';
 return `<section class="n1073-ref-box n1073-legal" aria-label="관련 법령 참고"><h3>관련 법조문 참고 · ${esc(r.subject)}</h3><p class="n27-note">문제의 용어로 찾아낸 <strong>조문 후보</strong>입니다. 법조문 내용은 국가법령정보센터에서 직접 확인하세요. 현재 보이는 법령과 <strong>${r.year}년 시험 당시 시행 법령</strong>이 다를 수 있으므로 연혁·시행일 대조 전에는 답안 근거로 확정하지 않습니다.</p>${links.length?`<div class="n1073-law-list">${links.map(x=>`<div class="n1073-law-item"><b>${esc(x.act)} ${esc(x.article)} (${esc(x.title)})</b><small>${esc(x.summary)} · 사안 적용 미검증</small><p class="n1073-law-gist">법조문 요지: ${esc(x.gist||'')}<br><small>확인한 시행본 ${esc(x.effective||'미확인')} · 시험 당시 시행본 대조 필요</small></p><a href="${esc(x.url)}" target="_blank" rel="noopener noreferrer">공식 법령에서 확인</a></div>`).join('')}</div>`:`<p class="n27-note">이 문항의 자동 조문 후보가 없습니다. 주제·사건과 관련 법령을 먼저 확인하세요.</p>`}<p><a href="${esc(fallback)}" target="_blank" rel="noopener noreferrer">국가법령정보센터 본문·연혁 보기</a></p></section>`;
}
function referencePanel(r){return isStudyTheory(r)?academicPanel(r):lawPanel(r);}

const checklist=r=>{const specific=(r.sections||[]).flatMap((s,i)=>(s.reviewChecklist||[]).map((text,j)=>({key:`${i}-${j}`,title:s.title,text}))).slice(0,48);const generic=['문제의 요구사항과 배점에 맞게 논점을 나누었는지 확인','개념·법리·이론 등 핵심 근거를 직접 대조했는지 확인','구체적 사실관계·모형·수식 등을 문제에 맞게 적용했는지 확인','결론과 이유가 논리적으로 연결되는지 확인'];const stages=isLegal(r)?['쟁점','법리·판례','사안포섭','결론']:['요구사항','개념·이론','분석·적용','결론'];return [...(specific.length?specific:generic.map((text,j)=>({key:`0-${j}`,title:'공통 자기점검 · 채점기준 아님',text}))),...stages.map((title,i)=>({key:'flow-'+title,title:'원문·답안 연결 직접 확인',text:`${i+1}. ${title}`}))];};
function compactExcerpt(s){
 const raw=String(s?.detailed||'').trim();if(!raw)return '상세답안 내용 없음';
 const heads=raw.split(/(?=^\s*[ⅠⅡⅢⅣⅤⅥⅦ]\.\s)/m).map(x=>x.trim()).filter(Boolean);
 const blocks=heads.length>1?heads:raw.split(/\n\s*\n/).filter(Boolean);
 const selected=[];
 for(const b of blocks.slice(0,5)){
   const lines=b.split(/\n+/).map(x=>x.trim()).filter(Boolean);
   if(!lines.length)continue;
   // Preserve complete original sentences and case citations: do NOT truncate a precedent citation.
   const head=lines[0];
   const substantive=lines.slice(1).find(x=>x.length>=30)||lines.slice(1)[0]||'';
   selected.push([head,substantive].filter(Boolean).join('\n'));
 }
 return selected.join('\n\n')||raw.slice(0,700);
}
function compactText(s){return String(s?.compressed||'').trim()||compactExcerpt(s);}
function unifiedLearningAnswer(r){
 const expanded=expandedSet[r.id],q=qualityFor(r),plan=writingPlan(r);
 if(expanded){
  const table=expanded.table?`<div class="n1073-table-scroll" role="region" tabindex="0" aria-label="학습 비교표"><table class="n1073-table"><thead><tr>${expanded.table.headers.map(v=>`<th scope="col">${esc(v)}</th>`).join('')}</tr></thead><tbody>${expanded.table.rows.map(row=>`<tr>${row.map(v=>`<td>${esc(v)}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`:'';
  const docs=(expanded.sources||[]).length?`<details class="n1079-bibliography"><summary>학자·원전 확인 (${expanded.sources.length}건)</summary><ul>${expanded.sources.map(x=>`<li>${esc(x.author)} (${esc(x.year)}). <i>${esc(x.title)}</i> · <a href="${esc(x.url)}" target="_blank" rel="noopener noreferrer">서지 확인</a></li>`).join('')}</ul><p class="n27-note">서지정보는 답안의 내용검증·공식 승인과 다릅니다.</p></details>`:'';
  return `<section class="n1079-answer" aria-label="통합 상세 학습답안"><div class="n1079-answer-head"><h3>통합 상세 학습답안</h3><span class="n27-tag hold">심화 학습 초안 · 승인 HOLD</span></div><p class="n27-note">${esc(expanded.title)} · ${expanded.chars.toLocaleString('ko-KR')}자 · 약 ${(expanded.chars/plan.perPage).toFixed(1)}장(학습용 환산)</p>${expanded.parts.map(p=>`<section class="n1079-answer-part"><h4>${esc(p.heading)}</h4><div class="n27-answer">${esc(p.text)}</div></section>`).join('')}${table}${docs}<details><summary>이전 상세답안 초안 · 변경 전 내용 확인</summary>${r.sections.map(t=>`<h4>${esc(t.title)}</h4><div class="n27-answer">${esc(t.detailed)}</div>`).join('')}</details><p class="n27-note">기존 원본 답안은 삭제·수정하지 않았으며 이 내용은 공식 모범답안이 아닙니다.</p></section>`;
 }
 if(q?.improvedDraft){
  return `<section class="n1079-answer" aria-label="통합 상세 학습답안"><h3>통합 상세 학습답안 <small>학습 초안 · 승인 HOLD</small></h3><div class="n27-answer">${esc(q.improvedDraft)}</div><details><summary>원본 상세답안 보기</summary>${r.sections.map(t=>`<h4>${esc(t.title)}</h4><div class="n27-answer">${esc(t.detailed)}</div>`).join('')}</details></section>`;
 }
 return `<section class="n1079-answer" aria-label="통합 상세 학습답안"><h3>상세 학습답안 <small>검토 초안</small></h3>${r.sections.map(t=>`<section class="n1079-answer-part"><h4>${esc(t.title)}</h4><div class="n27-answer">${esc(t.detailed)}</div></section>`).join('')}${r.extra?`<details><summary>보충자료</summary><div class="n27-answer">${esc(r.extra)}</div></details>`:''}</section>`;
}
function modelBody(r,lock,isOnly){
 if(lock)return '<div class="n27-hidden-answer" role="status">20분 실전 진행 중: 학습답안·암기·비교를 숨겼습니다. 직접 작성만 가능합니다.</div>';
 if(pane==='memory')return memoryBody(r);
 if(isOnly)return '<section class="n1079-empty"><h3>원문 중심 직접 작성</h3><p>학습답안 HOLD · 원본문제지를 확인하고 직접 작성하세요.</p></section>';
 if(pane==='write')return '';
 if(pane==='compact')return `<section aria-label="학습용 압축답안"><h3>시험장 압축답안 <small>학습 초안</small></h3>${r.sections.map(t=>`<h4>${esc(t.title)}</h4>${!t.compressed?'<p class="n27-note">기존 상세답안 발췌 · 완성된 압축 모범답안 아님</p>':''}<div class="n27-answer">${esc(compactText(t))}</div>`).join('')}</section>`;
 if(pane==='compare')return `<section aria-label="내 답안 비교"><h3>내 답안과 학습내용 비교</h3><p class="n27-note">문자열 일치 여부는 정답 채점과 다릅니다.</p><div class="n106-compare"><div class="n106-side"><h4>내 답안</h4><div class="n106-own">${esc(saved.drafts[r.id]||'직접 작성 탭에서 답안을 작성해 주세요.')}</div></div><div class="n106-side"><h4>학습용 압축답안</h4>${r.sections.map(t=>`<h5>${esc(t.title)}</h5><div class="n27-answer">${esc(compactText(t))}</div>`).join('')}</div></div>${keywordComparison(r)}</section>`;
 return unifiedLearningAnswer(r);
}
function checklistBody(r,lock){const items=checklist(r);if(lock||!items.length||pane!=='compare'||r.sourceOnly)return '';
 const checked=saved.checks[r.id]||{},done=items.filter(x=>checked[x.key]).length;
 return `<section class="n106-checks" aria-label="자가점검 체크리스트"><h3>쟁점별 스스로 확인 <small>${done}/${items.length}개 직접 확인</small></h3><p class="n27-note">아래 체크는 본인이 직접 표시하며, 자동 채점이나 법령·판례 승인 결과가 아닙니다.</p>${items.map(x=>`<label class="n106-check"><input type="checkbox" data-check="${x.key}" ${checked[x.key]?'checked':''}><span><b>${esc(x.title)}</b> ${esc(x.text)}</span></label>`).join('')}</section>`;
}
const verifyNote='<strong>학습자료 유의:</strong> 원본 PDF의 무결성과 해설의 법률·학술 정확성은 별개입니다. 모든 기존 상세·압축답안은 학습용 검토 초안이며 공식 모범답안·채점기준이 아닙니다. 과거 연도의 원본 전사는 미검수된 경우가 있습니다.';
function detail(r,found){
 if(!r)return '<article class="n27-detail"><h2>검색 결과가 없습니다.</h2><p>연도·과목·검색어를 변경해 주세요.</p></article>';
 const isOnly=!!r.sourceOnly,lock=locked(),ix=found.findIndex(x=>x.id===r.id), plan=writingPlan(r),defaults=pageDefaults(r.points);
 const requirement=sourceRequirements(r).join('\n').trim();
 const pdf=typeof r.pdfPath==='string'&&/^source_pdf\/\d{4}\/[a-zA-Z0-9_-]+\.pdf$/.test(r.pdfPath)?'../'+r.pdfPath+'#page='+ (Number(r.pdfPage)||1):null;
 const targetLabel=plan.custom?`개인 설정 ${plan.pages}장 (기본 권장 ${defaults.pages}장)`:`권장 ${defaults.pages}장`;
 const planLabel=plan.custom&&plan.pages!==defaults.pages?`<span class="n1079-custom">사용자 선택값</span>`:'';
 return `<article class="n27-detail n1079-detail" aria-label="논술 답안 본문">
 <label class="n1079-mobile-jump">문제 선택<select id="n1079-jump">${found.map(x=>opt(x.id,`${x.year} · ${x.subject} · ${x.topic}`,r.id)).join('')}</select></label>
 <div class="n27-tags"><span class="n27-tag">${r.year}년</span><span class="n27-tag">${esc(r.subject)}</span><span class="n27-tag">${esc(r.points)}점</span><span class="n27-tag hold">${isOnly?'원문 연습':'학습용 초안 · 승인 HOLD'}</span></div>
 <h2>${esc(r.topic)}</h2>
 <div class="n27-actions n27-nav"><button class="btn" id="n27-prev" ${ix<=0?'disabled':''}>이전</button><button class="btn" id="n27-next" ${ix>=found.length-1?'disabled':''}>다음</button><button class="btn" id="n27-bookmark">${saved.bookmarks[r.id]?'★ 즐겨찾기 해제':'☆ 즐겨찾기'}</button></div>
 <section class="n1079-question" aria-label="기출문제"><div class="n1079-question-head"><h3>기출문제</h3><span class="n27-note">${esc(r.points)}점 · ${esc(targetLabel)}</span></div><div class="n1079-question-text">${esc((r.historicalSource?.length?r.sourceText:requirement)||r.sourceText||'원본 PDF에서 질문을 확인하세요.')}</div><div class="n1079-question-tools">${pdf?`<a href="${esc(pdf)}" target="_blank" rel="noopener noreferrer">원본문제지 PDF 열기</a>`:''}<span class="n27-note">문제 텍스트·배점은 원본 대조가 필요합니다.</span></div></section>
 <div class="n106-tabs n1079-tabs" role="group" aria-label="학습 단계">${panes.map(([id,title])=>`<button type="button" class="n106-tab ${pane===id?'current':''}" data-pane="${id}" aria-pressed="${pane===id}" ${lock&&id!=='write'?'disabled title="실전에서는 작성만 가능"':''}>${id==='compact'?'압축답안':id==='memory'?'암기':title}</button>`).join('')}</div>
 ${pane==='write'||lock?`<section class="n106-workspace n106-write" aria-label="나의 답안 작성"><div class="n106-work-head"><h3>내 답안 <span class="n27-note">· 자동저장</span></h3><span id="n106-count" class="n27-note">${lengthOf(saved.drafts[r.id]||'')}자</span></div><textarea id="n27-draft" rows="16" placeholder="쟁점 → 법리·이론 → 사안 적용·분석 → 결론">${esc(saved.drafts[r.id]||'')}</textarea><div class="n106-work-foot"><button type="button" class="btn" id="n106-outline">답안 틀 삽입</button><span id="n27-save-state" role="status" class="n27-note">${saved.drafts[r.id]?'저장된 답안 있음':'새 답안'}</span></div><p class="n27-note">브라우저에 자동 저장됩니다. 로그인·기기 간 동기화는 제공하지 않습니다.</p></section>`:''}
 ${modelBody(r,lock,isOnly)}
 ${!lock&&pane==='compare'?checklistBody(r,lock):''}
 ${!lock?`<details class="n1079-length" id="n1079-length"><summary>답안지 분량 · ${esc(targetLabel)} ${planLabel} <span class="n27-note">설정 변경</span></summary>${writingPlanPanel(r,lock)}<button type="button" class="btn" id="n1079-reset-length">권장 장수로 초기화</button></details>`:''}
 ${!lock?`<details class="n1079-advanced" id="n1079-advanced"><summary>원본문제지 · 근거·검증 기록 자세히 보기</summary><div class="n1079-advanced-body">${sourcePanel(r)}${historicalSourcePanel(r)}${referencePanel(r)}${evidence1076Panel(r)}${qualityAuditPanel(r)}${answerGuide(r)}${curatedQualityPanel(r)}<details class="n107-transcript"><summary>원본 추출 텍스트 전체 보기</summary><div class="n27-source">${esc(r.sourceText)}</div></details></div></details>`:''}
 <p class="n1079-disclaimer">학습용 검토 초안입니다. 공식 모범답안이나 채점기준이 아니며, 법령·판례·학술자료와의 직접 적용은 별도 확인이 필요합니다.</p>
 <div class="n27-actions"><button type="button" class="btn" id="n27-flag">${questionReviewed(r)?'복습 완료 취소':'복습 완료 표시'}</button></div></article>`;
}
function render(){stopExpired();if(locked()&&pane!=='write')pane='write';const found=getRows();if(!found.some(r=>r.id===selected)){selected=found[0]?.id||null;pdfOpen=false;}const current=selected?byId.get(selected):null;
 const done=Object.keys(saved.flags).filter(k=>byId.has(k)&&questionReviewed(byId.get(k))).length;
 const drafts=Object.keys(saved.drafts).filter(k=>byId.has(k)&&saved.drafts[k]?.trim()).length;
 root.innerHTML=`<div class="n27-alert"><strong>2007~2026년 공인노무사 2차 통합 학습</strong> · ${rows.length}개 연습 항목 중 상세·압축답안 제공 ${answerCount}개, 원문 중심 직접작성 ${sourceCount}개. 승인된 공식 모범답안은 0개입니다.</div>
 <div class="n27-metrics"><div><strong>${years.length}</strong><small>수록 연도</small></div><div><strong>${rows.length}</strong><small>연습 항목</small></div><div><strong>${drafts}</strong><small>내 답안 저장</small></div><div><strong>${done} · ${Math.round(100*done/rows.length)}%</strong><small>복습 완료</small></div></div>
 <div class="n27-panel"><div class="n27-filters"><label>연도<select id="n27-year">${opt('all','전체 연도',year)}${years.map(y=>opt(String(y),String(y)+'년',year)).join('')}</select></label><label>과목<select id="n27-subject">${opt('all','전체 과목',subject)}${subjects.map(s=>opt(s,s,subject)).join('')}</select></label><label>학습자료<select id="n27-type">${opt('all','모두',answerType)}${opt('draft','답안 초안 있음',answerType)}${opt('source','원문 연습',answerType)}</select></label><label>검색<input type="search" id="n27-find" placeholder="문제·논점·연도별 검색" value="${esc(query)}"></label></div>
 <div class="n27-actions"><button type="button" class="btn primary" id="n27-timer">${locked()?'실전 종료':'20분 실전 시작'}</button><span id="n27-clock" class="n27-note">${locked()?'실전 진행 중':'학습 모드'}</span><button type="button" class="btn" id="n27-random" ${found.length?'':'disabled'}>무작위 문제</button><button type="button" class="btn" id="n27-export">기록 JSON 내보내기</button><label class="btn" style="cursor:pointer">기록 가져오기<input type="file" id="n27-import" accept=".json,application/json" hidden></label></div>
 <p class="n27-status" id="n27-status" role="status">${esc(message)}</p><div class="n27-cols"><aside class="n27-list" aria-label="문제 목록"><p class="n27-note">조건에 맞는 문제 ${found.length}개 · 점수 확정 및 공식 채점 아님</p>${found.map(r=>`<button type="button" class="n27-choice ${selected===r.id?'active':''}" data-answer="${esc(r.id)}"><b>${r.year} · ${esc(r.subject)}</b> ${esc(r.topic)}<small>${r.sourceOnly?'원문 연습':'학습 초안'}${questionReviewed(r)?' · 복습완료':''}${saved.bookmarks[r.id]?' · ★':''}${saved.drafts[r.id]?.trim()?' · 작성중':''}</small></button>`).join('')}</aside>${detail(current,found)}</div></div>`;
 root.querySelector('#n27-year').onchange=e=>{year=e.target.value;render()};
 root.querySelector('#n27-subject').onchange=e=>{subject=e.target.value;render()};
 root.querySelector('#n27-type').onchange=e=>{answerType=e.target.value;render()};
 root.querySelector('#n27-find').oninput=e=>{const p=e.target.selectionStart;query=e.target.value;render();const x=root.querySelector('#n27-find');x.focus();x.setSelectionRange(p,p)};
 const jump=root.querySelector('#n1079-jump');if(jump)jump.onchange=e=>{selected=e.target.value;pdfOpen=false;render();};
 root.querySelectorAll('[data-answer]').forEach(el=>el.onclick=()=>{selected=el.dataset.answer;pdfOpen=false;render()});
 root.querySelectorAll('[data-pane]').forEach(el=>el.onclick=()=>{if(locked()&&el.dataset.pane!=='write')return;pane=el.dataset.pane;render();if(pane==='write')root.querySelector('#n27-draft')?.focus();});
 const resetPg=root.querySelector('#n1079-reset-length');if(resetPg&&current)resetPg.onclick=()=>{saved.writingPlans[current.id]={...(saved.writingPlans[current.id]||{}),perPage:writingPlan(current).perPage};delete saved.writingPlans[current.id].pages;store();render();};
 const pg=root.querySelector('#n1077-pages'),pp=root.querySelector('#n1077-per-page');
 if(pg&&pp&&current){
  const saveLength=()=>{const old=writingPlan(current);saved.writingPlans[current.id]={pages:Number(pg.value)||old.pages,perPage:Number(pp.value)||old.perPage};store();render();};
  pg.onchange=saveLength;pp.onchange=saveLength;
 }
 const pdfToggle=root.querySelector('#n107-pdf-toggle');if(pdfToggle)pdfToggle.onclick=()=>{pdfOpen=!pdfOpen;render()};
 root.querySelectorAll('[data-scholar-field]').forEach(el=>el.oninput=()=>{if(!current||!isStudyTheory(current))return;if(!saved.researchCards||typeof saved.researchCards!=='object')saved.researchCards={};const old=saved.researchCards[current.id]||{};old[el.dataset.scholarField]=el.value;saved.researchCards[current.id]=old;store();});
 const sourceCheck=root.querySelector('#n107-source-checked');if(sourceCheck&&current)sourceCheck.onchange=e=>{saved.sourceChecks[current.id]=e.target.checked;store();};
 root.querySelectorAll('[data-mnem-suggest]').forEach(el=>el.onclick=()=>{if(!current)return;const k=el.dataset.mnemSuggest,i=Number(k.split('::').at(-1)),sections=current.sections?.length?current.sections:[{title:'내 키워드'}],section=sections[i];if(!section)return;const suggestions=seedKeywords(current,section,i);if(!suggestions.length){toast('이 항목은 자동 키워드 후보가 없습니다. 원본에서 직접 입력해 주세요.');return;}const previous=cardFor(current,section,i);if(previous.words?.trim()&&previous.words.trim()!==suggestions.join(', ')&&!confirm('기존에 저장한 키워드를 자동 후보로 바꾸시겠습니까?'))return;saved.memoryCards[k]={...previous,words:suggestions.join(', ')};store();render();});
 root.querySelectorAll('[data-mnem-words],[data-mnem-story]').forEach(el=>el.oninput=()=>{const k=el.dataset.mnemWords||el.dataset.mnemStory;if(!k||!current)return;const i=Number(k.split('::').at(-1)),section=(current.sections?.length?current.sections:[{title:'내 키워드'}])[i];if(!section)return;const c={...cardFor(current,section,i)};if(el.hasAttribute('data-mnem-words')){c.words=el.value;delete c.lastAccuracy;delete c.lastRecallAt;}else c.story=el.value;saved.memoryCards[k]=c;store();if(el.hasAttribute('data-mnem-words')){const node=el.closest('.n107-memory-card');if(node){const words=keywordsFrom(el.value);node.querySelector('.n1072-last-score')?.remove();recallInput[k]='';node.querySelector('.n107-initials').textContent=acronymOf(words)||'키워드를 입력하세요';const groups=node.querySelector('.n1072-groups');if(groups)groups.innerHTML=chunk3(words).map((g,j)=>`<li><span>${j+1}묶음</span><strong>${esc(acronymOf(g))}</strong><small>${j*3+1}~${j*3+g.length}번</small></li>`).join('')||'<li>키워드 입력 후 묶음 생성</li>'; const hint=node.querySelector('.n107-recall-words');if(hint&&!recallHidden[k])hint.textContent=words.join(' · ')||'키워드를 입력하면 암기카드가 생성됩니다.';}}});
 root.querySelectorAll('[data-recall-toggle]').forEach(el=>el.onclick=()=>{const k=el.dataset.recallToggle;recallHidden[k]=!recallHidden[k];if(recallHidden[k])recallInput[k]='';render()});
 root.querySelectorAll('[data-recall-answer]').forEach(el=>el.oninput=()=>{recallInput[el.dataset.recallAnswer]=el.value;});
 root.querySelectorAll('[data-recall-grade]').forEach(el=>el.onclick=()=>{if(!current)return;const k=el.dataset.recallGrade,i=Number(k.split('::').at(-1)),section=sectionsFor(current)[i];if(!section)return;const card={...cardFor(current,section,i)};const scored=recallAccuracy(keywordsFrom(card.words),recallInput[k]||'');card.recallAttempts=Math.min(100000,(Number(card.recallAttempts)||0)+1);card.recallHits=Math.min(100000,(Number(card.recallHits)||0)+scored.matches);card.lastAccuracy=scored.percent;card.lastRecallAt=new Date().toISOString();saved.memoryCards[k]=card;store();render();toast(`자가회상 문자열 일치 ${scored.matches}/${scored.total} · ${scored.percent}% (정답 채점 아님)`);});
 root.querySelectorAll('[data-flow-check]').forEach(el=>el.onchange=()=>{if(!current)return;if(!saved.checks[current.id])saved.checks[current.id]={};saved.checks[current.id][el.dataset.flowCheck]=el.checked;store();});
 root.querySelectorAll('[data-mnem-rate]').forEach(el=>el.onclick=()=>{const k=el.dataset.mnemKey,sec=Number(k.split('::').at(-1)),section=(current.sections?.length?current.sections:[{title:'내 키워드'}])[sec];if(!section)return;const c={...cardFor(current,section,sec),review:el.dataset.mnemRate};saved.memoryCards[k]=c;syncQuestionReview(current);store();render()});
 const ta=root.querySelector('#n27-draft');if(ta&&current){ta.oninput=e=>{saved.drafts[current.id]=e.target.value;const ok=store();const x=root.querySelector('#n27-save-state');if(x)x.textContent=ok?'임시저장 완료':'저장 불가';const counter=root.querySelector('#n106-count');if(counter)counter.textContent=Array.from(e.target.value).length+'자';updateWritingProgress(current);};
 root.querySelector('#n106-outline').onclick=()=>{if(ta.value.trim()&&!confirm('현재 작성한 답안 뒤에 구성 틀을 추가하시겠습니까?'))return;const addition=outline(current);ta.value+=(ta.value.trim()?'\n\n':'')+addition;ta.dispatchEvent(new Event('input',{bubbles:true}));ta.focus();};
 root.querySelectorAll('[data-check]').forEach(el=>el.onchange=()=>{if(!saved.checks[current.id])saved.checks[current.id]={};saved.checks[current.id][el.dataset.check]=el.checked;store();render()});
 root.querySelector('#n27-flag').onclick=()=>{setQuestionReviewed(current,!questionReviewed(current));store();render()};
 root.querySelector('#n27-bookmark').onclick=()=>{saved.bookmarks[current.id]=!saved.bookmarks[current.id];store();render()};
 const ix=found.findIndex(r=>r.id===current.id);
 root.querySelector('#n27-prev').onclick=()=>{if(ix>0){selected=found[ix-1].id;render()}};
 root.querySelector('#n27-next').onclick=()=>{if(ix<found.length-1){selected=found[ix+1].id;render()}};
 }
 root.querySelector('#n27-random').onclick=()=>{if(found.length){const alternatives=found.filter(r=>r.id!==selected); selected=(alternatives.length?alternatives:found)[Math.floor(Math.random()*(alternatives.length||found.length))].id;render()}};
 root.querySelector('#n27-export').onclick=download;
 root.querySelector('#n27-timer').onclick=()=>{if(locked()){if(!confirm('실전을 종료하고 답안을 표시하시겠습니까?'))return;saved.examEnd=0;pane='detail';}else{saved.examEnd=Date.now()+20*60*1000;pane='write';}store();render()};
 root.querySelector('#n27-import').onchange=async e=>{const file=e.target.files[0];if(!file)return;try{if(file.size>3000000)throw Error('3MB를 초과하는 백업');const x=JSON.parse(await file.text());if(x.schema!=='nomusa-rc27-essay-records/1'||!x.saved||typeof x.saved.drafts!=='object'||typeof x.saved.flags!=='object')throw Error('백업 형식 불일치');if(!confirm('현재 답안 기록을 덮어쓰시겠습니까?'))return;const safeDrafts={},safeFlags={},safeBookmarks={},safeChecks={};for(const [k,v] of Object.entries(x.saved.drafts)){if(byId.has(k)&&typeof v==='string'&&v.length<300000)safeDrafts[k]=v;}for(const [k,v] of Object.entries(x.saved.flags)){if(byId.has(k)&&typeof v==='boolean')safeFlags[k]=v;}for(const [k,v] of Object.entries(x.saved.bookmarks||{})){if(byId.has(k)&&typeof v==='boolean')safeBookmarks[k]=v;}for(const [k,v] of Object.entries(x.saved.checks||{})){if(byId.has(k)&&v&&typeof v==='object'&&!Array.isArray(v)){const valid=new Set(checklist(byId.get(k)).map(c=>c.key));safeChecks[k]={};for(const [ck,cv] of Object.entries(v)){if(valid.has(ck)&&typeof cv==='boolean')safeChecks[k][ck]=cv;}}}const safeMemory={},safeSourceChecks={};for(const [k,v] of Object.entries(x.saved.memoryCards||{})){const parts=k.split('::'),i=Number(parts.at(-1)),id=parts.slice(0,-1).join('::');if(!byId.has(id)||!Number.isInteger(i)||i<0||i>25||!v||typeof v!=='object'||Array.isArray(v))continue;if(typeof v.words==='string'&&v.words.length<=1200&&typeof v.story==='string'&&v.story.length<=900)safeMemory[k]={words:v.words,story:v.story,review:['known','retry'].includes(v.review)?v.review:''};if(Number.isInteger(v.recallAttempts)&&v.recallAttempts>=0&&v.recallAttempts<=100000)safeMemory[k].recallAttempts=v.recallAttempts;if(Number.isInteger(v.recallHits)&&v.recallHits>=0&&v.recallHits<=100000)safeMemory[k].recallHits=v.recallHits;if(Number.isInteger(v.lastAccuracy)&&v.lastAccuracy>=0&&v.lastAccuracy<=100)safeMemory[k].lastAccuracy=v.lastAccuracy;if(typeof v.lastRecallAt==='string'&&/^\d{4}-\d{2}-\d{2}T/.test(v.lastRecallAt))safeMemory[k].lastRecallAt=v.lastRecallAt;}for(const [k,v] of Object.entries(x.saved.sourceChecks||{})){if(byId.has(k)&&typeof v==='boolean')safeSourceChecks[k]=v;}const safeResearch={};for(const [id,v] of Object.entries(x.saved.researchCards||{})){if(!byId.has(id)||!v||typeof v!=='object'||Array.isArray(v))continue;const out={};for(const field of ['author','title','year','locator','note']){const value=v[field];if(typeof value==='string'&&value.length<=(field==='note'?700:220))out[field]=value;}safeResearch[id]=out;}const safeWritingPlans={};for(const [id,v] of Object.entries(x.saved.writingPlans||{})){if(!byId.has(id)||!v||typeof v!=='object'||Array.isArray(v))continue;const entry={};if(Number.isInteger(v.pages)&&v.pages>=1&&v.pages<=12)entry.pages=v.pages;if([300,400,500,600,700,800].includes(v.perPage))entry.perPage=v.perPage;if(Object.keys(entry).length)safeWritingPlans[id]=entry;}saved={drafts:safeDrafts,flags:safeFlags,bookmarks:safeBookmarks,checks:safeChecks,memoryCards:safeMemory,sourceChecks:safeSourceChecks,researchCards:safeResearch,writingPlans:safeWritingPlans,examEnd:0};store();message='기록 복원 완료';render();}catch(err){toast('복원 HOLD: '+err.message)}};
}
render();setInterval(()=>{if(!locked()&&saved.examEnd){stopExpired();render()}const x=root.querySelector('#n27-clock');if(x&&locked()){const t=Math.max(0,Math.ceil((saved.examEnd-Date.now())/1000));x.textContent=`남은 시간 ${Math.floor(t/60)}:${String(t%60).padStart(2,'0')}`;}},1000);
window.N27_ESSAY_TEST={count:rows.length,sourceOnlyCount:sourceCount,answerDraftCount:answerCount,years,open:()=>root.scrollIntoView?.({block:'start'}),select:id=>{if(byId.has(id)){year='all';subject='all';answerType='all';query='';selected=id;render();}},get selected(){return selected;},get locked(){return locked();},get saved(){return saved;},get pane(){return pane;},get pdfOpen(){return pdfOpen;}};
})();

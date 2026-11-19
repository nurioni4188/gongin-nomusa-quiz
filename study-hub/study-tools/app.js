(async()=>{
'use strict';
const E=id=>document.getElementById(id);
const plain=v=>String(v==null?'':v);
const esc=v=>plain(v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const STORAGE='nomusa_study_tools_v1';
const allowed=['schema','updatedAt','items','lastId'];
// Reuse legacy source-only questions without enabling their unapproved candidate keys.
const legacy=[];
for(const key of ['NOMUSA_FIRST_2008','NOMUSA_FIRST_2009','NOMUSA_FIRST_2010']){
 const value=window[key];
 legacy.push(...(Array.isArray(value)?value:Array.isArray(value?.items)?value.items:[]));
}
if(window.NOMUSA_FIRST_BATCH_PACK && 'DecompressionStream' in window){
 try{
  const bytes=Uint8Array.from(atob(window.NOMUSA_FIRST_BATCH_PACK),c=>c.charCodeAt(0));
  const stream=new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'));
  const parsed=JSON.parse(await new Response(stream).text());
  const rows=Array.isArray(parsed)?parsed:(parsed.items||parsed.rows||[]);
  legacy.push(...rows);
 }catch(err){console.warn('Legacy source-only bank could not be read:',err?.message||err)}
}
const questions=[...new Map([...(window.QDATA||[]),...legacy,...(window.NOMUSA_FIRST_V42_TWO_THEORY||[])].filter(q=>q&&q.k).map(q=>[q.k,q])).values()];
const questionById=new Map(questions.map(q=>[q.k,q]));
const essay=(window.N27_CATALOG?.items||[]);
const hub=window.HubState;
const savedWrong=new Set();
Object.entries(hub?.hub?.wrong||{}).forEach(([id,value])=>{if(value===true)savedWrong.add(id)});
Object.entries(hub?.first?.att||{}).forEach(([id,value])=>{if(value?.ok===false)savedWrong.add(id)});
let store={schema:'nomusa_study_tools/1',updatedAt:null,items:{},lastId:null};
let storageBlocked=false;
try{
 const raw=localStorage.getItem(STORAGE);
 if(raw){
  const obj=JSON.parse(raw);
  if(!obj||obj.schema!==store.schema||!obj.items||Array.isArray(obj.items)||typeof obj.items!=='object')throw Error('형식 오류');
  if(Object.keys(obj).some(k=>!allowed.includes(k))||Object.keys(obj.items).some(k=>!questionById.has(k)))throw Error('알 수 없는 기록');
  store={...store,...obj};
 }
}catch(e){storageBlocked=true;setTimeout(()=>notice('이전 학습도구 기록 형식이 달라 자동저장을 중지했습니다. 기존 저장기록은 보호됩니다.'),0)}
const item=id=>{
 if(!store.items[id])store.items[id]={choice:0,card:false,dueAt:null,intervalDays:0,reviews:0};
 return store.items[id];
};
const save=()=>{
 if(storageBlocked)return false;
 try{store.updatedAt=new Date().toISOString();localStorage.setItem(STORAGE,JSON.stringify(store));return true}
 catch{notice('브라우저 저장 실패: 저장 공간을 확인해 주세요.');return false}
};
let pool=[],cursor=0,revealed=false,start=Date.now(),currentSection='focus';
function notice(s){
 E('toast').textContent=plain(s);clearTimeout(notice.timer);notice.timer=setTimeout(()=>E('toast').textContent='',4400);
}
const confirmKey=q=>q&&Array.isArray(q.o)&&q.o.length===5&&Array.isArray(q.a)&&q.a.length===1
 &&Number.isInteger(Number(q.a[0]))&&Number(q.a[0])>=1&&Number(q.a[0])<=5
 &&(q.chk==='MATCH'||String(q.sourceReviewStatus||'').includes('CHECKED'));
const sel=(id,values,label,valueFn)=>{
 const select=E(id),keep=select.value;
 select.innerHTML='<option value="">'+esc(label)+'</option>'+values.map(v=>'<option value="'+esc(v)+'">'+esc(valueFn?valueFn(v):v)+'</option>').join('');
 if([...select.options].some(o=>o.value===keep))select.value=keep;
};
const uniq=list=>[...new Set(list)].filter(x=>x!=null&&x!=='').sort((a,b)=>String(a).localeCompare(String(b),'ko'));
sel('fYear',uniq(questions.map(q=>q.y)).sort((a,b)=>b-a),'전체 연도',x=>x+'년');
sel('fSubject',uniq(questions.map(q=>q.s)),'전체 과목');
sel('pYear',uniq(essay.map(q=>q.year)).sort((a,b)=>b-a),'전체 연도',x=>x+'년');
sel('pSubject',uniq(essay.map(q=>q.subject)),'전체 과목');
function isWrong(q){return savedWrong.has(q.k)||Number(item(q.k).reviews)>0&&item(q.k).lastRating==='again'}
function due(q){return item(q.k).dueAt && new Date(item(q.k).dueAt).getTime()<=Date.now()}
function updatePool(preferredId){
 const year=E('fYear').value,subject=E('fSubject').value,query=E('fQuery').value.trim().toLowerCase();
 pool=questions.filter(q=>(!year||String(q.y)===year)&&(!subject||q.s===subject)
  &&(!query||[q.k,q.q,q.s,String(q.n)].some(x=>plain(x).toLowerCase().includes(query)))
  &&(!E('fWrong').checked||isWrong(q))&&(!E('fDue').checked||due(q)));
 const i=pool.findIndex(q=>q.k===(preferredId||store.lastId));
 cursor=i>=0?i:0;revealed=false;start=Date.now();renderQuestion();
}
function current(){return pool[cursor]||null}
function renderQuestion(){
 const q=current();
 E('focusCount').textContent=questions.length.toLocaleString('ko-KR')+'개 원문 조회 · 기존 오답 '+savedWrong.size+'개 · 과거 미승인 정답 HOLD';
 E('focusPosition').textContent=pool.length?((cursor+1)+' / '+pool.length+'문항'):'조건에 맞는 문항 없음';
 const disabled=!q;
 for(const id of ['prev','next','reveal','again','remembered','selectCard'])E(id).disabled=disabled;
 E('prev').disabled=disabled||cursor===0;E('next').disabled=disabled||cursor>=pool.length-1;
 if(!q){E('question').innerHTML='<p class="empty">필터에 맞는 문항이 없습니다. 다른 연도·과목 또는 복습 조건을 선택해 주세요.</p>';E('selectCard').checked=false;return}
 const rec=item(q.k);
 store.lastId=q.k;save();
 const optionHTML=Array.isArray(q.o)&&q.o.length===5?
  '<div class="options">'+q.o.map((value,i)=>'<button type="button" class="choice'+(rec.choice===i+1?' chosen':'')+'" data-choice="'+(i+1)+'"><span class="num">'+(i+1)+'</span><span>'+esc(value)+'</span></button>').join('')+'</div>':
  '<div class="hold">이 문항의 선택지 전사·구조화는 확인되지 않았습니다. 기존 기출화면의 원문 페이지에서 대조해 주세요.</div>';
 const approved=confirmKey(q);
 const answer=revealed?
  '<div class="'+(approved?'answer':'hold')+'">'+(approved?'기존 정답표 번호 <strong>'+Number(q.a[0])+'번</strong> · 최종 내용 승인과 별개입니다.':'원본 선택지·정답표 일대일 대조 미확인 · 정답 공개 HOLD')+'</div>':'';
 const reviewStatus=rec.dueAt?'다음 복습: '+new Date(rec.dueAt).toLocaleDateString('ko-KR'):'복습 간격 미설정';
 E('question').innerHTML='<div class="question-head"><span class="eyebrow">'+esc(q.y+'년 · '+q.s+' · '+q.n+'번')+'</span><span class="tag hold">'+(approved?'정답표 대조 · 전문가 승인 HOLD':'정답 근거 HOLD')+'</span></div>'
  +'<div class="question-id">'+esc(q.k)+'</div><div class="stem">'+esc(q.q||'텍스트 원문 대조 필요 · 기존 1차 문제지에서 확인하세요.')+'</div>'
  +optionHTML+answer+'<div class="question-foot"><span>'+esc(reviewStatus)+'</span><a href="../../" target="_blank" rel="noopener">기존 1차 화면 열기</a></div>';
 E('selectCard').checked=!!rec.card;
 E('reveal').textContent=revealed?'정답표 번호 가리기':'정답표 번호 보기';
 updateCardCount();
}
function go(next){cursor=Math.max(0,Math.min(pool.length-1,next));revealed=false;start=Date.now();renderQuestion()}
E('question').addEventListener('click',ev=>{
 const btn=ev.target.closest('[data-choice]'),q=current();
 if(!btn||!q)return;
 item(q.k).choice=Number(btn.dataset.choice);save();renderQuestion();
});
E('prev').onclick=()=>go(cursor-1);E('next').onclick=()=>go(cursor+1);
E('reveal').onclick=()=>{revealed=!revealed;renderQuestion()};
function rate(kind){
 const q=current();if(!q)return;
 const data=item(q.k);const last=Number(data.intervalDays)||0;
 const days=kind==='again'?1:(last?Math.min(last*2,60):3);
 data.intervalDays=days;data.reviews=(Number(data.reviews)||0)+1;
 data.lastRating=kind;data.dueAt=new Date(Date.now()+days*86400000).toISOString();
 data.reviewedAt=new Date().toISOString();save();notice(kind==='again'?'1일 후 다시 보기':'복습 간격을 '+days+'일로 설정');
 const id=q.k;updatePool(id);
 if(!E('fDue').checked&&!E('fWrong').checked&&cursor<pool.length-1)go(cursor+1);
}
E('again').onclick=()=>rate('again');E('remembered').onclick=()=>rate('remembered');
E('selectCard').onchange=e=>{const q=current();if(!q)return;item(q.k).card=e.target.checked;save();updateCardCount()};
for(const id of ['fYear','fSubject','fWrong','fDue'])E(id).addEventListener('change',()=>updatePool());
E('fQuery').addEventListener('input',()=>updatePool());
setInterval(()=>{if(currentSection!=='focus'||!pool.length)return;const sec=Math.floor((Date.now()-start)/1000);E('focusTimer').textContent='경과 '+String(Math.floor(sec/60)).padStart(2,'0')+':'+String(sec%60).padStart(2,'0')},1000);
function cardItems(){return questions.filter(q=>store.items[q.k]?.card&&confirmKey(q))}
function updateCardCount(){const size=cardItems().length;E('ankiCount').textContent='Anki 내보내기 대상 '+size+'개 · 선택한 문항 중 정답표 번호와 5지 구조가 확인된 것만 포함됩니다.'}
E('addWrongCards').onclick=()=>{
 let count=0,skipped=0;
 for(const q of questions)if(savedWrong.has(q.k)){
  if(confirmKey(q)){item(q.k).card=true;count++}else skipped++;
 }
 save();renderQuestion();notice('오답 '+count+'개 선택 · 근거 미확인 '+skipped+'개 제외');
};
const flatten=v=>plain(v).replace(/[\t\r\n]+/g,' ').replace(/\s+/g,' ').trim();
function download(content,name,mime){
 const url=URL.createObjectURL(new Blob(['\ufeff',content],{type:mime}));
 const a=document.createElement('a');a.href=url;a.download=name;document.body.append(a);a.click();a.remove();
 setTimeout(()=>URL.revokeObjectURL(url),3000);
}
E('exportAnki').onclick=()=>{
 const rows=cardItems();
 if(!rows.length){notice('내보낼 카드가 없습니다. 정답표 구조 확인 문항을 선택해 주세요.');return}
 const header=['#separator:Tab','#html:false','#tags column:3','#columns:Front\tBack\tTags'].join('\n');
 const data=rows.map(q=>{
  const front=flatten(q.k+' | '+q.q+' / '+q.o.map((v,i)=>(i+1)+') '+v).join(' '));
  const back=flatten('기존 정답표 '+q.a[0]+'번. 공식 법령·학술 내용 승인 HOLD. 원본 문항 ID: '+q.k);
  return [front,back,'nomusa_first year_'+q.y+' source_check_hold'].join('\t');
 }).join('\n');
 download(header+'\n'+data+'\n','nomusa-anki-review-'+new Date().toISOString().slice(0,10)+'.txt','text/plain;charset=utf-8');
 notice(rows.length+'개 Anki 가져오기 파일 생성 · 자동 동기화 아님');
};
function selectPItems(){
 const y=E('pYear').value,s=E('pSubject').value,prev=E('pItem').value;
 const rows=essay.filter(e=>(!y||String(e.year)===y)&&(!s||e.subject===s));
 E('pItem').innerHTML='<option value="">문항 선택</option>'+rows.map(r=>'<option value="'+esc(r.id)+'">'+esc(r.year+' · '+r.subject+' · '+r.topic+' ('+(r.points||'?')+'점)')+'</option>').join('');
 if(rows.some(r=>r.id===prev))E('pItem').value=prev;
 else if(rows.length)E('pItem').value=rows[0].id;
 E('essayCount').textContent=essay.length+'개 기존 카탈로그 중 '+rows.length+'개 선택 가능 · 내용 승인 HOLD';
}
for(const id of ['pYear','pSubject'])E(id).addEventListener('change',selectPItems);
for(const id of ['pItem','pFormat','pMyDraft'])E(id).addEventListener('change',()=>{E('printArea').hidden=true;E('previewInfo').textContent='구성이 변경되었습니다. 인쇄물 미리보기를 다시 확인해 주세요.'});
function sheets(points){if(points===50)return '8~10장';if(points===25)return '4장';if(points===15)return '3장';if(points&&points<=10)return '2장';return '소문항 배점에 비례'}
function printPreview(){
 const r=essay.find(e=>e.id===E('pItem').value);
 if(!r){notice('먼저 2차 문항을 선택해 주세요.');return false}
 const format=E('pFormat').value;
 const own=E('pMyDraft').checked&&plain(hub?.essay?.drafts?.[r.id]).trim();
 const parts=[
  '<article class="paper">',
  '<div class="paper-label">NOMUSA · 2차 학습용 출력 / 전문가 내용 승인 HOLD</div>',
  '<h1>'+esc(r.year+'년 · '+r.subject+' · '+r.topic)+'</h1>',
  '<p class="paper-meta">원본 ID '+esc(r.id)+' · '+esc((r.points||'배점 미확인')+'점')+' · 목표 답안 '+esc(sheets(Number(r.points)))+'</p>',
  '<h2>기출 원문</h2><div class="paper-source">'+esc(r.sourceText||'원문 텍스트 미확인 · 공식 문제지 대조 필요')+'</div>'
 ];
 if(format!=='practice'&&Array.isArray(r.sections)){
  for(const section of r.sections){
   parts.push('<section class="paper-section"><h2>'+esc(section.title||'소문항')+'</h2>');
   if(format==='full')parts.push('<h3>상세 학습답안 초안</h3><p>'+esc(section.detailed||'상세답안 미확인')+'</p>');
   parts.push('<h3>시험장 압축답안 초안</h3><p>'+esc(section.compressed||'압축답안 미확인')+'</p>');
   parts.push('</section>');
  }
 }
 if(own)parts.push('<section class="paper-section"><h2>내 작성 답안 (기존 학습기록)</h2><p>'+esc(own)+'</p></section>');
 if(format!=='full')parts.push('<h2>필기 공간</h2><div class="handwriting"></div><div class="handwriting"></div>');
 parts.push('<p class="paper-warning">검증 구분: 원문/답안 초안 · 시험 당시 법령·판례 및 학술원전 독립 승인 미완료(HOLD). 공식 모범답안이나 채점자료가 아닙니다.</p></article>');
 E('printArea').innerHTML=parts.join('');E('printArea').hidden=false;
 E('previewInfo').textContent='인쇄 미리보기 생성 · '+r.year+' '+r.subject+' · '+r.id;
 return true;
}
E('previewPdf').onclick=()=>{if(printPreview())E('printArea').scrollIntoView({behavior:'smooth'})};
E('printPdf').onclick=()=>{if(printPreview())window.print()};
function switchTo(next){
 const focus=next==='focus';currentSection=next;
 E('focusPanel').hidden=!focus;E('pdfPanel').hidden=focus;
 E('showFocus').classList.toggle('active',focus);E('showPdf').classList.toggle('active',!focus);
 if(focus)E('printArea').hidden=true;
 window.location.hash=focus?'focus':'pdf';
}
E('showFocus').onclick=()=>switchTo('focus');E('showPdf').onclick=()=>switchTo('pdf');
selectPItems();
updatePool();
updateCardCount();
if(location.hash==='#pdf')switchTo('pdf');
window.NOMUSA_STUDY_TOOLS_READONLY=Object.freeze({
 totalFirst:questions.length,totalEssayCatalog:essay.length,
 getState:()=>({selectedAnki:cardItems().length,lastId:store.lastId,reviewItems:Object.keys(store.items).length}),
 hasScoringMutation:false,storageKey:STORAGE
});
})();

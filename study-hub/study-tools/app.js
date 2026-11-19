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
const complete=await window.NOMUSA_COMPLETE_LOAD();
const questions=[...new Map([...(window.QDATA||[]),...legacy,...(window.NOMUSA_FIRST_V42_TWO_THEORY||[]),...complete.first].filter(q=>q&&q.k).map(q=>[q.k,q])).values()];
const questionById=new Map(questions.map(q=>[q.k,q]));
const essaySources=new Map([
 ...(window.N27_CATALOG?.items||[]),
 ...(window.NOMUSA_2013_2014_SPLIT_V1?.items||[])
].map(row=>[row.id,row]));
// Fixed to the 328 ledger IDs; source-only archive records do not inflate the count.
const essay=complete.essay.map(base=>{
 const original=essaySources.get(base.id);
 if(original)return {...base,...original,sourceFile:base.sourceFile,sourceUrl:base.sourceUrl};
 const recovered=window.NOMUSA_ESSAY_12_RECOVERY?.[base.id];
 if(recovered)return {...base,...recovered,topic:'학습용 출제요지 · '+base.id,
   sourceFile:base.sourceFile,sourceUrl:base.sourceUrl};
 // Where subquestions are still unsplit, show the whole original paper with an
 // explicit warning, never pretend it is the exact isolated question.
 let parentId='';
 if(/^2018_p[35]_q[1-3]$/.test(base.id))parentId=base.id.split('_q')[0];
 if(/^2021-경영조직론-q[1-3]$/.test(base.id))parentId='2021_p5';
 if(/^2021-인사노무관리론-q[1-3]$/.test(base.id))parentId='2021_p3';
 const parent=essaySources.get(parentId);
 if(parent?.sourceText)return {...base,sourceText:'[해당 과목 전체 문제지 — 선택한 소문항의 개별 전사·배점은 추가 검토 필요]\n\n'+parent.sourceText,
   topic:'원문 묶음 확인 · '+base.id,sourceBundleOnly:true};
 return base;
});
const ESSAY_NOTE_KEY='nomusa_study_tools_essay_writing_v1';
let essayNotes={schema:'nomusa_study_essay_notes/1',items:{}},essayStorageBlocked=false;
try{
 const raw=localStorage.getItem(ESSAY_NOTE_KEY);
 if(raw){
  const value=JSON.parse(raw),ids=new Set(essay.map(x=>x.id));
  if(!value||value.schema!==essayNotes.schema||!value.items||Array.isArray(value.items)||typeof value.items!=='object'
     ||Object.keys(value.items).some(id=>!ids.has(id)||typeof value.items[id]!=='string'))throw Error('writing schema');
  essayNotes=value;
 }
}catch{essayStorageBlocked=true}
function persistEssay(){
 if(essayStorageBlocked)return false;
 try{localStorage.setItem(ESSAY_NOTE_KEY,JSON.stringify(essayNotes));return true}
 catch{return false}
}
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
function isWrong(q){const d=store.items[q.k];return savedWrong.has(q.k)||Boolean(d&&Number(d.reviews)>0&&d.lastRating==='again')}
function due(q){const d=store.items[q.k];return Boolean(d?.dueAt && new Date(d.dueAt).getTime()<=Date.now())}
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
 E('focusCount').textContent=questions.length.toLocaleString('ko-KR')+'개 ID · 기존 오답 '+savedWrong.size+'개';
 E('sourceCoverage').textContent=complete.failures.length?
   '원장 로드 오류 '+complete.failures.length+'건 · 전체 수록 상태 HOLD':
   '1차 '+questions.length.toLocaleString('ko-KR')+'개 ID 조회 · 103 집중검토 '+complete.report.first103+' · 원문대조 '+complete.report.first686+' · 원문 미확인 문항은 선택지·정답 공개 HOLD';
 E('focusPosition').textContent=pool.length?((cursor+1)+' / '+pool.length+'문항'):'조건에 맞는 문항 없음';
 const disabled=!q;
 for(const id of ['prev','next','reveal','again','remembered','selectCard'])E(id).disabled=disabled;
 E('prev').disabled=disabled||cursor===0;E('next').disabled=disabled||cursor>=pool.length-1;
 if(!q){E('question').innerHTML='<p class="empty">필터에 맞는 문항이 없습니다. 다른 연도·과목 또는 복습 조건을 선택해 주세요.</p>';E('selectCard').checked=false;return}
 const rec=item(q.k);
 store.lastId=q.k;save();
 const optionHTML=Array.isArray(q.o)&&q.o.length===5?
  '<div class="options">'+q.o.map((value,i)=>'<button type="button" class="choice'+(rec.choice===i+1?' chosen':'')+'" data-choice="'+(i+1)+'"><span class="num">'+(i+1)+'</span><span>'+esc(value)+'</span></button>').join('')+'</div>':
  '<div class="hold">이 문항의 선택지 전사·구조화는 확인되지 않았습니다. 원본 문제지를 열어 직접 확인해야 합니다.</div>'+
  '<div class="manual-choice" role="group" aria-label="원전 확인 후 예상 답안 선택"><p>원문을 확인했다면 본인의 예상 답안을 선택하세요. <strong>자동채점·정답 확정이 아닙니다.</strong></p><div class="manual-choice-buttons">'+[1,2,3,4,5].map(n=>'<button type="button" class="choice'+(rec.choice===n?' chosen':'')+'" data-choice="'+n+'" aria-label="내 예상 선택지 '+n+'번">'+n+'번</button>').join('')+'</div></div>';
 const approved=confirmKey(q);
 E('reveal').disabled=!approved;
 const evidenceLinks=[];
 const toRepo=path=>'https://github.com/nurioni4188/gongin-nomusa-quiz/blob/review/nomusa-auto-v1-20year-gate-20261115/'+path.split('/').map(encodeURIComponent).join('/');
 if(/^review\/[A-Za-z0-9_./-]+$/.test(q.sourceOriginal||''))evidenceLinks.push('<a target="_blank" rel="noopener" href="'+esc(toRepo(q.sourceOriginal))+'">문항 근거 원장 열기</a>');
 if(/^https:\/\/[a-z0-9.-]+\//i.test(q.sourceEvidence||''))evidenceLinks.push('<a target="_blank" rel="noopener" href="'+esc(q.sourceEvidence)+'">공식 원문 게시물</a>');
 if(/^https:\/\/www\.q-net\.or\.kr\//i.test(q.sourceOfficialURL||''))evidenceLinks.push('<a target="_blank" rel="noopener" href="'+esc(q.sourceOfficialURL)+'">Q-Net 원본 문제지 열기</a>');
 if(/^https:\/\/renew\.primeedunet\.com\//i.test(q.sourceCandidateURL||''))evidenceLinks.push('<a target="_blank" rel="noopener" href="'+esc(q.sourceCandidateURL)+'">외부 재게시 후보 · 공식 원전 대조 HOLD</a>');
 if(!evidenceLinks.length&&q.fullStage)evidenceLinks.push('<a target="_blank" rel="noopener" href="'+esc(toRepo('review/NOMUSA_FIRST_V54_686_UNIFIED_PRIMARY_SOURCE_LEDGER_20261118.json'))+'">원문 수집·검토 장부</a>');
 const cropPath=typeof q.sourceCrop==='string' && /^review\/first-v(?:41-native-crops|48-provisional-crops|42-four-corrected-crops)\/legacy1-[A-Za-z0-9-]+\.jpg$/.test(q.sourceCrop)?q.sourceCrop:'';
 const cropHTML=cropPath?'<figure class="source-crop"><figcaption>원본문항 이미지 후보 · 지문/선택지 위치 독립 대조 HOLD</figcaption><img loading="lazy" alt="문제지의 잠정 발췌 이미지 — 배점·지문 및 5지 대조 전" src="../../'+cropPath.split('/').map(encodeURIComponent).join('/')+'"></figure>':'';
 const sourceNote=!q.q||!Array.isArray(q.o)||q.o.length!==5?
  '<div class="hold">원문·선택지 전사 미확인: 아래 근거를 확인하며 학습 메모를 작성할 수 있지만, 공식 문제풀이와 채점은 HOLD입니다.</div>':
  (q.fullStage?'<div class="hold">원문 전사 초안 · 독립 교열 대기 · 정답·해설 최종승인 HOLD</div>':'');
 const answer=revealed?
  '<div class="'+(approved?'answer':'hold')+'">'+(approved?'기존 정답표 번호 <strong>'+Number(q.a[0])+'번</strong> · 최종 내용 승인과 별개입니다.':'원본 선택지·정답표 일대일 대조 미확인 · 정답 공개 HOLD')+'</div>':'';
 const draftRationale=q.fullStage==='source103'&&q.learningExplanationDraft?
   '<details class="learning-rationale"><summary>기존 학습 해설 초안 확인 · 독립검증 HOLD</summary>'+
   '<p class="rationale-notice">이 해설은 학습 초안입니다. 선택지별 법령·판례·계산과 공식 답안의 독립 교열은 완료되지 않았고, 자동채점 근거가 아닙니다.</p>'+
   '<div class="rationale-text">'+esc(plain(q.learningExplanationDraft).slice(0,15000))+'</div>'+
   (Array.isArray(q.learningOptionNotes)&&q.learningOptionNotes.length===5?
     '<h4>선택지별 학습 메모 초안</h4><ol>'+q.learningOptionNotes.map(v=>'<li>'+esc(plain(v).slice(0,1600))+'</li>').join('')+'</ol>':
     '<p class="rationale-notice">선택지별 독립 논증·교열 대기</p>')+
   '</details>':'';
 const reviewStatus=rec.dueAt?'다음 복습: '+new Date(rec.dueAt).toLocaleDateString('ko-KR'):'복습 간격 미설정';
 E('question').innerHTML='<div class="question-head"><span class="eyebrow">'+esc(q.y+'년 · '+q.s+' · '+q.n+'번')+'</span><span class="tag hold">'+(approved?'정답표 대조 · 전문가 승인 HOLD':'정답 근거 HOLD')+'</span></div>'
  +'<div class="question-id">'+esc(q.k)+'</div><div class="stem">'+esc(q.q||'텍스트 원문 대조 필요 · 기존 1차 문제지에서 확인하세요.')+'</div>'
  +sourceNote+cropHTML+optionHTML+answer+draftRationale
  +(q.fullStage?'<div class="evidence-links">'+evidenceLinks.join(' ')+'</div>':'')
  +(!q.q||!Array.isArray(q.o)||q.o.length!==5?
     '<label class="first-note-label">원전 대조·학습 메모 (개인 기록)<textarea id="firstNote" maxlength="15000" placeholder="원본을 확인하면서 개인 메모를 남기세요. 공식 문제로 자동 확정되지 않습니다.">'+esc(rec.note||'')+'</textarea></label>':'')
  +'<div class="question-foot"><span>'+esc(reviewStatus)+'</span><a href="../../" target="_blank" rel="noopener">기존 1차 화면 열기</a></div>';
 E('selectCard').checked=!!rec.card;
 E('reveal').textContent=revealed?'정답표 번호 가리기':'정답표 번호 보기';
 updateCardCount();
}
function go(next){cursor=Math.max(0,Math.min(pool.length-1,next));revealed=false;start=Date.now();renderQuestion()}
E('question').addEventListener('input',ev=>{
  if(ev.target.id==='firstNote'&&current()){item(current().k).note=ev.target.value.slice(0,15000);save();}
});
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
 E('essayCount').textContent=essay.length+'개 원장 ID 중 '+rows.length+'개 조회 · 내용 승인 HOLD';
 updateEssayWorkspace();
}
function updateEssayWorkspace(){
 const r=essay.find(x=>x.id===E('pItem').value);
 if(!r){E('essaySourceStatus').textContent='문항을 선택하세요.';E('essayOwnWriting').value='';return}
 const links=[];
 const url=r.sourceOfficialUrl||r.sourceUrl||r.source?.qnetPostUrl||'';
 if(/^https:\/\/[a-z0-9.-]+\//i.test(url))links.push('<a href="'+esc(url)+'" target="_blank" rel="noopener">공식 기출 게시물</a>');
 const path=r.sourcePdfPath||r.pdfPath||r.sourceFile||'';
 if(/^(source_pdf|review)\/[A-Za-z0-9_./-]+$/.test(path)){
  const link='https://github.com/nurioni4188/gongin-nomusa-quiz/blob/review/nomusa-auto-v1-20year-gate-20261115/'+path.split('/').map(encodeURIComponent).join('/');
  links.push('<a href="'+esc(link)+'" target="_blank" rel="noopener">원본문서 저장소</a>');
 }
 E('essaySourceStatus').innerHTML='<strong>'+(r.sourceSummaryOnly?'학습용 출제요지 · 공식 원문 전문 대조 HOLD':r.sourceBundleOnly?'과목 전체 원본문서 연결 · 개별 소문항 분리 HOLD':r.sourceText?'학습용 원문 텍스트 연결 · 검증/승인 별도 HOLD':'원문 텍스트 미연결 · 원본문서 확인 필요 HOLD')+'</strong> · '+esc(r.id)+' · '+links.join(' · ');
 E('essayOwnWriting').value=essayNotes.items[r.id]||'';
 E('essayOwnSaveStatus').textContent=essayStorageBlocked?'저장기록 오류 · 자동저장 HOLD':'이 페이지에서만 별도 자동저장';
}
E('essayOwnWriting').addEventListener('input',ev=>{
 const id=E('pItem').value;
 if(!essay.some(x=>x.id===id)||essayStorageBlocked)return;
 essayNotes.items[id]=ev.target.value.slice(0,150000);
 E('essayOwnSaveStatus').textContent=persistEssay()?'별도 자동저장 완료':'저장 실패 · 본문 복사 권장';
});
for(const id of ['pYear','pSubject'])E(id).addEventListener('change',selectPItems);
for(const id of ['pItem','pFormat','pMyDraft'])E(id).addEventListener('change',()=>{
 E('printArea').hidden=true;
 E('previewInfo').textContent='구성이 변경되었습니다. 인쇄물 미리보기를 다시 확인해 주세요.';
 if(id==='pItem')updateEssayWorkspace();
});
function sheets(points){if(points===50)return '8~10장';if(points===25)return '4장';if(points===15)return '3장';if(points&&points<=10)return '2장';return '소문항 배점에 비례'}
function printPreview(){
 const r=essay.find(e=>e.id===E('pItem').value);
 if(!r){notice('먼저 2차 문항을 선택해 주세요.');return false}
 const format=E('pFormat').value;
 const own=E('pMyDraft').checked&&plain(essayNotes.items[r.id]||hub?.essay?.drafts?.[r.id]).trim();
 const parts=[
  '<article class="paper">',
  '<div class="paper-label">NOMUSA · 2차 학습용 출력 / 전문가 내용 승인 HOLD</div>',
  '<h1>'+esc(r.year+'년 · '+r.subject+' · '+r.topic)+'</h1>',
  '<p class="paper-meta">원본 ID '+esc(r.id)+' · '+esc((r.points||'배점 미확인')+'점')+' · 목표 답안 '+esc(sheets(Number(r.points)))+'</p>',
  '<h2>'+(r.sourceSummaryOnly?'학습용 출제요지 — 원문 전문은 별도 확인':'기출 원문')+'</h2><div class="paper-source">'+esc(r.sourceText||'원문 텍스트 미확인 · 공식 문제지 대조 필요')+'</div>'
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
 totalFirst:questions.length,totalEssayCatalog:essay.length,fullCoverageReport:complete.report,sourceLoadFailures:complete.failures,
 sourceCoverage:Object.freeze({firstWithStem:questions.filter(q=>!!q.q).length,firstWithFiveOptions:questions.filter(q=>Array.isArray(q.o)&&q.o.length===5).length,
  first103FullyRead:complete.first.filter(q=>q.fullStage==='source103'&&!!q.q&&q.o.length===5).length,
  first686AwaitingSource:complete.first.filter(q=>q.fullStage==='source686'&&!q.q).length,
  secondExactOrDraftText:essay.filter(r=>r.sourceText&&!r.sourceBundleOnly).length,
  secondOriginalBundleOnly:essay.filter(r=>r.sourceBundleOnly).length,
  secondLearningSummaries:essay.filter(r=>r.sourceSummaryOnly).length,
  secondExtractedOriginal2018:essay.filter(r=>r.sourceStatus?.startsWith('OFFICIAL_PDF_TEXT_EXTRACTED')).length,
  secondNoSourceText:essay.filter(r=>!r.sourceText).length}),
 getState:()=>({selectedAnki:cardItems().length,lastId:store.lastId,reviewItems:Object.keys(store.items).length}),
 hasScoringMutation:false,storageKey:STORAGE
});
})();

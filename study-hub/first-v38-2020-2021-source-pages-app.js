/* NOMUSA FIRST V38 · 2020/21 original QNet PDF page image study only.
 * 274 page OCR candidates, 26 exact-location HOLD. No scoring/approval/QDATA writes.
 */
(function(){'use strict';
const $=id=>document.getElementById(id), KEY='nomusa1-v38-a-2020-2021-page-review';
const C=['①','②','③','④','⑤'],v=window.NOMUSA_FIRST_LEGACY_V5,s=window.NOMUSA_FIRST_V61_SOURCES;
if(!v||!s?.records||!s?.documents)throw Error('V38_REQUIRED_SOURCE_MISSING');
const rows=v.records.filter(x=>x.type==='A'&&(x.year===2020||x.year===2021))
 .sort((a,b)=>a.year-b.year||a.questionNo-b.questionNo).map(x=>{
 const m=s.records[x.id],d=m&&s.documents[m.source];
 return Object.freeze({id:x.id,year:x.year,n:x.questionNo,subject:x.subject,
   status:m?.status||'HOLD',sourceKey:m?.source||'',pdfPage:m?.status==='OCR_PAGE_CANDIDATE'?m.pdfPage:null,
   url:d?.download||null,answers:x.answers});
 });
if(rows.length!==300||rows.filter(x=>Number.isInteger(x.pdfPage)).length!==274)
 throw Error('V38_300_ITEMS_274_PAGE_CANDIDATES_MISMATCH');
const byId=new Map(rows.map(x=>[x.id,x]));let saved={};
try{const o=JSON.parse(localStorage.getItem(KEY)||'{}');
 if(o&&typeof o==='object'&&!Array.isArray(o))
  for(const [k,z]of Object.entries(o))if(byId.has(k)&&z&&[null,1,2,3,4,5].includes(z.choice))
   saved[k]={choice:z.choice,flag:Boolean(z.flag)};
}catch(_){}
let list=[],selected=null;
function store(){try{localStorage.setItem(KEY,JSON.stringify(saved))}catch(_){}}
function resetList(){
 const year=Number($('year').value),old=$('subject').value;
 const active=rows.filter(x=>x.year===year);
 const sub=[...new Set(active.map(x=>x.subject))].sort((a,b)=>a.localeCompare(b,'ko'));
 $('subject').replaceChildren(new Option('전체 과목','all'),...sub.map(x=>new Option(x,x)));
 $('subject').value=sub.includes(old)?old:'all';
 list=active.filter(x=>$('subject').value==='all'||x.subject===$('subject').value);
 $('item').replaceChildren(...list.map(x=>new Option(
   String(x.n).padStart(3,'0')+'번 · '+x.subject+(x.pdfPage?' · 페이지후보':' · 위치HOLD'),x.id)));
 selected=list[0]?.id||null;render();
}
function render(){
 const x=list.find(x=>x.id===selected)||list[0];if(!x)return;
 selected=x.id;$('item').value=x.id;
 const i=list.findIndex(y=>y.id===x.id),rec=saved[x.id]||{choice:null,flag:false};
 $('title').textContent=x.year+'년 A형 · '+x.subject+' '+x.n+'번';
 $('meta').textContent='원본 문항 ID '+x.id+' · 공식 파일 '+x.sourceKey;
 const has=Number.isInteger(x.pdfPage)&&x.pdfPage>0;
 $('status').textContent=has?'OCR 추정 PDF '+x.pdfPage+'쪽 · 문항번호/선택지 수동 대조 HOLD':
 '원본 PDF 페이지 위치 미확정 · 선택 연습 차단';
 $('pageFigure').hidden=!has;$('noPage').hidden=has;
 if(has){
  const url='first-v38-qnet-pages-2020-2021/'+x.sourceKey+'-p'+String(x.pdfPage).padStart(3,'0')+'.jpg';
  $('sourceImg').src=url;$('sourceImg').alt=x.year+'년 A형 원본 PDF '+x.pdfPage+'쪽 이미지, '+x.n+'번 문항위치 검토 전';
  $('zoom').href=url;
 }else $('sourceImg').removeAttribute('src');
 $('official').href=(x.url||'https://www.q-net.or.kr/')+(has?'#page='+x.pdfPage:'');
 $('official').textContent='Q-Net 원본 PDF '+(has?x.pdfPage+'쪽 후보':'전체')+' 열기';
 $('choices').replaceChildren(...C.map((label,i)=>{
  const b=document.createElement('button');b.type='button';b.textContent=label;b.dataset.choice=i+1;
  b.disabled=!has;b.setAttribute('aria-pressed',String(rec.choice===i+1));
  b.setAttribute('aria-label',label+' 선택 저장 · 채점하지 않음');
  b.onclick=()=>{saved[x.id]={choice:i+1,flag:rec.flag};store();render()};return b;
 }));
 $('prev').disabled=i===0;$('next').disabled=i>=list.length-1;
 $('flag').disabled=!has;$('flag').textContent=rec.flag?'복습 표시 해제':'복습 표시';
 $('flag').setAttribute('aria-pressed',String(rec.flag));
 $('progress').textContent=(i+1)+'/'+list.length+' · 300문항 중 274페이지 추정 · 선택 기록 '+
  rows.filter(x=>saved[x.id]?.choice!=null).length+'/300 · 복습 '+rows.filter(x=>saved[x.id]?.flag).length;
 $('candidate').open=false;
 $('candidateText').textContent=x.answers?.length?
  '기존 정답표 전사 후보 '+x.answers.map(n=>C[n-1]||n).join(', ')+' · 독립 내용승인 전이므로 자동채점·정오판정 금지':
  '정답표 후보 원장 검토 대기';
}
$('year').onchange=()=>{$('subject').value='all';resetList()};
$('subject').onchange=resetList;
$('item').onchange=()=>{selected=$('item').value;render()};
$('prev').onclick=()=>{let i=list.findIndex(x=>x.id===selected);if(i>0){selected=list[i-1].id;render()}};
$('next').onclick=()=>{let i=list.findIndex(x=>x.id===selected);if(i>=0&&i<list.length-1){selected=list[i+1].id;render()}};
$('flag').onclick=()=>{const x=byId.get(selected),r=saved[selected]||{choice:null,flag:false};
 if(x.pdfPage){saved[selected]={choice:r.choice,flag:!r.flag};store();render()}};
$('reset').onclick=()=>{if(confirm('이 별도 원본 페이지 연습 기록만 초기화할까요?')){
 saved={};store();render()}};
$('export').onclick=()=>{const blob=new Blob([JSON.stringify({schema:'NOMUSA_V38_UNGRADED_SOURCE_REVIEW/1',
   items:saved,originalScoringChanged:false},null,2)],{type:'application/json'});
 const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;
 a.download='nomusa-first-v38-2020-2021-a-source-records.json';a.click();
 setTimeout(()=>URL.revokeObjectURL(url),1600);
};
resetList();
window.NOMUSA_FIRST_V38=Object.freeze({total:300,pageCandidates:274,strictHold:26,approvedKeys:0});
})();
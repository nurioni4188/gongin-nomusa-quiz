'use strict';
// Static require allows Vercel's serverless file tracer to include the manifest.
const records = require('../_data/questions.json');
const byKey = new Map(records.map(x => [x.k, x]));
const LAW_BASE = 'https://www.law.go.kr/DRF';
const LAW_NAMES = [
  '노동조합 및 노동관계조정법','근로기준법','남녀고용평등과 일·가정 양립 지원에 관한 법률',
  '기간제 및 단시간근로자 보호 등에 관한 법률','파견근로자 보호 등에 관한 법률',
  '산업재해보상보험법','고용보험법','고용보험 및 산업재해보상보험의 보험료징수 등에 관한 법률',
  '국민건강보험법','국민연금법','고용정책 기본법','근로자퇴직급여 보장법',
  '산업안전보건법','최저임금법','민법','상법','근로자참여 및 협력증진에 관한 법률',
  '사회보장기본법','장애인고용촉진 및 직업재활법','사회보험료 징수법'
];
function candidates(q){
  const s=[q.q,...(q.o||[])].join(' ');
  return LAW_NAMES.filter(n=>s.includes(n)).slice(0,4);
}
function response(res, status, data){
  res.setHeader('Content-Type','application/json; charset=utf-8');
  res.setHeader('Cache-Control','no-store');
  res.setHeader('X-Content-Type-Options','nosniff');
  res.status(status).end(JSON.stringify(data));
}
function safeMethod(req, allowed){return allowed.includes(req.method||'GET');}
function trimString(x,n=120){return typeof x==='string'?x.trim().slice(0,n):'';}
function urlToLaw(verb, params){
  const url=new URL(`${LAW_BASE}/${verb}.do`);
  for(const [k,v] of Object.entries(params))url.searchParams.set(k,String(v));
  return url;
}
async function upstream(url,timeoutMs=9000){
  const ac=new AbortController();const timer=setTimeout(()=>ac.abort(),timeoutMs);
  try{
    const r=await fetch(url,{signal:ac.signal,redirect:'error',headers:{accept:'application/json'}});
    if(!r.ok)throw new Error('UPSTREAM_HTTP_'+r.status);
    const text=await r.text();
    if(text.length>2200000)throw new Error('UPSTREAM_TOO_LARGE');
    let result;
    try{result=JSON.parse(text)}catch{throw new Error('UPSTREAM_NON_JSON')}
    return result;
  }finally{clearTimeout(timer)}
}
function lawRows(payload){
  let x=payload?.LawSearch??payload?.lawSearch??payload?.lawsearch??payload;
  const total=Number(x?.totalCnt ?? x?.totalcnt ?? 0);
  let list=x?.law??x?.법령??[];if(!Array.isArray(list))list=[list];
  const items=list.filter(Boolean).map(row=>({
    id:trimString(String(row?.법령ID??row?.lawId??row?.ID??''),30),
    name:trimString(row?.법령명한글??row?.법령명??row?.name??'',160),
    effectiveDate:trimString(String(row?.시행일자??''),15),
    announcedDate:trimString(String(row?.공포일자??''),15),
    ministry:trimString(row?.소관부처명??'',80)
  })).filter(x=>x.id&&x.name);
  return {total,items:items.slice(0,5)};
}
async function searchLaw(term){
  if(!process.env.LAW_API_OC)throw new Error('LAW_OC_MISSING');
  const q=trimString(term,80);
  if(q.length<2)throw new Error('INVALID_QUERY');
  const url=urlToLaw('lawSearch',{OC:process.env.LAW_API_OC,target:'law',type:'JSON',search:1,query:q,display:5});
  const raw=await upstream(url);
  return lawRows(raw);
}
function extractArticles(payload){
  const body=payload?.법령??payload?.law??payload;
  const base=body?.기본정보??{};
  const ar=body?.조문?.조문단위??body?.조문?.조문??[];
  const items=(Array.isArray(ar)?ar:[ar]).filter(Boolean).slice(0,900).map(x=>({
    article:trimString(String(x?.조문번호??''),12),title:trimString(x?.조문제목??'',120),
    content:trimString(String(x?.조문내용??''),2800)
  })).filter(x=>x.content);
  return {name:trimString(base?.법령명_한글??base?.법령명한글??'',160),
    effectiveDate:trimString(String(base?.시행일자??''),15),articles:items};
}
async function lawDetail(lawId){
  if(!process.env.LAW_API_OC)throw new Error('LAW_OC_MISSING');
  const id=trimString(String(lawId),25);
  if(!/^\d{1,12}$/.test(id))throw new Error('INVALID_LAW_ID');
  const url=urlToLaw('lawService',{OC:process.env.LAW_API_OC,target:'law',type:'JSON',ID:id});
  return extractArticles(await upstream(url));
}
function failReason(error){
  const v=String(error?.message??error??'');
  if(v==='LAW_OC_MISSING')return [503,'HOLD_LAW_OC_MISSING'];
  if(v==='INVALID_QUERY'||v==='INVALID_LAW_ID')return [400,'HOLD_INVALID_INPUT'];
  if(v.includes('UPSTREAM_')||error?.name==='AbortError')return [502,'HOLD_LAW_UPSTREAM'];
  return [500,'HOLD_SERVER_ERROR'];
}
module.exports={records,byKey,LAW_NAMES,candidates,response,safeMethod,trimString,searchLaw,lawDetail,failReason};

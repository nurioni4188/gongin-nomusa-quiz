'use strict';
const c=require('./_lib/core.cjs');
function parseBody(req){
 if(typeof req.body==='object'&&req.body!==null)return req.body;
 const raw=typeof req.body==='string'?req.body:'';
 if(raw.length>4096)throw Error('INVALID_BODY');
 return JSON.parse(raw||'{}');
}
function extractResponseText(data){
 if(typeof data?.output_text==='string')return data.output_text;
 return (data?.output??[]).flatMap(x=>x?.content??[]).filter(x=>x?.type==='output_text').map(x=>x.text).join('\n');
}
module.exports=async function explain(req,res){
 if(req.method!=='POST')return c.response(res,405,{status:'HOLD_METHOD'});
 if(process.env.EXPLANATION_ENABLED!=='true')return c.response(res,403,{status:'HOLD_EXPLANATION_DISABLED',message:'관리자 검증 전 AI 해설 생성 비활성'});
 if(!process.env.OPENAI_API_KEY || !process.env.EXPLANATION_MODEL)return c.response(res,503,{status:'HOLD_AI_CONFIG_MISSING'});
 let body;
 try{body=parseBody(req)}catch{return c.response(res,400,{status:'HOLD_BAD_REQUEST'});}
 const key=c.trimString(body.key||'',100);
 const q=c.byKey.get(key);
 if(!q)return c.response(res,404,{status:'HOLD_UNKNOWN_QUESTION'});
 if(!q.q||q.q.length<12||!Array.isArray(q.o)||q.o.length!==5||q.tx==='scan')return c.response(res,422,{status:'HOLD_SOURCE_TEXT_REVIEW',key});
 if(!Array.isArray(q.a)||!q.a.length)return c.response(res,422,{status:'HOLD_UNVERIFIED_ANSWER',key});
 const terms=c.candidates(q);if(!terms.length)return c.response(res,422,{status:'HOLD_NO_EXPLICIT_LAW',key});
 let law,detail;
 try{
   law=await c.searchLaw(terms[0]);
   const exact=law.items.find(x=>x.name===terms[0]);
   if(!exact)return c.response(res,422,{status:'HOLD_LAW_MATCH_UNCONFIRMED',key,candidate:terms[0]});
   detail=await c.lawDetail(exact.id);
   if(!detail.articles.length)return c.response(res,422,{status:'HOLD_NO_ARTICLE_TEXT',key});
 }catch(e){let [code,status]=c.failReason(e);return c.response(res,code,{status,key});}
 // A capped passage is context for drafting, never a proof of historical applicability.
 const brief=detail.articles.filter(x=>x.content).slice(0,75).map(x=>`제${x.article}조 ${x.title} ${x.content}`).join('\n').slice(0,18000);
 const userData={key:q.k,year:q.y,subject:q.s,question:q.q,options:q.o,officialAnswerCandidate:q.a,
  sourceFile:q.src,sourcePage:q.pg,lawName:terms[0],currentLawTextExcerpt:brief,
  lawEffectiveDate:detail.effectiveDate||law.items[0]?.effectiveDate||''};
 const ac=new AbortController();const timeout=setTimeout(()=>ac.abort(),18000);
 try{
    const r=await fetch('https://api.openai.com/v1/responses',{
      method:'POST',signal:ac.signal,headers:{'Authorization':`Bearer ${process.env.OPENAI_API_KEY}`,'Content-Type':'application/json'},
      body:JSON.stringify({model:process.env.EXPLANATION_MODEL,store:false,max_output_tokens:1100,
      instructions:'공인노무사 기출문제 학습 보조용 한국어 AI 해설 초안입니다. 제공된 법령 발췌만 근거로 사용하세요. 출제 연도 당시 시행법 여부를 확인하지 못했으므로 현행/당시 규정 동일함을 단정하지 마세요. 근거 없는 조문·판례·정답을 만들어내지 마세요. 공식 정답 후보를 변경하지 마세요. 명백하지 않은 사항은 미확인이라고 쓰세요. JSON만 반환: {"summary":"...","reason":"...","articleCitations":["..."],"unverified":["..."]}.',
      input:JSON.stringify(userData)})
    });
    if(!r.ok)return c.response(res,502,{status:'HOLD_AI_UPSTREAM',key,upstreamStatus:r.status});
    const payload=await r.json();let raw=extractResponseText(payload);
    let draft;try{draft=JSON.parse(raw.replace(/^```(?:json)?\s*|\s*```$/g,''))}catch{return c.response(res,502,{status:'HOLD_AI_RESPONSE_FORMAT',key});}
    if(!draft||typeof draft.summary!=='string'||typeof draft.reason!=='string')return c.response(res,502,{status:'HOLD_AI_RESPONSE_FORMAT',key});
    return c.response(res,200,{status:'DRAFT_HOLD_HUMAN_REVIEW',key,year:q.y,subject:q.s,
      answerCandidate:q.a,draft:{summary:draft.summary.slice(0,1600),reason:draft.reason.slice(0,3500),
      articleCitations:Array.isArray(draft.articleCitations)?draft.articleCitations.slice(0,8).map(x=>c.trimString(x,160)):[],
      unverified:Array.isArray(draft.unverified)?draft.unverified.slice(0,8).map(x=>c.trimString(x,160)):[]},
      law:{name:terms[0],id:law.items.find(x=>x.name===terms[0])?.id,effectiveDate:detail.effectiveDate||''},
      officialAnswerVerified:false,examDateLawVerified:false,releaseApproved:false});
 }catch(e){return c.response(res,502,{status:'HOLD_AI_UPSTREAM',key});}
 finally{clearTimeout(timeout)}
};

'use strict';
const c=require('./_lib/core.cjs');
module.exports=async function law(req,res){
 if(!c.safeMethod(req,['GET']))return c.response(res,405,{status:'HOLD_METHOD',message:'GET only'});
 try{
   const action=c.trimString(req.query?.action||'search',12);
   if(action==='search'){
      const key=c.trimString(req.query?.key||'',100);
      const q=key?c.byKey.get(key):null;
      if(key&&!q)return c.response(res,404,{status:'HOLD_UNKNOWN_QUESTION'});
      const terms=q?c.candidates(q):[c.trimString(req.query?.query||'',80)];
      if(!terms[0])return c.response(res,422,{status:'HOLD_NO_EXPLICIT_LAW',questionKey:key,terms:[],source:'국가법령정보센터',verified:false});
      const found=await c.searchLaw(terms[0]);
      return c.response(res,200,{status:found.items.length?'FOUND_CURRENT_LAW':'HOLD_NO_MATCH',questionKey:key,terms,
        ...found,source:'국가법령정보센터 법령 목록 API',effectiveDateVerifiedForExam:false,
        note:'현재 법령 검색결과입니다. 출제 당시 시행 조문과 별도로 대조해야 합니다.'});
   }
   if(action==='detail'){
      const id=c.trimString(req.query?.id||'',25);
      const d=await c.lawDetail(id);
      return c.response(res,200,{status:d.articles.length?'FOUND_CURRENT_TEXT':'HOLD_NO_ARTICLE_TEXT',
         ...d,source:'국가법령정보센터 법령 본문 API',effectiveDateVerifiedForExam:false,
         note:'출제 당시 법령 이력 대조 전에는 정답 근거 확정 불가'});
   }
   return c.response(res,400,{status:'HOLD_INVALID_ACTION'});
 }catch(err){const [code,status]=c.failReason(err);return c.response(res,code,{status,verified:false});}
};

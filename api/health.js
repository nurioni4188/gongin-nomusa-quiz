'use strict';
const {response}=require('./_lib/core.cjs');
module.exports=function health(req,res){
 if(req.method!=='GET')return response(res,405,{status:'HOLD_METHOD'});
 const lawConfigured=Boolean(process.env.LAW_API_OC);
 const aiConfigured=Boolean(process.env.OPENAI_API_KEY&&process.env.EXPLANATION_MODEL);
 const enabled=process.env.EXPLANATION_ENABLED==='true';
 return response(res,200,{status:'SERVER_FUNCTION_READY',scope:'Preview-only verification recommended',
    law:{configured:lawConfigured,verified:false},
    ai:{configured:aiConfigured,enabled,verified:false},
    answers:{loaded:1020,officialSourceIndependentlyVerified:false},
    note:'키 존재여부만 확인합니다. 실제 API 인증/법령 정확성 검증과는 다릅니다.'});
};

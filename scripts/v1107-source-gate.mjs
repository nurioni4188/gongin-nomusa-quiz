#!/usr/bin/env node
// V11.0.7 read-only source gate. This does not approve legal contents or validate HTTPS.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
const root=path.resolve(process.argv[2]||'.');
const failures=[];
const required=['study-hub/index.html','study-hub/app.js','study-hub/state.js','second/index.html','second/essay-app.js','second/v1098-law-47-autodrafts.js','second/v1105-law-review-sidecar.js','second/v1106-law-review-bridge.js','review/v1105-47-answer-correction-map.json'];
for(const p of required)if(!fs.existsSync(path.join(root,p)))failures.push('MISSING:'+p);
const expected='7d0bac4e82a812c2e59171573fa4f09bc3c45de310599b5f54fc0ad1c42df48c';
const draft=path.join(root,'second/v1098-law-47-autodrafts.js');
if(fs.existsSync(draft)){const hash=crypto.createHash('sha256').update(fs.readFileSync(draft)).digest('hex');if(hash!==expected)failures.push('DRAFT_SHA256_MISMATCH')}
let counts={};
const mapfile=path.join(root,'review/v1105-47-answer-correction-map.json');
if(fs.existsSync(mapfile)){
 try{
 const m=JSON.parse(fs.readFileSync(mapfile,'utf8')),ids=m.sourceAnswerIds,cor=m.corrections,untouched=m.unmodifiedAnswerIds,targets=new Set(cor.map(x=>x.questionId));
 counts={sourceAnswers:ids.length,untouched:untouched.length,targets:targets.size,corrections:cor.length};
 if(ids.length!==47||new Set(ids).size!==47)failures.push('SOURCE_ID_COUNT');
 if(cor.length!==18||targets.size!==6)failures.push('CORRECTION_COUNT');
 if(untouched.length!==41||untouched.some(id=>targets.has(id)))failures.push('UNTOUCHED_MISMATCH');
 for(const id of targets)if(!ids.includes(id)||cor.filter(c=>c.questionId===id).length!==3)failures.push('INVALID_TARGET:'+id);
 if(m.officialApprovalStatus!=='HOLD'||m.readOnly!==true)failures.push('REVIEW_ONLY_MISMATCH');
 }catch(e){failures.push('MAPPING_PARSE:'+String(e))}
}
for(const entry of ['study-hub/index.html','second/index.html']){
 const f=path.join(root,entry);
 if(fs.existsSync(f)&&!fs.readFileSync(f,'utf8').includes('v1106-law-review-bridge.js'))failures.push('MISSING_BRIDGE_ENTRY:'+entry);
}
const status=failures.length?'HOLD':'PASS_STATIC_ONLY';
console.log(JSON.stringify({schema:'nomusa-v1107-source-gate-v1',status,counts,failures,legalContentApproval:'0/47 HOLD',httpsPreview:'NOT_TESTED'},null,2));
if(failures.length)process.exitCode=1;

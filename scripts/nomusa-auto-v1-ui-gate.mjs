#!/usr/bin/env node
// NOMUSA-AUTO V1.2: read-only compatibility check for staged 2007-2026 study catalogs.
// No network, Git mutation, deployment, or browser automation is performed.
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
const root=path.resolve(process.argv[2]||'.'), errors=[];
const load=f=>fs.readFileSync(path.join(root,f),'utf8');
const ctx={window:{},console:{log(){},warn(){},error(){}}};vm.createContext(ctx);
for(const f of ['data.js','rc27_essay_catalog.js','second/archive_2013_2021.js']){
 try{vm.runInContext(load(f),ctx,{filename:f,timeout:2500});}catch(e){errors.push('LOAD_ERROR:'+f+':'+e.message);}
}
const baseline=JSON.stringify(ctx.window.N27_CATALOG?.items||[]);
try{vm.runInContext(load('second/legacy_2007_2012_source_only.js'),ctx,{timeout:2500});}
catch(e){errors.push('LOAD_ERROR:legacy_2007_2012_source_only.js:'+e.message);}
const items=ctx.window.N27_CATALOG?.items||[],status=ctx.window.NOMUSA_LEGACY_STATUS||{};
const ids=items.map(x=>x.id),unique=new Set(ids);
const added=items.filter(x=>x.origin==='LEGACY_HWP_2007_2012');
const old=items.filter(x=>x.origin!=='LEGACY_HWP_2007_2012');
if(old.length!==215||JSON.stringify(old)!==baseline)errors.push('EXISTING_ESSAY_RECORD_CHANGED');
const firstIds=(ctx.window.QDATA||[]).map(row=>row.k);
if(firstIds.length!==1020)errors.push('FIRST_STAGE_COUNT_NOT_1020');
const subIds=added.flatMap(row=>(row.subquestions||[]).map(sub=>sub.id));
if(subIds.length!==76)errors.push('SUBQUESTION_COUNT_NOT_76');
const allIds=[...firstIds,...ids,...subIds];
if(new Set(allIds).size!==allIds.length)errors.push('CROSS_STAGE_ID_COLLISION');
const proposed=JSON.parse(load('review/NOMUSA_AUTO_V1_PROPOSED_QUESTIONS.json')).records;
const byId=new Map(added.map(row=>[row.id,row]));
for(const row of proposed){
 const item=byId.get(row.id);
 if(item?.points!==row.points||item?.subject!==row.subject||item?.sourcePage!==row.sourcePage||
    item?.sourcePageEnd!==row.sourcePageEnd||item?.year!==row.year||
    item?.sourceText!==[row.questionText,...row.subquestions.map(sub=>sub.text)].join('\n')||
    JSON.stringify(item?.subquestions)!==JSON.stringify(row.subquestions.map(({id,number,points,text})=>({id,number,points,text})))){
  errors.push('SOURCE_OVERLAY_MISMATCH:'+row.id);
 }
}
if(items.length!==309)errors.push('TOTAL_COUNT_NOT_309:'+items.length);
if(unique.size!==ids.length)errors.push('ID_COLLISION');
if(added.length!==94)errors.push('NEW_COUNT_NOT_94:'+added.length);
if(added.some(x=>x.approved!==false||x.answerStatus!=='HOLD'||!x.sourceOnly||x.sections?.length))errors.push('UNAUTHORIZED_ANSWER_OR_APPROVAL');
if([...new Set(added.map(x=>x.year))].sort().join(',')!=='2007,2008,2009,2010,2011,2012')errors.push('WRONG_YEARS');
const pages=['second/index.html','study-hub/index.html'];
for(const f of pages){
 const s=load(f);
 const loader='legacy_2007_2012_source_only.js';
 const app=f.startsWith('second/')?'essay-app.js':'app.js';
 if(!s.includes(loader)||s.indexOf(loader)>s.indexOf('src="'+app+'"'))errors.push('SCRIPT_LOADING_ORDER:'+f);
}
if(!load('second/index.html').includes('2007~2026'))errors.push('YEAR_LABEL_MISSING');
if(status.added!==94||status.pageVerified!==94||status.status!=='SOURCE_ONLY_ANSWER_HOLD')errors.push('LEGACY_GATE_MISMATCH');
const out={status:errors.length?'FAIL':'PASS_STATIC_ONLY',total:items.length,baselineCatalog:128,archival:87,newSourceOnly:added.length,uniqueIds:unique.size,totalDistinctIds:new Set(allIds).size,years:[...new Set(items.map(x=>x.year))].sort(),errors,realBrowser:'NOT_TESTED',sourceVisualAccuracy:'NOT_TESTED_BY_THIS_SCRIPT',legalContentApproval:'HOLD',deploy:'NOT_REQUESTED'};
console.log(JSON.stringify(out,null,2));if(errors.length)process.exitCode=1;

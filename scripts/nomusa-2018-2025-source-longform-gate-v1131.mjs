#!/usr/bin/env node
// V11.31 static data integrity for 2018/2021 six answers each, 2022/23/25 four additional longforms.
// Run from repository root. This script does NOT claim browser/E2E or Vercel deployment.
import fs from 'node:fs';import vm from 'node:vm';import assert from 'node:assert/strict';
const read=p=>fs.readFileSync(p,'utf8');
const scripts=[
'rc27_essay_catalog.js','second/archive_2013_2021.js',
'second/essay-2015-2017-18q-source-linked-v1125.js','second/essay-2017-longform-v1126.js',
'second/essay-2016-hrm-longform-v1127.js','second/essay-2016-organization-longform-v1127.js',
'second/essay-2015-hrm-longform-v1128.js','second/essay-2015-organization-longform-v1128.js',
'second/essay-2018-hrm-longform-v1129.js','second/essay-2018-organization-longform-v1129.js',
'second/essay-2021-hrm-longform-v1130.js','second/essay-2021-organization-longform-v1130.js',
'second/deep-essay-2022-organization-q1-v1131.js','second/deep-essay-2023-organization-q1-v1131.js',
'second/deep-essay-2025-hrm-q2-q3-v1131.js'];
const ctx=vm.createContext({window:{},console}),counts=[];
for(const p of scripts){new vm.Script(read(p),{filename:p}).runInContext(ctx);counts.push(ctx.window.N27_CATALOG.items.length);}
const items=ctx.window.N27_CATALOG.items,byId=new Map(items.map(x=>[x.id,x]));
const targets=['2022-org-1','2023-org-1','2025-hr-2','2025-hr-3'].map(x=>byId.get(x));
const checks=[];const test=(name,fn)=>{try{fn();checks.push({name,status:'PASS'})}catch(e){checks.push({name,status:'FAIL',reason:String(e.message||e)})}};
test('245_ITEMS_NO_ID_COLLISION',()=>{
 assert.equal(counts.join(','),'128,215,233,233,233,233,233,233,236,239,242,245,245,245,245');
 assert.equal(new Set(items.map(x=>x.id)).size,items.length);
 assert.equal(items.filter(x=>x.origin==='NOMUSA_2018_SOURCE_LINKED_REVIEW').length,6);
 assert.equal(items.filter(x=>x.origin==='NOMUSA_2021_SOURCE_LINKED_REVIEW').length,6);
});
test('EXISTING_2022_2023_2025_ID_SOURCE_GUARDS',()=>{
 assert.ok(targets.every(x=>x&&x.origin==='V103_57'));
 for(const x of targets){assert.equal(x.approved,false);assert.equal(x.scoringApproved,false);
 assert.ok(x.sourceStatus.includes('HOLD'));assert.equal(x.answerStatus,'DRAFT_UNVERIFIED');
 assert.ok(x.sourceText.length>=100);
 assert.equal(x.keywords333.length,3);
 assert.ok(x.keywords333.every(g=>g.length===3));}
});
test('EXACT_POINT_ALLOCATION',()=>{
 assert.equal(targets.map(x=>x.pointsAllocation.join('/')).join('|'),'10/25/15|10/20/20|9/16|25');
});
test('DETAILED_LENGTH_REVIEW',()=>{
 for(const x of targets){const n=x.sections.reduce((z,s)=>z+s.detailed.length,0);
 assert.ok(n>=(x.points===50?4000:1900) && n<=(x.points===50?5200:2300),x.id+':'+n);
 assert.ok(x.sections.every(s=>s.detailed.length>40&&s.compressed.length>20));
 }
});
test('BOTH_HTML_INTEGRATIONS_LAST_OVERLAY',()=>{
 const names=scripts.slice(-3).map(x=>x.split('/').at(-1));
 for(const p of ['second/index.html','study-hub/index.html']){const html=read(p);
 let last=-1;for(const name of names){let pos=html.indexOf(name);assert.ok(pos>last);last=pos;assert.equal(html.split(name).length-1,1);}
 }
 const second=read('second/index.html'),hub=read('study-hub/index.html');
 assert.ok(second.indexOf(names[0])>second.indexOf('v1099-law-accuracy-gate.js'));
 assert.ok(second.indexOf(names[2])<second.indexOf('essay-app.js'));
 assert.ok(hub.indexOf(names[2])<hub.indexOf('state.js'));
 new vm.Script(read('second/essay-app.js'));new vm.Script(read('study-hub/app.js'));
});
const report={version:'V11.31',verdict:checks.every(t=>t.status==='PASS')?'STATIC_PASS_BROWSER_HOLD':'STATIC_FAIL',
checks,updated:targets.map(x=>({id:x.id,points:x.points,chars:x.sections.reduce((n,s)=>n+s.detailed.length,0),partPoints:x.pointsAllocation})),
fullContentApproval:'HOLD',academicVerification:'HOLD',qnetOriginalPageMatch:'HOLD',
browserE2E:'NOT_RUN',firstStageSaveRestore:'NOT_RUN',vercelPreview:'NOT_DEPLOYED'};
process.stdout.write(JSON.stringify(report,null,2)+'\n');if(checks.some(t=>t.status==='FAIL'))process.exitCode=1;

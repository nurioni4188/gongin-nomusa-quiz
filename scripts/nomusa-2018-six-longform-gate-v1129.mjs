#!/usr/bin/env node
// NOMUSA V11.29 2018 source-linked six-exam essay gate.
// Run at existing repository root. This is STATIC and VM only, not browser E2E.
import fs from 'node:fs';import vm from 'node:vm';import assert from 'node:assert/strict';
const read=p=>fs.readFileSync(p,'utf8');
const files=['rc27_essay_catalog.js','second/archive_2013_2021.js',
'second/essay-2015-2017-18q-source-linked-v1125.js','second/essay-2017-longform-v1126.js',
'second/essay-2016-hrm-longform-v1127.js','second/essay-2016-organization-longform-v1127.js',
'second/essay-2015-hrm-longform-v1128.js','second/essay-2015-organization-longform-v1128.js',
'second/essay-2018-hrm-longform-v1129.js','second/essay-2018-organization-longform-v1129.js'];
const ctx=vm.createContext({window:{},console}),steps=[];
for(const f of files){new vm.Script(read(f),{filename:f}).runInContext(ctx);steps.push(ctx.window.N27_CATALOG.items.length);}
const rows=ctx.window.N27_CATALOG.items,byId=new Map(rows.map(x=>[x.id,x]));
const targets=rows.filter(x=>x.origin==='NOMUSA_2018_SOURCE_LINKED_REVIEW');
const checks=[];
const gate=(name,fn)=>{try{fn();checks.push({name,status:'PASS'})}catch(err){checks.push({name,status:'FAIL',detail:String(err.message||err)})}};
gate('CATALOG_NO_OVERWRITE_OR_DUPLICATE',()=>{
 assert.equal(steps.join(','),'128,215,233,233,233,233,233,233,236,239');
 assert.equal(new Set(rows.map(x=>x.id)).size,rows.length);
 assert.equal(targets.length,6);
 assert.equal(targets.filter(x=>x.points===50).length,2);
 assert.equal(targets.filter(x=>x.points===25).length,4);
});
gate('PARENT_AND_POINTS_PRESERVED',()=>{
 for(const r of targets){
 const p=byId.get(r.parentId);assert.ok(p&&p.sourceOnly);
 for(const k of ['year','subject','pdfPath','pdfPage'])assert.equal(r[k],p[k]);
 assert.ok(r.sourceStatus.includes('ORIGINAL_PAGE_HOLD'));
 assert.equal(r.points,r.questionNo===1?50:25);
 }
 assert.equal(targets.find(x=>x.id==='2018_p5_q1').partPoints.join(','),'20,30');
});
gate('ANSWER_VOLUME_AND_REVIEW_ONLY',()=>{
 for(const r of targets){
 const n=r.sections.reduce((sum,s)=>sum+s.detailed.length,0);
 assert.ok(n>=(r.points===50?4000:1900)&&n<=(r.points===50?5100:2300),r.id+':'+n);
 assert.ok(r.sections.length>=6&&r.sections.every(s=>s.detailed.length>=50&&s.compressed.length>=20));
 assert.ok(r.keywords333.length===3&&r.keywords333.every(g=>g.length===3));
 assert.equal(r.answerStatus,'DRAFT_UNVERIFIED');assert.equal(r.approved,false);assert.equal(r.scoringApproved,false);
 }
});
gate('BOTH_EXISTING_ENTRIES',()=>{
 for(const p of ['second/index.html','study-hub/index.html']){
 const s=read(p),a=s.indexOf('essay-2018-hrm-longform-v1129.js'),b=s.indexOf('essay-2018-organization-longform-v1129.js');
 assert.ok(a>=0&&b>a);
 assert.equal(s.split('essay-2018-hrm-longform-v1129.js').length,2);
 assert.equal(s.split('essay-2018-organization-longform-v1129.js').length,2);
 }
 new vm.Script(read('second/essay-app.js'));new vm.Script(read('study-hub/app.js'));
});
const report={version:'V11.29',verdict:checks.every(x=>x.status==='PASS')?'STATIC_PASS_BROWSER_HOLD':'STATIC_FAIL',checks,
rows2018:targets.map(r=>({id:r.id,points:r.points,chars:r.sections.reduce((n,s)=>n+s.detailed.length,0)})),
originalPDFPages:'HOLD_DIFF_REPRINT_PAGE_ORDER',academicApproval:'HOLD',historicalLawApproval:'HOLD',
browserE2E:'NOT_RUN',previewDeployment:'NOT_PERFORMED',mainAndProduction:'NOT_CHANGED'};
process.stdout.write(JSON.stringify(report,null,2)+'\n');
if(checks.some(x=>x.status==='FAIL'))process.exitCode=1;

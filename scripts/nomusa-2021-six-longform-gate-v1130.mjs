#!/usr/bin/env node
// NOMUSA V11.30 reproducible 2021 six-essay static/in-memory integration gate
// Run from the existing repository root. No browser E2E, production or Preview deployment.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const read=p=>fs.readFileSync(p,'utf8');
const files=[
 'rc27_essay_catalog.js','second/archive_2013_2021.js',
 'second/essay-2015-2017-18q-source-linked-v1125.js',
 'second/essay-2017-longform-v1126.js','second/essay-2016-hrm-longform-v1127.js',
 'second/essay-2016-organization-longform-v1127.js',
 'second/essay-2015-hrm-longform-v1128.js',
 'second/essay-2015-organization-longform-v1128.js',
 'second/essay-2018-hrm-longform-v1129.js','second/essay-2018-organization-longform-v1129.js',
 'second/essay-2021-hrm-longform-v1130.js','second/essay-2021-organization-longform-v1130.js'
];
const ctx=vm.createContext({window:{},console}),snapshots=[];
for(const path of files){new vm.Script(read(path),{filename:path}).runInContext(ctx);snapshots.push(ctx.window.N27_CATALOG.items.length)}
const items=ctx.window.N27_CATALOG.items,allIds=new Set(items.map(x=>x.id)),parentMap=new Map(items.map(x=>[x.id,x]));
const answers=items.filter(x=>x.origin==='NOMUSA_2021_SOURCE_LINKED_REVIEW');
const tests=[];
const check=(name,fn)=>{try{fn();tests.push({name,status:'PASS'});}catch(err){tests.push({name,status:'FAIL',detail:String(err.message||err)})}};
check('CATALOG_245_WITHOUT_COLLISION',()=>{
 assert.equal(snapshots.join(','),'128,215,233,233,233,233,233,233,236,239,242,245');
 assert.equal(allIds.size,items.length);assert.equal(answers.length,6);
 assert.equal(answers.filter(x=>x.points===50).length,2);assert.equal(answers.filter(x=>x.points===25).length,4);
});
check('UNCHANGED_PARENTS_AND_PDF_REF',()=>{
 for(const a of answers){const p=parentMap.get(a.parentId);
 assert.ok(p&&p.sourceOnly);assert.equal(p.year,2021);
 for(const k of ['year','subject','pdfPath','pdfPage'])assert.equal(a[k],p[k]);
 assert.ok(a.sourceStatus.includes('HOLD'));
 assert.equal(a.answerStatus,'DRAFT_UNVERIFIED');assert.equal(a.approved,false);assert.equal(a.scoringApproved,false);}
});
check('DETAILED_COMPRESSED_MNEMONIC_LENGTH',()=>{
 for(const a of answers){const chars=a.sections.reduce((n,s)=>n+s.detailed.length,0);
 assert.ok(chars>=(a.points===50?4000:1900)&&chars<=(a.points===50?5100:2500),a.id+':'+chars);
 assert.ok(a.sections.length>=6&&a.sections.every(s=>s.detailed.length>=50&&s.compressed.length>=20));
 assert.ok(a.keywords333.length===3&&a.keywords333.every(g=>g.length===3));
 }
});
check('ORIGINAL_SUBQUESTION_POINTS',()=>{
 assert.equal(answers.find(x=>x.id==='2021-경영조직론-q1').partPoints.join(','),'20,15,15');
 assert.equal(answers.find(x=>x.id==='2021-경영조직론-q2').partPoints.join(','),'6,6,7,6');
 assert.equal(answers.find(x=>x.id==='2021-경영조직론-q3').partPoints.join(','),'10,15');
});
check('HISTORICAL_2021_HARASSMENT_LAW',()=>{
 const q3=answers.find(x=>x.id==='2021-인사노무관리론-q3');
 assert.ok(q3.academicOrLawReferences.some(s=>s.includes('17862')));
 assert.ok(q3.academicOrLawReferences.some(s=>s.includes('2021-10-14')));
 assert.ok(q3.sections.some(s=>s.detailed.includes('소급')));
});
check('BOTH_LEARNING_ENTRY_POINTS',()=>{
 for(const path of ['second/index.html','study-hub/index.html']){
 const s=read(path),a=s.indexOf('essay-2021-hrm-longform-v1130.js'),b=s.indexOf('essay-2021-organization-longform-v1130.js');
 assert.ok(a>=0&&b>a);assert.equal(s.split('essay-2021-hrm-longform-v1130.js').length,2);
 assert.equal(s.split('essay-2021-organization-longform-v1130.js').length,2);
 }
 new vm.Script(read('second/essay-app.js'));
 new vm.Script(read('study-hub/app.js'));
});
const report={version:'V11.30',staticVerdict:tests.every(x=>x.status==='PASS')?'PASS':'FAIL',tests,
counts:answers.map(x=>({id:x.id,points:x.points,chars:x.sections.reduce((n,s)=>n+s.detailed.length,0)})),
lawDate:'2021-08-21',postExamLawEffective:'2021-10-14',historicalLawSubstanceApproval:'HOLD',
originalPdfPageMapping:'HOLD',answerContentFinalApproval:'HOLD',realBrowserE2E:'NOT_RUN',vercelPreview:'NOT_DEPLOYED'};
process.stdout.write(JSON.stringify(report,null,2)+'\n');if(tests.some(x=>x.status==='FAIL'))process.exitCode=1;

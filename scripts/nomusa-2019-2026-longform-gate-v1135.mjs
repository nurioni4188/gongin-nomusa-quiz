#!/usr/bin/env node
// NOMUSA V11.35: 2019–2020 legacy sidecar & 2024–2026 native catalog content QA.
// Execute from existing repo root with Node. No browser automation or deployment.
import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';
const read=p=>fs.readFileSync(p,'utf8');
const files=[
'rc27_essay_catalog.js',
'second/archive_2013_2021.js',
'second/legacy_2007_2012_source_only.js',
'second/legacy-181-answer-drafts-v1110.js',
'second/deep-essay-2019-hrm-q1.js',
'second/deep-essay-2019-organization-q2.js',
'second/deep-essay-2020-organization-q3.js',
'second/deep-essay-2020-hrm-q3.js',
'second/deep-essay-2019-four-v1132.js',
'second/deep-essay-2020-four-v1133.js',
'second/deep-essay-2024-hrm-v1134.js',
'second/deep-essay-2024-organization-v1134.js',
'second/deep-essay-2026-hrm-v1135.js',
'second/deep-essay-2026-organization-v1135.js'
];
const ctx=vm.createContext({window:{},console}),length=[];
for(const p of files){
 new vm.Script(read(p),{filename:p}).runInContext(ctx);
 length.push(ctx.window.N27_CATALOG.items.length);
}
const current=ctx.window.N27_CATALOG.items;
const sidecar=ctx.window.NOMUSA_LEGACY_181_DRAFTS?.items||{};
const base=vm.createContext({window:{},console});
new vm.Script(read('rc27_essay_catalog.js')).runInContext(base);
const orig=new Map(base.window.N27_CATALOG.items.map(x=>[x.id,x]));
const targets=current.filter(r=>[2024,2026].includes(r.year)&&['인사노무관리론','경영조직론'].includes(r.subject));
const older=Object.values(sidecar).filter(r=>[2019,2020].includes(r.year)&&['인사노무관리론','경영조직론'].includes(r.subject));
const tests=[];const test=(label,fn)=>{try{fn();tests.push({label,status:'PASS'})}catch(e){tests.push({label,status:'FAIL',error:String(e.message||e)})}};
test('NATIVE_CATALOG_AND_ID_STABILITY',()=>{
 assert.equal(length.join(','),'128,215,309,309,309,309,309,309,309,309,309,309,309,309');
 assert.equal(new Set(current.map(x=>x.id)).size,current.length);
 assert.equal(Object.keys(sidecar).length,181);
 assert.equal(targets.length,24);
});
test('2019_2020_TWELVE_INDIVIDUAL_ESSAYS',()=>{
 assert.equal(older.length,12);
 for(const year of [2019,2020]){const rows=older.filter(x=>x.year===year);
 assert.equal(rows.length,6);
 assert.equal(rows.filter(x=>(x.examPoints||x.points)===50).length,2);
 assert.equal(rows.filter(x=>(x.examPoints||x.points)===25).length,4);}
 assert.ok(older.every(x=>x.authoring==='INDIVIDUAL_SOURCE_GROUNDED_ESSAY'&&x.draftStatus==='DRAFT_UNVERIFIED'&&x.scoringApproved===false));
});
test('2024_2026_24_SOURCE_SUBQUESTIONS',()=>{
 for(const year of [2024,2026]){const rows=targets.filter(x=>x.year===year);assert.equal(rows.length,12);}
 for(const row of targets){const p=orig.get(row.id);assert.ok(p);
 for(const k of ['id','year','subject','points','pdfPath','pdfPage','origin','sourceText'])assert.equal(row[k],p[k],row.id+':'+k);
 assert.equal(row.approved,false);assert.equal(row.scoringApproved,false);assert.equal(row.contentApproval,'HOLD');
 assert.equal(row.enhancementStatus,'DRAFT_UNVERIFIED');
 assert.ok(row.sections.length>=2);}
});
test('PER_BIG_QUESTION_POINTS_AND_VOLUME',()=>{
 const g=new Map();
 for(const row of targets){const k=row.year+'|'+row.subject+'|'+row.id.split('|')[1];
 const v=g.get(k)||{points:0,chars:0};v.points+=row.points;v.chars+=row.sections.reduce((n,s)=>n+s.detailed.length,0);g.set(k,v)}
 assert.equal(g.size,12);
 for(const [k,v] of g){assert.ok(v.points===25||v.points===50,k);
 const lo=v.points===50?4000:1850,hi=v.points===50?5000:2650;
 assert.ok(v.chars>=lo&&v.chars<=hi,k+':'+v.chars)}
});
test('BOTH_SCREENS_AND_HISTORIC_STUDY_SIDECAR',()=>{
 const hub=read('study-hub/index.html'),essay=read('second/index.html');
 for(const filename of ['deep-essay-2024-hrm-v1134.js','deep-essay-2024-organization-v1134.js',
 'deep-essay-2026-hrm-v1135.js','deep-essay-2026-organization-v1135.js']){
 for(const html of [hub,essay])assert.equal(html.split(filename).length-1,1,filename);
 }
 for(const filename of ['deep-essay-2019-four-v1132.js','deep-essay-2020-four-v1133.js'])
 assert.equal(hub.split(filename).length-1,1);
 assert.ok(hub.indexOf('deep-essay-2019-four-v1132.js')>hub.indexOf('deep-essay-2019-hrm-q1.js'));
 assert.ok(hub.indexOf('deep-essay-2020-four-v1133.js')>hub.indexOf('deep-essay-2020-hrm-q3.js'));
 for(const p of ['second/essay-app.js','study-hub/app.js'])new vm.Script(read(p),{filename:p});
});
const report={version:'V11.35',verdict:tests.every(x=>x.status==='PASS')?'IN_MEMORY_AND_STATIC_PASS':'STATIC_FAIL',tests,
notes:['500 characters per sheet is an estimate and not actual handwriting verification','2019–2020 essays live in the legacy sidecar consumed by study-hub, not the standalone second app'],
contentFinalApproval:'HOLD',originalPdfVisualAndLawReview:'HOLD',independentNodeExecution:'RUN_THIS_SCRIPT_FROM_REPO',
browser1440_390_360:'NOT_RUN',saveRestoreE2E:'NOT_RUN',vercelPreview:'NOT_DEPLOYED'};
process.stdout.write(JSON.stringify(report,null,2)+'\n');
if(tests.some(x=>x.status==='FAIL'))process.exitCode=1;

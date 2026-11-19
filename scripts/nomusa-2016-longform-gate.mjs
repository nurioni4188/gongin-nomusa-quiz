#!/usr/bin/env node
// V11.27 reproducible source-only integration gate. Runs without browser or deployment.
// From repository root: node scripts/nomusa-2016-longform-gate.mjs
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const read = path => fs.readFileSync(path,'utf8');
const context=vm.createContext({window:{},console});
const modules=[
  'rc27_essay_catalog.js',
  'second/archive_2013_2021.js',
  'second/essay-2015-2017-18q-source-linked-v1125.js',
  'second/essay-2017-longform-v1126.js',
  'second/essay-2016-hrm-longform-v1127.js',
  'second/essay-2016-organization-longform-v1127.js'
];
const snapshots=[];
for(const path of modules){new vm.Script(read(path),{filename:path}).runInContext(context);snapshots.push(context.window.N27_CATALOG.items.length)}
const catalog=context.window.N27_CATALOG.items;
const originals=new Map(catalog.map(x=>[x.id,x]));
const years2016=catalog.filter(x=>x.year===2016&&x.origin==='NOMUSA_2015_2017_18Q_REVIEW');
const checked=[];
const test=(name,fn)=>{try{fn();checked.push({name,result:'PASS'})}catch(error){checked.push({name,result:'FAIL',reason:String(error.message||error)})}};
test('CATALOG_LOAD_AND_IDENTITY',()=>{
 assert.equal(snapshots.join(','),'128,215,233,233,233,233');
 assert.equal(new Set(catalog.map(x=>x.id)).size,catalog.length);
 assert.equal(years2016.length,6);
 assert.equal(years2016.filter(x=>x.points===50).length,2);
 assert.equal(years2016.filter(x=>x.points===25).length,4);
});
test('PARENT_ID_PDF_AND_SOURCE_UNCHANGED',()=>{
 for(const e of years2016){const p=originals.get(e.parentId);assert.ok(p&&p.sourceOnly);
 for(const f of ['year','subject','pdfPath','pdfPage'])assert.equal(e[f],p[f]);
 assert.equal(e.questionNo,Number(e.id.match(/q(\d)$/)?.[1]));
 }
});
test('2016_DETAIL_COMPRESSED_MEMORY_AND_HOLD',()=>{
 for(const e of years2016){
  const chars=e.sections.reduce((n,s)=>n+s.detailed.length,0);
  assert.ok(chars>=(e.points===50?4000:1900) && chars<=(e.points===50?5000:2300),e.id+':'+chars);
  assert.ok(e.sections.length>=6&&e.sections.every(s=>s.detailed.length>=30&&s.compressed.length>=20));
  assert.equal(e.keywords333.length,3);assert.ok(e.keywords333.every(g=>g.length===3));
  assert.equal(e.approved,false);assert.equal(e.scoringApproved,false);
  assert.equal(e.answerStatus,'DRAFT_UNVERIFIED');
  assert.equal(e.contentRevision,'V11.27_2016_LONGFORM_DRAFT');
 }
});
test('2017_AND_2015_PRESERVED',()=>{
 const e2017=catalog.filter(x=>x.year===2017&&x.origin==='NOMUSA_2015_2017_18Q_REVIEW');
 const e2015=catalog.filter(x=>x.year===2015&&x.origin==='NOMUSA_2015_2017_18Q_REVIEW');
 assert.equal(e2017.length,6);assert.equal(e2015.length,6);
 assert.ok(e2017.every(x=>x.contentRevision==='V11.26_2017_LONGFORM_DRAFT'));
 assert.ok(e2015.every(x=>!x.contentRevision));
});
test('EXISTING_UI_ENTRY_POINTS',()=>{
 for(const f of ['second/index.html','study-hub/index.html']){
   const s=read(f);
   let last=-1;for(const script of modules.slice(2)){const token=script.split('/').pop(),pos=s.indexOf(token);assert.ok(pos>last,'script load order '+f+' '+token);assert.equal(s.split(token).length-1,1);last=pos}
 }
 new vm.Script(read('second/essay-app.js'),{filename:'second/essay-app.js'});
 new vm.Script(read('study-hub/app.js'),{filename:'study-hub/app.js'});
 assert.ok(read('second/essay-app.js').includes('nomusa_rc27_v103_essay_records_v1'));
});
const out={
 version:'V11.27',verdict:checked.every(x=>x.result==='PASS')?'STATIC_AND_IN_MEMORY_PASS_BROWSER_HOLD':'STATIC_FAIL',
 tests:checked,
 targetNote:'500 Korean characters/sheet is a study estimate, not physical handwritten proof',
 contentApproval:'HOLD',qnetOfficialByteMatch:'HOLD',browserE2E:'NOT_RUN',previewDeployment:'NOT_PERFORMED',
 answerCharacters:years2016.map(e=>({id:e.id,points:e.points,chars:e.sections.reduce((n,s)=>n+s.detailed.length,0)}))
};
process.stdout.write(JSON.stringify(out,null,2)+'\n');
if(checked.some(x=>x.result==='FAIL'))process.exitCode=1;

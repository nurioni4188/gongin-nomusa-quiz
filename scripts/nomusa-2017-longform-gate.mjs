#!/usr/bin/env node
// NOMUSA V11.26 reproducible static/in-memory integration gate.
// Usage: node scripts/nomusa-2017-longform-gate.mjs (from repository root).
// This checks catalog/script integration only. It DOES NOT run Chromium or deploy.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const read = file => fs.readFileSync(file,'utf8');
const context=vm.createContext({window:{},console});
const loaded=[];
for (const file of [
  'rc27_essay_catalog.js',
  'second/archive_2013_2021.js',
  'second/essay-2015-2017-18q-source-linked-v1125.js',
  'second/essay-2017-longform-v1126.js'
]){
  new vm.Script(read(file),{filename:file}).runInContext(context);
  loaded.push({file,catalogItems:context.window.N27_CATALOG.items.length});
}
const items=context.window.N27_CATALOG.items;
const essays=items.filter(r=>r.origin==='NOMUSA_2015_2017_18Q_REVIEW');
const year2017=essays.filter(r=>r.year===2017);
const allIds=new Set(items.map(x=>x.id));
const parentIds=new Set(essays.map(x=>x.parentId));
const parentMap=new Map(items.map(x=>[x.id,x]));
const results=[];
const check=(name,fn)=>{try{fn();results.push({name,status:'PASS'});}catch(err){results.push({name,status:'FAIL',detail:String(err.message||err)});}};
check('UNMODIFIED_BASE_AND_18_CHILDREN',()=>{
  assert.deepEqual(loaded.map(x=>x.catalogItems),[128,215,233,233]);
  assert.equal(allIds.size,items.length);
  assert.equal(essays.length,18);
  assert.equal(parentIds.size,6);
  for(const e of essays){
    const p=parentMap.get(e.parentId);assert.ok(p&&p.sourceOnly);
    for(const k of ['year','subject','pdfPath','pdfPage'])assert.equal(e[k],p[k]);
    assert.equal(e.points,e.questionNo===1?50:25);
  }
});
check('SIX_2017_DETAILED_ANSWERS_TARGET',()=>{
  assert.equal(year2017.length,6);
  assert.equal(year2017.filter(x=>x.points===50).length,2);
  assert.equal(year2017.filter(x=>x.points===25).length,4);
  for(const e of year2017){
    const chars=e.sections.reduce((n,s)=>n+s.detailed.length,0);
    const low=e.points===50?4000:1900;
    const high=e.points===50?5000:2300;
    assert.ok(chars>=low&&chars<=high,e.id+' chars='+chars+' outside '+low+'-'+high);
    assert.ok(e.sections.every(s=>s.detailed.length>=30&&s.compressed.length>=20));
    assert.equal(e.keywords333.length,3);
    assert.ok(e.keywords333.every(g=>g.length===3));
    assert.equal(e.approved,false);
    assert.equal(e.scoringApproved,false);
    assert.equal(e.answerStatus,'DRAFT_UNVERIFIED');
    assert.equal(e.contentRevision,'V11.26_2017_LONGFORM_DRAFT');
  }
});
check('2017_LABOR_LAW_TAXONOMY_CORRECTION',()=>{
  const e=year2017.find(x=>x.id==='2017_p3_q3');
  assert.ok(e);
  assert.ok(e.sections[0].detailed.includes('사보타지'));
  assert.ok(!e.sections[0].detailed.includes('⑤직장점거'));
  assert.ok(e.keywords333.flat().includes('사보타지'));
});
check('BOTH_UI_SCRIPT_TAGS_IN_LOAD_ORDER',()=>{
  for(const file of ['second/index.html','study-hub/index.html']){
    const s=read(file),v1125=s.indexOf('essay-2015-2017-18q-source-linked-v1125.js'),v1126=s.indexOf('essay-2017-longform-v1126.js');
    assert.ok(v1125>=0&&v1126>v1125,'wrong order '+file);
    assert.equal(s.split('essay-2017-longform-v1126.js').length-1,1);
  }
  new vm.Script(read('second/essay-app.js'));
  new vm.Script(read('study-hub/app.js'));
});
check('2016_2015_AND_OLD_STORAGE_UNCHANGED',()=>{
  assert.ok(essays.filter(x=>x.year<2017).every(x=>!x.contentRevision));
  assert.ok(read('second/essay-app.js').includes('nomusa_rc27_v103_essay_records_v1'));
  assert.ok(read('study-hub/index.html').includes('<script src="state.js"></script>'));
});
const stats=year2017.map(e=>({
  id:e.id,points:e.points,
  detailedChars:e.sections.reduce((n,s)=>n+s.detailed.length,0),
  estimatedPages:e.sections.reduce((n,s)=>n+s.detailed.length,0)/500,
  targetPages:e.points===50?'8-10':'4',
  wordCountIsEstimated:true,
  status:'DRAFT_UNVERIFIED'
}));
const output={
  version:'V11.26',status:results.every(x=>x.status==='PASS')?'STATIC_PASS_BROWSER_HOLD':'STATIC_FAIL',
  tests:results,
  stats,
  contentApproval:'HOLD',
  verifiedRealHandwrittenPageCount:false,
  browserE2E:'NOT_RUN',
  previewDeployment:'NOT_PERFORMED',
  sourceQnetHashIdentity:'HOLD',
  baselinePreserved:true
};
process.stdout.write(JSON.stringify(output,null,2)+'\n');
if(results.some(x=>x.status==='FAIL'))process.exitCode=1;

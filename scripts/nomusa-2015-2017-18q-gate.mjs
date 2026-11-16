#!/usr/bin/env node
// V11.25 — additive 2015–2017 source-linked 18-question integrity gate.
// Run from repository root: node scripts/nomusa-2015-2017-18q-gate.mjs
// No browser, network, deployment, file writes, score approval or saved-record mutation.
import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';

const paths = [
  'rc27_essay_catalog.js',
  'second/archive_2013_2021.js',
  'second/essay-2015-2017-18q-source-linked-v1125.js'
];
const ctx = vm.createContext({ window: {}, console });
const read = p => fs.readFileSync(p, 'utf8');
const checked = (name, fn) => { try { fn(); return {name,status:'PASS'}; } catch (error) {return {name,status:'FAIL',reason:String(error.message || error)};} };
const tests = [];

for (const p of paths) {
  new vm.Script(read(p), {filename:p}).runInContext(ctx);
}
const initial = ctx.window.N27_CATALOG.items.filter(x => /^(2015|2016|2017)_p[35]$/.test(x.id));
const snapshot = JSON.stringify(initial.map(x => ({id:x.id,year:x.year,subject:x.subject,pdfPath:x.pdfPath,pdfPage:x.pdfPage,points:x.points,sourceOnly:x.sourceOnly})));
const data=ctx.window.N27_CATALOG.items;
const sidecar=ctx.window.NOMUSA_2015_2017_18Q;
const children=data.filter(x => x.origin==='NOMUSA_2015_2017_18Q_REVIEW');
const base=data.filter(x => !children.includes(x));
const basemap=new Map(base.map(x => [x.id,x]));
tests.push(checked('18_CHILD_IDS_UNIQUE_AND_BASE_UNTOUCHED',() => {
  assert.equal(children.length,18);
  assert.equal(new Set(data.map(x=>x.id)).size,data.length);
  assert.equal(data.length,233,'expected 215 existing catalog items plus 18 question children');
  assert.equal(initial.length,6);
  assert.equal(JSON.stringify(initial.map(x => ({id:x.id,year:x.year,subject:x.subject,pdfPath:x.pdfPath,pdfPage:x.pdfPage,points:x.points,sourceOnly:x.sourceOnly}))),snapshot);
  assert.equal(sidecar.questionCount,18);
  assert.equal(sidecar.existingParentsUnchanged,true);
}));
tests.push(checked('PARENT_PDF_AND_POINTS',() => {
  assert.equal(new Set(children.map(x=>x.parentId)).size,6);
  assert.equal(children.filter(x=>x.points===50).length,6);
  assert.equal(children.filter(x=>x.points===25).length,12);
  for (const row of children) {
    const parent=basemap.get(row.parentId);
    assert.ok(parent,'parent missing '+row.id);
    assert.equal(row.year,parent.year);
    assert.equal(row.subject,parent.subject);
    assert.equal(row.pdfPath,parent.pdfPath);
    assert.equal(row.pdfPage,parent.pdfPage);
    assert.equal(row.points,row.questionNo===1?50:25);
  }
}));
tests.push(checked('DETAIL_COMPACT_MEMORY_DRAFT_GUARDS',() => {
  for (const row of children) {
    assert.ok(row.sections.length>0);
    assert.ok(row.sections.every(s=>s.detailed.length>=30&&s.compressed.length>=20));
    assert.equal(row.keywords333.length,3);
    assert.ok(row.keywords333.every(g=>g.length===3));
    assert.equal(row.approved,false);
    assert.equal(row.scoringApproved,false);
    assert.equal(row.answerStatus,'DRAFT_UNVERIFIED');
    assert.equal(row.sourceOnly,false);
  }
}));
tests.push(checked('LOAD_ORDER_BOTH_UI_ENTRYPOINTS',() => {
  for (const p of ['second/index.html','study-hub/index.html']) {
    const s=read(p);
    const a=s.indexOf('archive_2013_2021.js'),b=s.indexOf('essay-2015-2017-18q-source-linked-v1125.js');
    assert.ok(a>=0&&b>a);
    assert.ok((s.match(/essay-2015-2017-18q-source-linked-v1125\.js/g)||[]).length===1);
  }
  assert.ok(read('study-hub/app.js').includes('NOMUSA_2015_2017_18Q_REVIEW'));
  new vm.Script(read('study-hub/app.js'),{filename:'study-hub/app.js'});
  new vm.Script(read('second/essay-app.js'),{filename:'second/essay-app.js'});
}));
const totalChars=children.reduce((n,r)=>n+r.sections.reduce((m,s)=>m+s.detailed.length,0),0);
const targets=children.map(r=>({id:r.id,points:r.points,characters:r.sections.reduce((n,s)=>n+s.detailed.length,0),targetPages:r.points===50?'8~10':'4',targetComplete:false}));
const output={
  gate:'NOMUSA_V1125_2015_2017_18Q',
  status:tests.every(t=>t.status==='PASS')?'STATIC_PASS_BROWSER_HOLD':'STATIC_FAIL',
  checks:tests,
  yearCounts:Object.fromEntries([2017,2016,2015].map(y=>[y,children.filter(x=>x.year===y).length])),
  totalDraftCharacters:totalChars,
  lengthGate:'HOLD_INSUFFICIENT_FOR_TARGET_PAGES',
  contentApproval:'HOLD',
  browserE2E:'NOT_RUN',
  deployment:'NOT_REQUESTED',
  targets
};
process.stdout.write(JSON.stringify(output,null,2)+'\n');
if (tests.some(t=>t.status==='FAIL'))process.exitCode=1;

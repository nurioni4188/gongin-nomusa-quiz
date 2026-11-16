#!/usr/bin/env node
// V11.28 exam learning hub integrity gate. Execute from existing repository root.
// No deploy, network requests, browser, score approval or saved-record mutation.
import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';
const read=p=>fs.readFileSync(p,'utf8');
const ctx=vm.createContext({window:{},console});
const files=[
 'rc27_essay_catalog.js',
 'second/archive_2013_2021.js',
 'second/essay-2015-2017-18q-source-linked-v1125.js',
 'second/essay-2017-longform-v1126.js',
 'second/essay-2016-hrm-longform-v1127.js',
 'second/essay-2016-organization-longform-v1127.js',
 'second/essay-2015-hrm-longform-v1128.js',
 'second/essay-2015-organization-longform-v1128.js'
];
const steps=[];
for(const file of files){
 new vm.Script(read(file),{filename:file}).runInContext(ctx);
 steps.push(ctx.window.N27_CATALOG.items.length);
}
const all=ctx.window.N27_CATALOG.items;
const byId=new Map(all.map(x=>[x.id,x]));
const exercise=all.filter(x=>x.origin==='NOMUSA_2015_2017_18Q_REVIEW');
const perYear=year=>exercise.filter(x=>x.year===year);
const checks=[];
const test=(name,fn)=>{try{fn();checks.push({name,status:'PASS'});}catch(e){checks.push({name,status:'FAIL',reason:String(e.message||e)});}};
test('BASE_215_AND_ADDITIVE_18_STABLE',()=>{
 assert.equal(steps.join(','),'128,215,233,233,233,233,233,233');
 assert.equal(all.length,233);
 assert.equal(new Set(all.map(r=>r.id)).size,all.length);
 assert.equal(exercise.length,18);
 assert.equal(new Set(exercise.map(x=>x.parentId)).size,6);
});
test('PARENT_PDF_MAPPING_AND_POINTS',()=>{
 for(const r of exercise){
 const p=byId.get(r.parentId);
 assert.ok(p&&p.sourceOnly,'Missing source-only parent for '+r.id);
 for(const f of ['year','subject','pdfPath','pdfPage'])assert.equal(r[f],p[f],r.id+':'+f);
 assert.equal(r.points,r.questionNo===1?50:25);
 }
 for(const year of [2015,2016,2017]){
 const set=perYear(year);assert.equal(set.length,6);
 assert.equal(set.filter(x=>x.points===50).length,2);
 assert.equal(set.filter(x=>x.points===25).length,4);
 }
});
test('THREE_YEARS_FULL_LENGTH_DRAFTS',()=>{
 for(const year of [2015,2016,2017]){
  for(const r of perYear(year)){
    const chars=r.sections.reduce((n,s)=>n+s.detailed.length,0);
    const lo=r.points===50?4000:1900,hi=r.points===50?5200:2300;
    assert.ok(chars>=lo&&chars<=hi,r.id+':'+chars+' outside '+lo+'-'+hi);
    assert.ok(r.sections.every(s=>s.detailed.length>=30&&s.compressed.length>=20),r.id+' incomplete sections');
    assert.equal(r.keywords333.length,3);
    assert.ok(r.keywords333.every(g=>g.length===3));
    assert.equal(r.approved,false);
    assert.equal(r.scoringApproved,false);
    assert.equal(r.answerStatus,'DRAFT_UNVERIFIED');
    assert.equal(r.contentRevision,({2015:'V11.28_2015_LONGFORM_DRAFT',2016:'V11.27_2016_LONGFORM_DRAFT',2017:'V11.26_2017_LONGFORM_DRAFT'})[year]);
  }
 }
});
test('EXACT_TWO_SUBJECTS_IN_2015',()=>{
 const r=perYear(2015);
 assert.equal(r.filter(x=>x.subject==='인사노무관리론').length,3);
 assert.equal(r.filter(x=>x.subject==='경영조직론').length,3);
 assert.equal(ctx.window.NOMUSA_2015_HRM_LONGFORM?.officialApproved,0);
 assert.equal(ctx.window.NOMUSA_2015_ORG_LONGFORM?.officialApproved,0);
});
test('UI_LOAD_ORDER_AND_JAVASCRIPT_SYNTAX',()=>{
 for(const path of ['second/index.html','study-hub/index.html']){
 const html=read(path);let last=-1;
 for(const source of files.slice(2)){
  const name=source.split('/').at(-1),offset=html.indexOf(name);
  assert.ok(offset>last,path+': bad script load order '+name);
  assert.equal(html.split(name).length-1,1,path+': duplicate '+name);
  last=offset;
 }
 }
 new vm.Script(read('second/essay-app.js'));
 new vm.Script(read('study-hub/app.js'));
});
test('EXISTING_STUDY_STORAGE_AND_APPROVAL_GUARDS',()=>{
 assert.ok(read('second/essay-app.js').includes('nomusa_rc27_v103_essay_records_v1'));
 assert.ok(read('study-hub/index.html').includes('<script src="state.js"></script>'));
 assert.ok(exercise.every(r=>r.sourceStatus==='REPRINT_PAGE_VISUAL_CHECKED_QNET_BYTES_HOLD'));
});
const output={
 version:'V11.28',
 verdict:checks.every(x=>x.status==='PASS')?'STATIC_AND_IN_MEMORY_PASS_BROWSER_HOLD':'STATIC_FAIL',
 tests:checks,
 stats:Object.fromEntries([2015,2016,2017].map(y=>[y,perYear(y).map(r=>({id:r.id,points:r.points,detailedChars:r.sections.reduce((n,s)=>n+s.detailed.length,0),pagesEstimatedAt500Chars:r.sections.reduce((n,s)=>n+s.detailed.length,0)/500,contentApproved:false}))])),
 caution:'500 chars/sheet is user study estimate, not physical handwriting validation',
 originalPDFVisual:'REPRINT_SCAN_CHECKED',
 qnetOfficialFileByteEquality:'HOLD',
 historicalLegalAndAcademicReview:'HOLD',
 browserE2E:'NOT_RUN',
 previewDeployment:'NOT_PERFORMED',
 productionChange:'NOT_REQUESTED'
};
process.stdout.write(JSON.stringify(output,null,2)+'\n');
if(checks.some(t=>t.status==='FAIL'))process.exitCode=1;

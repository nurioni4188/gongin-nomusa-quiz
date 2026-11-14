#!/usr/bin/env node
// NOMUSA-AUTO V1.1: safe read-only provenance / integrity gate.
import fs from 'node:fs'; import path from 'node:path'; import crypto from 'node:crypto';
const root=path.resolve(process.argv[2]||'.');
const manifest=JSON.parse(fs.readFileSync(path.join(root,'review/NOMUSA_AUTO_V1_20YEAR_SOURCE_MANIFEST.json'),'utf8'));
const original=JSON.parse(fs.readFileSync(path.join(root,'second/ARCHIVE_MANIFEST.json'),'utf8'));
const proposals=JSON.parse(fs.readFileSync(path.join(root,'review/NOMUSA_AUTO_V1_PROPOSED_QUESTIONS.json'),'utf8'));
const failures=[],holds=[];
const years=Array.from({length:20},(_,i)=>i+2007);
if(JSON.stringify(original.years)!==JSON.stringify(years.slice(6)))failures.push('ORIGINAL_2013_2026_YEAR_LIST_CHANGED');
if(original.baseline_count!==128||original.total_study_units!==215)failures.push('ORIGINAL_UNIT_COUNTS_CHANGED');
if(manifest.newSources.length!==6||new Set(manifest.newSources.map(s=>s.year)).size!==6)failures.push('EXPECTED_SIX_NEW_YEARS');
for(const source of manifest.newSources){
 if(source.year<2007||source.year>2012||!(/^[a-f0-9]{64}$/).test(source.sha256)||source.approved!==false)failures.push('SOURCE_MANIFEST_INVALID:'+source.year);
 const local=path.join(root,'incoming',source.filename);
 if(fs.existsSync(local)){
  const digest=crypto.createHash('sha256').update(fs.readFileSync(local)).digest('hex');
  if(digest!==source.sha256)failures.push('SOURCE_SHA_MISMATCH:'+source.year);
 }else holds.push('SOURCE_BINARY_NOT_IN_REPO:'+source.year);
}
if(original.source_files_sha256?.[manifest.boundary2013.existingPath]!==manifest.boundary2013.uploadedSha256)failures.push('2013_SOURCE_HASH_COLLISION');
if(manifest.duplicateEvidence.sha256!==manifest.newSources.find(s=>s.year===2009)?.sha256)failures.push('2009_DUPLICATE_SOURCE_HASH_MISMATCH');
if(manifest.idPolicy.existingIds!=='IMMUTABLE'||manifest.idPolicy.existingStorageKeys!=='IMMUTABLE')failures.push('PRESERVATION_POLICY_INVALID');
if(manifest.deployment.preview!=='FORBIDDEN_UNTIL_USER_APPROVAL'||manifest.deployment.production!=='FORBIDDEN'||manifest.deployment.main!=='FORBIDDEN')failures.push('DEPLOYMENT_POLICY_INVALID');
for(const p of ['study-hub/state.js','second/essay-app.js','second/index.html','scripts/v1107-source-gate.mjs']){
 if(!fs.existsSync(path.join(root,p)))failures.push('BASELINE_FILE_MISSING:'+p);
}
if(!Array.isArray(proposals.records))failures.push('PROPOSED_RECORDS_NOT_ARRAY');
const seen=new Set();let subCount=0;const byYear={};
for(const q of (Array.isArray(proposals.records)?proposals.records:[])){
 byYear[q.year]=(byYear[q.year]||0)+1;
 if(q.year<2007||q.year>2012||!Number.isInteger(q.questionNumber))failures.push('YEAR_OR_QUESTION_NUMBER_INVALID:'+q.id);
 if(seen.has(q.id)||!q.id?.startsWith('legacy2-'+q.year+'-'))failures.push('DUPLICATE_OR_INVALID_ID:'+q.id);
 seen.add(q.id);
 if(q.sourceSha256!==manifest.newSources.find(s=>s.year===q.year)?.sha256)failures.push('QUESTION_SOURCE_HASH_MISMATCH:'+q.id);
 if(!q.questionText||!q.subject||!q.sourceFile||q.approved!==false||q.answerStatus!=='HOLD')failures.push('QUESTION_PROVENANCE_INVALID:'+q.id);
 if(q.sourcePage==null)holds.push('PAGE_UNVERIFIED:'+q.id);
 if(q.points==null)holds.push('POINTS_UNVERIFIED:'+q.id);
 for(const sub of q.subquestions||[]){
  subCount++;
  if(sub.id!==q.id+'-s'+sub.number)failures.push('SUBQUESTION_ID_INVALID:'+sub.id);
  if(sub.points==null)holds.push('SUBQUESTION_POINTS_UNVERIFIED:'+sub.id);
 }
}
if(JSON.stringify(Object.keys(byYear).sort())!==JSON.stringify(['2007','2008','2009','2010','2011','2012']))failures.push('SIX_YEAR_COVERAGE_INCOMPLETE');
if(!proposals.records?.length)holds.push('NO_EXTRACTED_QUESTIONS');
holds.push('NOT_COMPARED_WITH_ALL_LEGACY_QUESTION_IDS');
holds.push('NOT_INTEGRATED_WITH_UI_OR_STORAGE');
holds.push('BROWSER_PC_MOBILE_NOT_RUN');
const report={schema:'nomusa-auto-v1.1-readonly-gate',status:failures.length?'FAIL':holds.length?'HOLD':'PASS',majorQuestions:proposals.records?.length??0,subquestions:subCount,byYear,existingYearCount:original.years.length,targetYearCount:years.length,failures,holdCount:holds.length,holdExamples:holds.slice(0,15),contentApproval:'HOLD',preview:'NOT_DEPLOYED'};
console.log(JSON.stringify(report,null,2));if(failures.length)process.exitCode=1;

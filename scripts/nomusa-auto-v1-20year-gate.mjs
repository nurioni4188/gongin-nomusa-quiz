#!/usr/bin/env node
// NOMUSA-AUTO V1.0: read-only source gate; no files are modified.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
const root=path.resolve(process.argv[2]||'.');
const manifest=JSON.parse(fs.readFileSync(path.join(root,'review/NOMUSA_AUTO_V1_20YEAR_SOURCE_MANIFEST.json'),'utf8'));
const original=JSON.parse(fs.readFileSync(path.join(root,'second/ARCHIVE_MANIFEST.json'),'utf8'));
const failures=[],holds=[];
const years=Array.from({length:20},(_,i)=>2007+i);
const oldYears=original.years;
if(JSON.stringify(oldYears)!==JSON.stringify(years.filter(y=>y>=2013)))failures.push('BASELINE_YEAR_LIST_CHANGED');
if(original.baseline_count!==128 || original.total_study_units!==215)failures.push('EXISTING_COUNTS_CHANGED');
if(manifest.newSources.length!==6 || new Set(manifest.newSources.map(x=>x.year)).size!==6)failures.push('NEW_SOURCE_YEAR_COUNT');
for(const source of manifest.newSources){
 if(!years.includes(source.year)||source.year>=2013)failures.push('INVALID_NEW_YEAR:'+source.year);
 if(!/^[0-9a-f]{64}$/.test(source.sha256))failures.push('INVALID_SHA256:'+source.year);
 if(source.approved!==false)failures.push('UNAUTHORIZED_APPROVAL:'+source.year);
 const matching=path.join(root,'incoming',source.filename);
 if(fs.existsSync(matching)){
  const actual=crypto.createHash('sha256').update(fs.readFileSync(matching)).digest('hex');
  if(actual!==source.sha256)failures.push('SOURCE_SHA_MISMATCH:'+source.year);
 }else holds.push('SOURCE_NOT_IN_REPOSITORY:'+source.year);
}
const existing2013=original.source_files_sha256?.[manifest.boundary2013.existingPath];
if(!existing2013||existing2013!==manifest.boundary2013.uploadedSha256)failures.push('2013_SOURCE_CONFLICT');
if(manifest.duplicateEvidence.sha256!==manifest.newSources.find(x=>x.year===2009)?.sha256)failures.push('2009_DUPLICATE_CONFLICT');
if(manifest.idPolicy.existingIds!=='IMMUTABLE'||manifest.idPolicy.existingStorageKeys!=='IMMUTABLE')failures.push('ID_OR_STORAGE_POLICY_CHANGED');
if(manifest.deployment.main!=='FORBIDDEN'||manifest.deployment.production!=='FORBIDDEN'||manifest.deployment.preview!=='FORBIDDEN_UNTIL_USER_APPROVAL')failures.push('DEPLOYMENT_GATE_CHANGED');
for(const needed of ['second/index.html','second/essay-app.js','study-hub/state.js','scripts/v1107-source-gate.mjs'])
 if(!fs.existsSync(path.join(root,needed)))failures.push('MISSING_BASELINE:'+needed);
const proposedPath=path.join(root,'review/NOMUSA_AUTO_V1_PROPOSED_QUESTIONS.json');
let proposed=0;
if(fs.existsSync(proposedPath)){
 const records=JSON.parse(fs.readFileSync(proposedPath,'utf8'));
 const ids=new Set();
 if(!Array.isArray(records))failures.push('PROPOSALS_NOT_ARRAY');
 else for(const q of records){
  proposed++;
  if(!Number.isInteger(q.year)||q.year<2007||q.year>2012)failures.push('PROPOSED_YEAR_INVALID');
  if(!q.id||ids.has(q.id))failures.push('PROPOSED_DUPLICATE_ID:'+q.id);
  ids.add(q.id);
  if(!q.subject||!q.questionNumber||!q.sourcePage||!q.sourceSha256||!q.questionText)failures.push('PROPOSED_MISSING_PROVENANCE:'+q.id);
  if(q.approved!==false||q.answerStatus!=='HOLD')failures.push('PROPOSED_UNAPPROVED_MISMATCH:'+q.id);
 }
}
if(!proposed)holds.push('NO_EXTRACTED_QUESTION_RECORDS');
const result={schema:'nomusa-auto-v1-readonly-gate',status:failures.length?'FAIL':holds.length?'HOLD':'PASS_STATIC_ONLY',baselineYears:oldYears.length,targetYears:years.length,newSourceYears:manifest.newSources.map(x=>x.year),proposedQuestions:proposed,failures,holds,legalAnswerApproval:'HOLD',browserE2E:'NOT_RUN',previewDeployment:'NOT_REQUESTED'};
console.log(JSON.stringify(result,null,2));
if(failures.length)process.exitCode=1;

#!/usr/bin/env node
/** V33 — inspect actual existing 1차 banks and 3400 answer candidate IDs;
 * never generate artificial questions, change answers or authorize scoring.
 */
import {readFileSync,mkdirSync,writeFileSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
import {runInNewContext} from 'node:vm';
import {resolve} from 'node:path';
const root=resolve(process.argv[2]||'.');
const scope={window:{}};
function load(p){
  runInNewContext(readFileSync(resolve(root,p),'utf8'),scope,{timeout:9000,filename:p});
}
for(const f of ['data.js','study-hub/first-2008-a.js','study-hub/first-2009-a.js',
 'study-hub/first-2010-a.js','study-hub/first-2011-2019-a-pack.js',
 'study-hub/legacy-first-answer-review.js','study-hub/legacy-first-v2-staged.js',
 'study-hub/legacy-first-v4-2014-2021-review.js','study-hub/legacy-first-v5-correction.js',
 'study-hub/legacy-first-v61-sources.js','study-hub/first-v33-missing-year-coverage.js'])load(f);
const w=scope.window;
const batch=JSON.parse(gunzipSync(Buffer.from(w.NOMUSA_FIRST_BATCH_PACK,'base64')).toString('utf8'));
const all=[...w.QDATA,...w.NOMUSA_FIRST_2008,...w.NOMUSA_FIRST_2009,...w.NOMUSA_FIRST_2010,...batch];
const keys=all.map(q=>q.k);
const yearCount=Object.fromEntries([...new Set(all.map(q=>q.y))].sort((a,b)=>a-b).map(y=>[y,all.filter(q=>q.y===y).length]));
const expectedHistory={2008:125,2009:125,2010:125,2011:149,2012:149,2014:150,2015:150,2017:144,2019:142};
for(const [y,n]of Object.entries(expectedHistory))if(yearCount[y]!==n)throw Error('HOLD_LOADED_QUESTION_COUNT_'+y+'_'+yearCount[y]);
const missing=[2013,2016,2018,2020,2021];
for(const y of missing)if(yearCount[y])throw Error('HOLD_FALSELY_LOADED_MISSING_YEAR_'+y);
if(w.QDATA.length!==1020||all.length!==2279||new Set(keys).size!==2279)
  throw Error('HOLD_RC35_OR_IMPORT_ID_COLLISION');
const old=w.NOMUSA_FIRST_LEGACY_V5;
if(!old||old.records?.length!==3400||new Set(old.records.map(x=>x.id)).size!==3400)
  throw Error('HOLD_3400_ANSWER_CANDIDATE_OR_DUPLICATE');
const details={};
for(const y of missing){
  const rec=old.records.filter(r=>r.year===y);
  const a=rec.filter(r=>r.type==='A'),b=rec.filter(r=>r.type==='B');
  if(rec.length!==300||a.length!==150||b.length!==150)throw Error('HOLD_MISSING_YEAR_CANDIDATE_'+y);
  const linked=Object.entries(w.NOMUSA_FIRST_V61_SOURCES.records).filter(([k,v])=>k.startsWith('legacy1-'+y+'-')).length;
  if(linked!==(y>=2020?300:0))throw Error('HOLD_ORIGINAL_PDF_LINK_'+y+'_'+linked);
  details[y]={questionBank:0,answerCandidateA:150,answerCandidateB:150,qnetPdfSourceLinks:linked,
     renderedQuestionStemVerified:0,scoringApproved:0};
}
const cc=w.NOMUSA_FIRST_V33_COVERAGE;
if(!cc||cc.missingYears.map(x=>x.year).join()!==missing.join()||
 cc.partialUnrenderedQuestionsA!==41||cc.fullMissingUnrenderedQuestionsA!==750||
 cc.registeredLegacyQuestions!==1259||cc.originalRC35Questions!==1020||cc.scoringPromoted!==0)
 throw Error('HOLD_V33_STATIC_COVERAGE_NOT_LEDGER_MATCHED');
const totalMissing=missing.reduce((n,y)=>n+details[y].answerCandidateA+details[y].answerCandidateB,0);
if(totalMissing!==1500)throw Error('HOLD_1500_CANDIDATE');
const result={
 schema:'NOMUSA_FIRST_V33_EXISTING_BAG_SOURCE_AUDIT/1',
 status:'PASS_EXISTING_1500_SOURCE_ONLY_CANDIDATES_AND_2279_RENDERED_QUESTIONS',
 originalRC35:w.QDATA.length,legacyImported:all.length-w.QDATA.length,
 renderedTotal:all.length,yearCount,missingYearCandidates:details,
 missingYearCount:5,missingYearCandidateTotal:totalMissing,
 historicalPartialUnrenderedA:41,historicalFullMissingUnrenderedA:750,
 indexedSourceRecords:Object.keys(w.NOMUSA_FIRST_V61_SOURCES.records).length,
 candidateAnswers:old.records.length,duplicateQuestionKeys:0,
 independentLegacyScoringApproved:0,
 questionTextSynthesized:0,productionOrMainTouched:false
};
const folder=resolve(root,'review-artifacts/NOMUSA_FIRST_V33');mkdirSync(folder,{recursive:true});
writeFileSync(resolve(folder,'NOMUSA_FIRST_V33_5_GAP_YEARS_3400_LEDGER.json'),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify(result));

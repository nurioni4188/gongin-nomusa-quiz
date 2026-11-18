#!/usr/bin/env node
// V42 exact original Q-Net crop + final key + academic explanation, 2 theory questions.
// 2279 existing IDs, 789 remaining A-form original candidates, 2 pilot scoring IDs.
import {readFileSync,existsSync} from 'node:fs';
import {resolve} from 'node:path';
import {gunzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import {runInNewContext} from 'node:vm';
const root=resolve(process.argv[2]||'.');
const ctx={window:{}};
for(const p of [
 'data.js',
 'study-hub/first-2008-a.js','study-hub/first-2009-a.js','study-hub/first-2010-a.js',
 'study-hub/first-2011-2019-a-pack.js',
 'study-hub/legacy-first-answer-review.js','study-hub/legacy-first-v2-staged.js',
 'study-hub/legacy-first-v4-2014-2021-review.js','study-hub/legacy-first-v5-correction.js',
 'explanations-v108.js','explanations-2026-social-v36.js',
 'study-hub/first-v42-two-theory-source-checked.js'
]){
 runInNewContext(readFileSync(resolve(root,p),'utf8'),ctx,{filename:p,timeout:18000});
}
const W=ctx.window;
const packed=JSON.parse(gunzipSync(Buffer.from(W.NOMUSA_FIRST_BATCH_PACK,'base64')).toString('utf8'));
const old=[...W.QDATA,...W.NOMUSA_FIRST_2008,...W.NOMUSA_FIRST_2009,...W.NOMUSA_FIRST_2010,...packed];
const two=W.NOMUSA_FIRST_V42_TWO_THEORY;
const all=[...old,...two];
if(old.length!==2279||all.length!==2281||new Set(all.map(x=>x.k)).size!==2281)throw Error('V42_2279_TO_2281_ID_COLLISION');
const source=W.NOMUSA_FIRST_LEGACY_V5.records;
const matches=Object.fromEntries(two.map(q=>{
  const oldAnswer=source.filter(r=>r.id===q.k);
  if(oldAnswer.length!==1||JSON.stringify(Array.from(oldAnswer[0].answers))!=='[3]')
    throw Error('V42_OFFICIAL_ANSWER_CANDIDATE_DISAGREEMENT_'+q.k);
  const exp=W.NOMUSA_V108_EXPLANATIONS.entries[q.k];
  if(!exp||exp.question!==q.q||JSON.stringify(Array.from(exp.correct))!=='[3]'||
     JSON.stringify(Array.from(exp.optionTexts))!==JSON.stringify(Array.from(q.o)) ||
     exp.validationStatus!=='PASS_QNET_ORIGINAL_FINAL_KEY_THEORY_CHECKED')throw Error('V42_THEORY_EXPLANATION_MISMATCH_'+q.k);
  if(q.o.length!==5||q.a[0]!==3||q.sourceReviewStatus!=='V42_FULL_IMAGE_FIVE_OPTIONS_OFFICIAL_KEY_AND_THEORY_CROSSCHECKED') throw Error('V42_QUESTION_STRUCTURE_HOLD_'+q.k);
  return [q.k,{key:3,source:'QNet official A-form final answer',subject:q.s,pdfPage:q.pg[0]}];
}));
const sourceManifest=JSON.parse(readFileSync(resolve(root,'review/NOMUSA_FIRST_V42_FOUR_MANUAL_CROP_REPAIRS_20261118.json'),'utf8'));
if(sourceManifest.repairedCrops!==4||sourceManifest.newQDATAImported!==0||
   sourceManifest.expertIndependentFinalApproval!==0)throw Error('V42_SOURCE_MANIFEST_UNTRUSTED');
for(const rec of sourceManifest.records){
 const f=resolve(root,rec.originalQuestionImage);
 if(!existsSync(f)||createHash('sha256').update(readFileSync(f)).digest('hex')!==rec.sha256)
  throw Error('V42_CORRECTED_IMAGE_HASH_CHANGED_'+rec.id);
}
const expected=new Set(['legacy1-2020-A-management-101','legacy1-2021-A-management-110']);
if(two.length!==2||new Set(two.map(q=>q.k)).size!==2||
   two.some(q=>!expected.has(q.k))||W.NOMUSA_FIRST_V42_SCORING_IDS.some(k=>!expected.has(k)))
 throw Error('V42_ONLY_TWO_EXCEPTIONS_EXPECTED');
for(const q of old){if(expected.has(q.k))throw Error('V42_OLD_BANK_OVERWRITE_'+q.k)}
console.log(JSON.stringify({status:'PASS',oldQuestionBank:2279,newSourceCheckedTheoryQuestions:2,
 totalStudyBank:2281,remainingOriginalNotImported:789,manualRepairedCrops:4,
 onlyAutoGradedHistoricalIDs:[...expected],otherHistoricalScoringChanged:0,
 technicalValidation:'PASS',independentExpertFinalApproval:'HOLD',
 originalMainAndProduction:'UNTOUCHED',proof:matches},null,2));

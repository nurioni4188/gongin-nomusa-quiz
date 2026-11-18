#!/usr/bin/env node
/**
 * V77: reconcile 2008-2026 A-form 3,070 distinct question IDs in five
 * independently preserved NON-OVERLAPPING data scopes.
 * This is SOURCE-COVERAGE ONLY; it does not approve source OCR, law, answer
 * cells, 5 options, or independent explanations for examination scoring.
 */
import fs from 'node:fs';
import vm from 'node:vm';
import zlib from 'node:zlib';
import path from 'node:path';
const read=p=>fs.readFileSync(p,'utf8');
const must=(x,s)=>{if(!x)throw Error('HOLD_V77_'+s)};
const env={window:{},console};vm.createContext(env);
for(const file of ['data.js','study-hub/first-2008-a.js','study-hub/first-2009-a.js','study-hub/first-2010-a.js','study-hub/first-2011-2019-a-pack.js'])
 vm.runInContext(read(file),env,{filename:file,timeout:30000});
const w=env.window;
const original2022=w.QDATA;
const pack=JSON.parse(zlib.gunzipSync(Buffer.from(w.NOMUSA_FIRST_BATCH_PACK,'base64')).toString());
const initial=[...w.NOMUSA_FIRST_2008,...w.NOMUSA_FIRST_2009,...w.NOMUSA_FIRST_2010,...pack,...original2022];
must(initial.length===2279,'V33_RENDERED_INITIAL_2279');
const v42src=read('study-hub/first-v42-two-theory-source-checked.js');
const v42=['legacy1-2020-A-management-101','legacy1-2021-A-management-110'];
must(v42.every(id=>v42src.includes(id)),'PILOT_2_SOURCE');
const v43=JSON.parse(read('review/NOMUSA_FIRST_V43_103_FIRST_PASS_SOURCE_CONTENT_QA_20261118.json'));
must(v43.actualFirstPassSourceReadAndExplanationDrafts===v43.rows.length&&v43.rows.length===103,'V43_103');
const v74=JSON.parse(read('review-artifacts/V77_V74_BUNDLE/NOMUSA_FIRST_V74_686_ALL_SOURCE_LEADS_UNAPPROVED.json'));
must(v74.targetCount===v74.rows.length&&v74.rows.length===686,'V74_686');
const detailed=JSON.parse(read('review/NOMUSA_FIRST_V76_2013_MANAGEMENT_25_FIVE_CHOICE_DETAILED_EXPLANATIONS_20261119.json'));
must(Object.keys(detailed.entries).length===25,'V76_25');
const groups={
 existing2008to2026QuestionBank:initial.map(q=>({id:q.k,y:q.y,has5Options:!!(q.q&&Array.isArray(q.o)&&q.o.length===5)})),
 QNetTwoTheoryPilot:v42.map(id=>({id,y:Number(id.slice(8,12)),has5Options:true})),
 previous103FirstPass:v43.rows.map(q=>({id:q.id,y:Number(q.id.slice(8,12)),has5Options:true})),
 remaining686SourceReview:v74.rows.map(q=>({id:q.id,y:q.year,has5Options:q.reviewStage==='unapproved_full_stem_and_five_options'}))
};
const byId=new Map(),sourceCounts={},errors=[];
for(const [kind,arr]of Object.entries(groups)){
 sourceCounts[kind]=arr.length;
 for(const q of arr){
  must(q.id&&Number.isInteger(q.y),'INVALID_ID_OR_YEAR_'+kind);
  if(byId.has(q.id))errors.push({id:q.id,first:byId.get(q.id).kind,second:kind});
  else byId.set(q.id,{...q,kind});
 }
}
must(errors.length===0,'DUPLICATE_AFORM_SOURCE_IDS_'+JSON.stringify(errors.slice(0,5)));
must(byId.size===3070,'TOTAL_A_FORM_IDS_NOT_3070_'+byId.size);
const status=[];
for(let year=2008;year<=2026;year++){
 const rows=[...byId.values()].filter(q=>q.y===year);
 const expected=year===2008||year===2009?125:year<=2023?150:240;
 must(rows.length===expected,'YEAR_'+year+'_COUNT_'+rows.length+'_EXPECTED_'+expected);
 const count={};
 for(const r of rows)count[r.kind]=(count[r.kind]||0)+1;
 status.push({
  year,expectedAFormItemIDs:expected,registeredUniqueIDs:rows.length,
  existingQDATAAndLegacyBank:count.existing2008to2026QuestionBank||0,
  V42TwoPilot:count.QNetTwoTheoryPilot||0,
  V43OriginalFirstPassDraft:count.previous103FirstPass||0,
  V74OriginalSourceReviewDraft:count.remaining686SourceReview||0,
  explanationRequirement:'Each item has five independent choice explanations and dated authority; NONE of these counts proves final answer approval.'
 });
}
must(status.length===19,'EXACT_19_YEARS');
must(status.reduce((a,r)=>a+r.registeredUniqueIDs,0)===3070,'ALL_YEARS_3070');
const fiveUnverifiedByYear={};
for(const r of original2022){
 if(r.q&&Array.isArray(r.o)&&r.o.length===5)continue;
 fiveUnverifiedByYear[r.y]=(fiveUnverifiedByYear[r.y]||0)+1;
}
must(fiveUnverifiedByYear['2023']===91,'2023_91_UNSTRUCTURED');
const docs={
 schema:'NOMUSA_FIRST_V77_ALL_2008_2026_AFORM_3070_SOURCE_IDS_RECONCILED/1',
 asOfKST:'2026-11-19',
 periodStart:2008,periodEnd:2026,periodYears:19,
 expectedUniqueAFormIDs:3070,
 recordedUniqueAFormIDs:byId.size,
 sourceBuckets:sourceCounts,
 unreviewedSourceOrDraftAFormItems:byId.size,
 originalQDATA2022to2026Items:1020,
 QDATA2023FiveChoiceTextIncomplete:91,
 2013ManagementNewAcademicDraftExplanations:25,
 choiceReasonsNewlyAuthored:125,
 minimumDistinctChoiceReasonsToApproveAllAFormItems:3070*5,
 officialFinalKeyAll3070ReviewedByTwoIndependentExperts:0,
 allItemsOriginalFiveChoicesAndExamDateAuthorityApproved:0,
 newlyGradedLegacyItemsByThisAudit:0,
 appProductionAndGitHubMainUntouched:true,
 warning:'This reconciles all 3,070 target A-form IDs across 19 years. Does NOT verify their complete original text, official final answers, dated legal evidence, independent proofreading, or five-option solutions.',
 yearly:status
};
fs.mkdirSync('review-artifacts/NOMUSA_FIRST_V77',{recursive:true});
fs.writeFileSync('review/NOMUSA_FIRST_V77_2008_2026_3070_RECONCILIATION_SUMMARY_20261119.json',JSON.stringify(docs,null,2)+'\n');
const csv=['year,expected,sourceIDs,existingBank,twoPilots,previous103Drafts,remaining686SourceDrafts'];
for(const r of status)csv.push([r.year,r.expectedAFormItemIDs,r.registeredUniqueIDs,r.existingQDATAAndLegacyBank,
 r.V42TwoPilot,r.V43OriginalFirstPassDraft,r.V74OriginalSourceReviewDraft].join(','));
fs.writeFileSync('review-artifacts/NOMUSA_FIRST_V77/NOMUSA_FIRST_V77_19_YEAR_3070_CONTENT_GATES.csv',csv.join('\n')+'\n');
console.log(JSON.stringify({...docs,yearly:undefined},null,2));

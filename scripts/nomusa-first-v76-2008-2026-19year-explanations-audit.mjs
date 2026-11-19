#!/usr/bin/env node
/**
 * V76 inspect actual 19-year first-stage study material and existing explanations.
 * Verifies 25 substantively authored 2013 management explanations against V74
 * historically recorded answer candidate and complete original 5 option drafts.
 *
 * A source question, correct-answer candidate, explanation draft and an approved
 * exam-grade choice-by-choice solution are FOUR different states.
 * NEVER change QDATA, auto-scoring approval, original IDs, main, Preview or Production.
 */
import fs from 'node:fs';
import vm from 'node:vm';
import zlib from 'node:zlib';
import crypto from 'node:crypto';
import path from 'node:path';
const ROOT=process.cwd();
const read=(p)=>fs.readFileSync(path.join(ROOT,p),'utf8');
const json=(p)=>JSON.parse(read(p));
const assert=(ok,msg)=>{if(!ok)throw new Error('HOLD_V76_'+msg);};
const env={window:{},console};
vm.createContext(env);
for(const f of [
 'data.js','explanations-v108.js','explanations-2026-social-v36.js',
 'study-hub/first-2008-a.js','study-hub/first-2009-a.js',
 'study-hub/first-2010-a.js','study-hub/first-2011-2019-a-pack.js']){
 vm.runInContext(read(f),env,{filename:f,timeout:30000});
}
const win=env.window;
assert(Array.isArray(win.QDATA) && win.QDATA.length===1020,'ORIGINAL_2022_2026_QDATA_1020');
assert(win.QMETA.count===1020,'ORIGINAL_QMETA_1020');
const qdata=win.QDATA;
const qidx=new Map(qdata.map(q=>[q.k,q]));
assert(qidx.size===1020,'QDATA_DUPLICATE_IDS');
const explanations=win.NOMUSA_V108_EXPLANATIONS?.entries||{};
const exkeys=Object.keys(explanations);
const originalExpCount=exkeys.length;
const matched=exkeys.filter(k=>qidx.has(k));
const unmatched=exkeys.filter(k=>!qidx.has(k));
const byYear={};
for(let y=2008;y<=2026;y++){
 const qt=qdata.filter(x=>x.y===y);
 const ex=matched.filter(k=>qidx.get(k).y===y);
 byYear[y]={originalQDATAItems:qt.length,existingExplanationDrafts:ex.length,
  questionTextsWithFiveOptions:qt.filter(x=>Array.isArray(x.o)&&x.o.length===5&&x.q).length,
  existingOptionReasonListsFive:ex.filter(k=>Array.isArray(explanations[k]?.options)&&explanations[k].options.length===5).length};
}
const directFiles={
 2008:win.NOMUSA_FIRST_2008,2009:win.NOMUSA_FIRST_2009,2010:win.NOMUSA_FIRST_2010
};
for(const [year,arr] of Object.entries(directFiles)){
 assert(Array.isArray(arr),'LEGACY_DIRECT_'+year);
 const raw=arr.map(q=>q.k).filter(Boolean);
 assert(new Set(raw).size===raw.length,'LEGACY_DIRECT_DUP_'+year);
 byYear[year].legacyDirectQuestionItems=arr.length;
 byYear[year].legacyDirectFiveChoices=arr.filter(q=>Array.isArray(q.o)&&q.o.length===5&&q.q).length;
}
let pack={kind:'unknown',count:0,byYear:{},sample:null,error:null};
try{
 const packed=win.NOMUSA_FIRST_BATCH_PACK;
 assert(typeof packed==='string' && packed.length>100,'FIRST_PACK_BASE64');
 const raw=zlib.gunzipSync(Buffer.from(packed,'base64')).toString('utf8');
 const payload=JSON.parse(raw);
 const records=Array.isArray(payload)?payload:
  Array.isArray(payload.questions)?payload.questions:
  Array.isArray(payload.records)?payload.records:
  Array.isArray(payload.items)?payload.items:[];
 pack.kind=Array.isArray(payload)?'array':Object.keys(payload).slice(0,10).join(',');
 pack.count=records.length;
 pack.sample=records[0]?Object.fromEntries(Object.entries(records[0]).slice(0,12)):null;
 const hist={};
 for(const r of records){const y=Number(r.y||r.year);
  if(Number.isFinite(y)&&y>=2008&&y<=2026)hist[y]=(hist[y]||0)+1;}
 pack.byYear=hist;
 for(const [y,c]of Object.entries(hist)){
  byYear[y].legacyPackedQuestions=c;
 }
}catch(e){pack.error=String(e.message).slice(0,280)}
const si2026=exkeys.filter(k=>k.startsWith('2026-사회보험법-'));
const detailed=json('review/NOMUSA_FIRST_V76_2013_MANAGEMENT_25_FIVE_CHOICE_DETAILED_EXPLANATIONS_20261119.json');
const entries=detailed.entries;
const input=json('review-artifacts/V76_V74_BUNDLE/NOMUSA_FIRST_V74_686_ALL_SOURCE_LEADS_UNAPPROVED.json');
assert(input.targetCount===686&&Array.isArray(input.rows)&&input.rows.length===686,'V74_686_SOURCE');
const byID=new Map(input.rows.map(x=>[x.id,x]));
assert(byID.size===686,'V74_UNIQUE');
assert(Object.keys(entries).length===25,'MANAGEMENT_25_EXPLANATIONS');
assert(detailed.optionReasons===125&&detailed.officialFinalQNetAnswerCellApprovals===0,'DETAIL_125_ZERO_APPROVAL');
let sourceMatched=0;
const flagCounts={};
for(let n=101;n<=125;n++){
 const id='legacy1-2013-A-management-'+String(n).padStart(3,'0');
 const e=entries[id],q=byID.get(id);
 assert(e&&q,'ID_NOT_SOURCE_MATCHED_'+id);
 assert(q.year===2013&&q.subject==='경영학개론'&&q.questionNumber===n,'YEAR_SUBJECT_NUMBER_'+id);
 assert(e.questionNumber===n,'EXPLANATION_NUMBER_'+id);
 assert(Array.isArray(q.fiveOptionTextCandidates)&&q.fiveOptionTextCandidates.length===5,'OFFLINE_FIVE_ORIGINAL_CHOICES_'+id);
 assert(q.legacyAnswerCandidateNotApproved.length===1&&
   q.legacyAnswerCandidateNotApproved[0]===e.correctCandidateUnapproved[0],
   'LEGACY_ANSWER_CANDIDATE_NOT_MATCHED_'+id);
 assert(e.optionReasons.length===5&&e.optionReasons.every((o,i)=>o.choice===i+1&&
  o.explanation.length>=15),'FIVE_NONTRIVIAL_WRONG_CHOICE_EXPLANATIONS_'+id);
 assert(e.optionReasons.filter(o=>o.isCandidateCorrect).length===1&&
   e.optionReasons[e.correctCandidateUnapproved[0]-1].isCandidateCorrect,
   'ONE_ONLY_CANDIDATE_CORRECT_'+id);
 assert(e.coreExplanation.length>45&&e.mnemonic.length>=9&&e.theoryBasis.length>=12,
   'REASON_LENGTH_'+id);
 assert(e.officialKeyCellVerified===false&&e.independentExpertApproved===false&&
   e.gradingAllowed===false&&e.sourceOriginalEntireQuestionAndFiveChoicesVerified===false,
   'PREMATURE_OFFICIAL_APPROVAL_'+id);
 sourceMatched++;
}
assert(sourceMatched===25,'SOME_EXPLANATIONS_NOT_LINKED');
const former=byYear[2013].legacyPackedQuestions||0;
const summary={
 schema:'NOMUSA_FIRST_V76_19_YEAR_CONTENT_SCOPE_AND_2013_MANAGEMENT_25_AUDIT/1',
 asOfKST:'2026-11-19',
 requestedHistoricalPeriod:'2008-2026',
 periodYearCount:19,
 yearsCovered:Array.from({length:19},(_,i)=>i+2008),
 sourceWorkStatus:'AUDIT_ONLY_NOT_A_COMPLETE_EXAM_ANSWER_BANK',
 original2022to2026QDATAItems:qdata.length,
 first2022to2026FiveOptionOriginalQuestionRecords:qdata.filter(x=>Array.isArray(x.o)&&x.o.length===5&&x.q).length,
 existingOriginalAndV36ExplanationDrafts:originalExpCount,
 existingExplanationDraftsMatchingQDATA:matched.length,
 existingExplanationDraftsNotMatchingQDATA:unmatched.length,
 socialInsurance2026ExistingDrafts:si2026.length,
 existingFiveReasonListsFor2022to2026:matched.filter(k=>Array.isArray(explanations[k]?.options)&&explanations[k].options.length===5).length,
 prior686ReviewRows:686,
 substantive2013ManagementDetailedNewDrafts:25,
 substantive2013ManagementIndividualChoiceReasons:125,
 substantive2013ManagementCorrectCandidateLinksValidated:sourceMatched,
 newQDATAImports:0,newScoringApprovals:0,
 independentOfficialFinalKeyCellsApprovedForThese25:0,
 independentReviewerApprovedForThese25:0,
 legacyPackedAudit:pack,
 fullHistoricalYearSourceInventory:byYear,
 status:'PASS_19_YEAR_SCOPE_AUDIT_PLUS_25_FIVE_CHOICE_EXPLANATIONS_ZERO_APPROVED'
};
const dest=path.join(ROOT,'review','NOMUSA_FIRST_V76_19_YEAR_AUDIT_SUMMARY_20261119.json');
fs.writeFileSync(dest,JSON.stringify(summary,null,2)+'\n');
const csv=['year,originalQDATA2022to2026,originalQDATA5Options,existingExplanationDrafts,existingExplanationFiveReasons,legacyDirectQuestionItems,legacyDirectFiveChoices,legacyPackedQuestions'];
for(let y=2008;y<=2026;y++){
 const x=byYear[y];csv.push([y,x.originalQDATAItems,x.questionTextsWithFiveOptions,x.existingExplanationDrafts,x.existingOptionReasonListsFive,
  x.legacyDirectQuestionItems||0,x.legacyDirectFiveChoices||0,x.legacyPackedQuestions||0].join(','));
}
fs.mkdirSync(path.join(ROOT,'review-artifacts','NOMUSA_FIRST_V76'),{recursive:true});
fs.writeFileSync(path.join(ROOT,'review-artifacts','NOMUSA_FIRST_V76','NOMUSA_FIRST_V76_19_YEAR_COVERAGE.csv'),csv.join('\n')+'\n');
fs.writeFileSync(path.join(ROOT,'review-artifacts','NOMUSA_FIRST_V76','NOMUSA_FIRST_V76_2013_MANAGEMENT_25_STUDY_NOTES.json'),
 JSON.stringify({schema:detailed.schema,sourceTotal:25,candidateCorrectOnlyNotOfficial:true,items:Object.values(entries)},null,2)+'\n');
console.log(JSON.stringify({...summary,fullHistoricalYearSourceInventory:undefined},null,2));

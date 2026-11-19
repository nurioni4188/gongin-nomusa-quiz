#!/usr/bin/env node
// V34 source-to-question queue: 791 real A-form candidate IDs absent from QDATA.
// Source/answer metadata are evidence only; no text invented, no grading enabled.
import {readFileSync,mkdirSync,writeFileSync} from 'node:fs';
import {resolve} from 'node:path';
import {gunzipSync} from 'node:zlib';
import {runInNewContext} from 'node:vm';

const root=resolve(process.argv[2]||'.'),ctx={window:{}};
for(const path of [
  'data.js',
  'study-hub/first-2008-a.js','study-hub/first-2009-a.js','study-hub/first-2010-a.js',
  'study-hub/first-2011-2019-a-pack.js',
  'study-hub/legacy-first-answer-review.js','study-hub/legacy-first-v2-staged.js',
  'study-hub/legacy-first-v4-2014-2021-review.js','study-hub/legacy-first-v5-correction.js',
  'study-hub/legacy-first-v61-sources.js','study-hub/first-v32-proof-status.js',
  'study-hub/first-v33-missing-year-coverage.js'
]) runInNewContext(readFileSync(resolve(root,path),'utf8'),ctx,{timeout:15000,filename:path});
const w=ctx.window;
const packed=JSON.parse(gunzipSync(Buffer.from(w.NOMUSA_FIRST_BATCH_PACK,'base64')).toString('utf8'));
const actual=[...w.QDATA,...w.NOMUSA_FIRST_2008,...w.NOMUSA_FIRST_2009,...w.NOMUSA_FIRST_2010,...packed];
const actualKeys=new Set(actual.map(q=>q.k));
const allCandidate=w.NOMUSA_FIRST_LEGACY_V5.records.filter(r=>r.type==='A');
const target=allCandidate.filter(r=>!actualKeys.has(r.id)).sort((a,b)=>a.year-b.year||a.subject.localeCompare(b.subject,'ko')||a.questionNo-b.questionNo);
const yearExpected={2010:25,2011:1,2012:1,2013:150,2016:150,2017:6,2018:150,2019:8,2020:150,2021:150};
const byYear=Object.fromEntries(Object.keys(yearExpected).map(y=>[y,target.filter(r=>r.year===+y).length]));
if(target.length!==791||new Set(target.map(x=>x.id)).size!==791||actualKeys.size!==2279||
   actual.length!==2279||Object.keys(yearExpected).some(y=>byYear[y]!==yearExpected[y]))
  throw new Error('HOLD_791_ACTUAL_BANK_OR_CANDIDATE_MISMATCH '+JSON.stringify({count:target.length,byYear}));
const qnet=w.NOMUSA_FIRST_V61_SOURCES;
const officialNotice={
  2016:'https://www.q-net.or.kr/cst003.do?artlSeq=5183001&boardId=Q004&gId=05&gSite=L&id=cst00302&menuType=cst00309',
  2017:'https://www.q-net.or.kr/cst003.do?artlSeq=5201158&boardId=Q004&gId=05&gSite=L&id=cst00302&menuType=cst00309',
  2018:'https://www.q-net.or.kr/cst003.do?artlSeq=5203291&boardId=Q004&gId=05&gSite=L&id=cst00302&menuType=cst00309',
  2019:'https://www.q-net.or.kr/cst003.do?artlSeq=5205539&boardId=Q004&gId=05&gSite=L&id=cst00302&menuType=cst00309'
};
const output=target.map(r=>{
  const m=qnet.records[r.id],doc=m&&qnet.documents[m.source],
        status=m?.status||'ORIGINAL_QUESTION_PER_ITEM_NOT_LINKED';
  const page=m?.pdfPage||null;
  let originalURL=null,authority='NONE';
  if(doc) {originalURL=doc.download+(page?'#page='+page:'');authority='QNET_DOCUMENT_REGISTERED';}
  else if(officialNotice[r.year]){
    originalURL=officialNotice[r.year];
    authority=r.year===2016&&r.subject!=='경제학원론'?
      'GENERAL_OFFICIAL_ECONOMICS_ONLY_NOT_ITEM_LINK':
      'OFFICIAL_NOTICE_ONLY_NOT_ITEM_LINK';
  }
  return Object.freeze({
    id:r.id,year:r.year,form:'A',subject:r.subject,number:r.questionNo,
    candidateAnswers:r.answers,
    originalURL,sourceAuthority:authority,sourceStatus:status,
    sourceDocumentSHA256:doc?.sha256||null,
    candidatePdfPage:page,
    originalQuestionTextMatched:false,optionSequenceVisuallyMatched:false,
    formulaOrGraphicVerified:false,scoringApproved:false,
    readyForQDATAImport:false,
    origin:'existing V5 A-form answer candidate + V61 Q-Net source only'
  });
});
const linked=output.filter(r=>r.sourceAuthority==='QNET_DOCUMENT_REGISTERED');
if(linked.length!==300||output.some(r=>r.readyForQDATAImport||r.scoringApproved))
  throw Error('HOLD_QNET_300_LINKED_OR_UNAPPROVED');
const summary={
 schema:'NOMUSA_FIRST_V34_791_ORIGINAL_SOURCE_TARGETS/1',
 totalTargets:output.length,sourceLinkedQNetRecords:linked.length,
 missingAllFiveYears:750,partialYearTargets:41,
 perYear:byYear,sourceStatus:output.reduce((a,r)=>(a[r.sourceStatus]=(a[r.sourceStatus]||0)+1,a),{}),
 officialSourceURLs:output.filter(x=>x.originalURL).length,
 contentOneToOneVerified:0,allowedQDATAImport:0,scoringApproved:0,
 existingQDATA:2279,sourceRecordBaseline3400:w.NOMUSA_FIRST_LEGACY_V5.records.length,
 expertApproval:'HOLD',mainAndProduction:'NOT_TOUCHED'
};
const out=resolve(root,'review-artifacts/NOMUSA_FIRST_V34');mkdirSync(out,{recursive:true});
writeFileSync(resolve(out,'NOMUSA_FIRST_V34_791_SOURCE_TARGETS.json'),JSON.stringify({summary,rows:output},null,2)+'\n');
const csv=[['id','year','subject','number','originalURL','sourceAuthority','sourceStatus','candidatePdfPage','sha256','questionContentReady'].join(',')];
for(const row of output)csv.push([
  row.id,row.year,row.subject,row.number,row.originalURL||'',row.sourceAuthority,row.sourceStatus,
  row.candidatePdfPage||'',row.sourceDocumentSHA256||'',row.readyForQDATAImport
].map(x=>'"'+String(x).replaceAll('"','""')+'"').join(','));
writeFileSync(resolve(out,'NOMUSA_FIRST_V34_791_SOURCE_TARGETS.csv'),csv.join('\n')+'\n');
console.log(JSON.stringify(summary));

#!/usr/bin/env node
import fs from 'node:fs';
const m=JSON.parse(fs.readFileSync('data/rc29-2-source-manifest.json','utf8'));
const failures=[];
const ok=(test,n)=>{if(!test)failures.push(n)};
ok(m.target===1020,'target');
ok(m.candidateRows===565&&m.uniqueKeys===565,'candidate total/key uniqueness');
ok(m.textLayerCompleteMatches===443&&m.textLayerMismatchRows===122,'matches');
ok(m.rc17AReferenceRows===1020,'reference');
ok(m.scoringApproved===0&&m.pendingVisualReview===565&&m.releaseStatus==='HOLD','no premature scoring');
ok(m.missingFromCandidatePool===m.target-m.candidateRows,'missing slots');
ok(m.byYear.reduce((s,x)=>s+x.candidates,0)===m.candidateRows,'years candidates');
ok(m.byYear.reduce((s,x)=>s+x.textMatch,0)===m.textLayerCompleteMatches,'years matches');
ok(m.byYear.reduce((s,x)=>s+x.needsReview,0)===m.textLayerMismatchRows,'years mismatches');
ok(m.bySubject.reduce((s,x)=>s+x[2],0)===m.candidateRows,'subject candidates');
ok(m.bySubject.reduce((s,x)=>s+x[3],0)===m.textLayerCompleteMatches,'subject matches');
ok(new Set(m.bySubject.map(x=>x[0]+'|'+x[1])).size===m.bySubject.length,'duplicate subject key');
for(const p of m.pdfSources)ok(/^[a-f0-9]{64}$/.test(p.sha)&&p.pages>0,'source metadata '+p.name);
const result={schema:'rc29-2-ci-manifest-v1',status:failures.length?'ERROR':'MANIFEST_PASS_RELEASE_HOLD',
 pdfContentReopenedInCI:false,sourceManifestRecords:m.candidateRows,exactTextLayerMatches:m.textLayerCompleteMatches,
 scoringApproved:0,releaseGate:'HOLD',errors:failures};
fs.mkdirSync('rc29-evidence',{recursive:true});
fs.writeFileSync('rc29-evidence/rc29-2-ci-manifest.json',JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify(result));
if(failures.length)process.exitCode=2;

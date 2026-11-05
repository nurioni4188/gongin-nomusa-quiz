#!/usr/bin/env node
// RC29.8B static evidence integrity only; original scanned PDF unavailable in GitHub CI.
import fs from 'node:fs';
const m=JSON.parse(fs.readFileSync('data/rc29-8b-2023-highrisk.json','utf8'));
const errors=[];function check(x,k){if(!x)errors.push(k)}
check(m.year===2023&&m.total2023Slots===150,'scope');
check(m.priorFirstPassDrafts===47&&m.newFirstPassCorrections===6&&m.totalFirstPassDrafts===53,'firstpass counts');
check(m.priorLegacyOCRPending===103&&m.remainingLegacyOCR===97,'remaining 2023 OCR');
check(m.totalFirstPassDrafts+m.remainingLegacyOCR===150,'total pool 150');
check(m.priorHighRisk===43&&m.remainingHighRisk===37&&m.remainingNormalRisk===60,'high/normal risk counts');
check(m.remainingHighRisk+m.remainingNormalRisk===m.remainingLegacyOCR,'queue partition');
check(m.firstPassCorrections.length===6,'6 cases');
check(new Set(m.firstPassCorrections.map(q=>q.key)).size===6,'no duplicate keys');
check(m.firstPassCorrections.filter(q=>q.subject==='민법').length===1,'civil count');
check(m.firstPassCorrections.filter(q=>q.subject==='경영학개론').length===5,'management count');
check(m.firstPassCorrections.every(q=>q.defects.length>0&&q.paperPage>=1&&q.paperPage<=39),'defect classification and page');
check(m.firstPassCorrections.every(q=>/^[a-f0-9]{64}$/.test(q.pageRenderSha256)),'source image render digests');
check(m.firstPassCorrections.every(q=>q.status==='FIRST_PASS_CORRECTION_NEEDS_INDEPENDENT_REVIEW'&&!q.officiallyVerified&&!q.scoringApproved),'unverified source lock');
check(m.remainingOCRPageHintWithinPDFRange===97&&m.remainingOCRPageHintIndividuallyVerifiedOnPDF===0,'candidate page boundary is not source verification');
check(m.remainingOCRPageBatchCount===37,'page queue batching');
check(/^[a-f0-9]{64}$/.test(m.sourcePDFSha256),'source original hash format');
check(m.privateHTMLReviewRows===150&&m.browserViewportTestsPassed===4&&m.chromiumViewportTested.length===4&&!m.actualAndroidDeviceTested,'local Chromium only');
check(!m.ciReadsOriginalSourcePDF&&!m.publicRepositoryContainsOriginalSourcePDF&&!m.publicRepositoryContainsFullQuestionText,'no public exam copyright upload / source-CI overclaim');
check(m.independentSecondVisualReviewApproved===0&&m.finalAnswerToBookletApproved===0&&m.scoringApproved===0,'no grading approval');
check(m.releaseGate==='HOLD'&&!m.vercelDeploymentPerformed,'no deploy');
const out={schema:'rc29-8b-ci-integrity-v1',status:errors.length?'ERROR':'METADATA_PASS_RELEASE_HOLD',
 firstPassComparedSix:m.firstPassCorrections.length,firstPassDrafts:m.totalFirstPassDrafts,
 remainingHighRisk:m.remainingHighRisk,remainingOCR:m.remainingLegacyOCR,
 pageHintsWithinRange:97,pageHintsIndependentlyVerifiedInCI:0,officialScoringApproved:0,releaseGate:'HOLD',errors};
fs.mkdirSync('rc29-evidence',{recursive:true});
fs.writeFileSync('rc29-evidence/rc29-8b-ci-check.json',JSON.stringify(out,null,2)+'\n');
console.log(JSON.stringify(out,null,2));if(errors.length)process.exitCode=2;
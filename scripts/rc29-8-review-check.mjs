#!/usr/bin/env node
import fs from 'node:fs';
const d=JSON.parse(fs.readFileSync('data/rc29-8-ocr-review-progress.json','utf8'));
const failures=[];
const check=(x,label)=>{if(!x)failures.push(label)};
check(d.year===2023&&d.originalExpectedSlots===150,'scope');
check(d.priorDrafts===39&&d.previousOCRPending===111,'baseline');
check(d.newDraftsFromOCR===4&&d.totalDrafts===43&&d.ocrStillPending===107,'review increment');
check(d.totalDrafts+d.ocrStillPending===150&&d.originalBlankStillPending===0,'complete draft pool');
check(d.previousPriorityCount===50&&d.previousNormalCount===61,'triage baseline');
check(d.priorityCorrections===3&&d.normalCorrections===1,'corrected risk groups');
check(d.priorityStillPending===47&&d.normalStillPending===60,'risk queue integrity');
check(d.priorityStillPending+d.normalStillPending===107,'remaining risk sum');
check(d.firstPassManuallyCompared.length===4,'compared source sample count');
check(new Set(d.firstPassManuallyCompared.map(x=>x.questionKey)).size===4,'unique firstpass comparisons');
check(d.firstPassManuallyCompared.every(x=>x.paperPage===4||x.paperPage===5),'paper page references');
check(d.firstPassManuallyCompared.every(x=>x.fixedAsDraft===true&&!x.independentlyVerified&&!x.scoringApproved),'draft must never be approved');
check(d.firstPassManuallyCompared.find(x=>x.questionKey.endsWith('-010'))?.defects.includes('OCR_NEXT_QUESTION_MERGED'),'Q10 bleed test');
check(d.firstPassManuallyCompared.find(x=>x.questionKey.endsWith('-012'))?.defects.includes('RISK_HEURISTIC_FALSE_NEGATIVE'),'Q12 false negative test');
check(d.firstPassManuallyCompared.find(x=>x.questionKey.endsWith('-014'))?.defects.includes('OCR_2_YEARS_MISREAD_AS_3_YEARS'),'Q14 numerical OCR corruption');
check(/^[0-9a-f]{64}$/.test(d.sourceSha256),'source hash shape');
check(Object.values(d.browserQA).filter(x=>x===true).length===4&&d.browserQA.realAndroidDeviceVerified===false,'4 simulated viewports only');
check(d.independentSecondReviewerSignoffs===0&&d.officialFinalAnswerPerQuestionApproved===0&&d.scoringApproved===0,'NO GRADING');
check(d.status==='HOLD'&&!d.vercelDeploymentPerformed,'no deployment');
check(d.publicRepoSourcePDFUploaded===false&&d.publicRepoFullQuestionsUploaded===false,'no source copyright publication');
check(d.githubCILimit.startsWith('Metadata checks only'),'must not misrepresent CI source validation');
const output={schema:'rc29-8-ci-metadata-v1',status:failures.length?'ERROR':'METADATA_PASS_RELEASE_HOLD',
 manuallyComparedFirstPassDrafts:d.newDraftsFromOCR,allFirstPassDrafts:d.totalDrafts,remainingOCR:d.ocrStillPending,
 priorityPending:d.priorityStillPending,independentlyVerifiedForScoring:0,
 sourcePDFReopenedInGitHubCI:false,realAndroidDeviceTested:false,release:'HOLD',errors:failures};
fs.mkdirSync('rc29-evidence',{recursive:true});
fs.writeFileSync('rc29-evidence/rc29-8-review-metadata-check.json',JSON.stringify(output,null,2)+'\n');
console.log(JSON.stringify(output,null,2));
if(failures.length)process.exitCode=2;

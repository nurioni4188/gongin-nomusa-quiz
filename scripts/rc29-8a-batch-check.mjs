#!/usr/bin/env node
import fs from "node:fs";
const p="data/rc29-8a-batch-triage.json";const d=JSON.parse(fs.readFileSync(p,"utf8"));
const errors=[];const check=(cond,label)=>{if(!cond)errors.push(label)};
check(d.year===2023&&d.total2023QuestionSlots===150,"year/slots");
check(d.priorFirstPassDrafts===43&&d.newFirstPassDrafts===4&&d.totalFirstPassDrafts===47,"draft count");
check(d.previousOcrUnverified===107&&d.remainingOcrUnverified===103,"remaining OCR");
check(d.totalFirstPassDrafts+d.remainingOcrUnverified===d.total2023QuestionSlots,"pool partition");
check(d.previousHighRisk===47&&d.remainingHighRisk===43&&d.previousNormalRisk===d.remainingNormalRisk&&d.remainingNormalRisk===60,"priority queue");
check(d.remainingHighRisk+d.remainingNormalRisk===103,"priority+normal");
check(d.newManuallyComparedQuestionNumbers.join(",")==="15,16,17,18","new visual comparison keys");
check(d.newManualSourcePages.join(",")==="6,6,6,7","original source page clues");
check(new Set(d.newManuallyComparedQuestionNumbers).size===4&&d.newVisualFindings.length===4,"dedup new keys");
check(d.autoTriageAppliedToRemaining===103&&d.autoTriageMethod==="TEXT_ONLY_HEURISTIC_NO_NEW_OCR_NO_SCAN_PIXEL_CHECK","heuristic methodology");
check(d.autoTriageFlagCounts.insufficientReliableCircledOptionMarkers===103,"marker signal limitations");
check(d.autoTriageFlagCounts.likelyCorruptionTokens===50&&d.autoTriageFlagCounts.duplicatedAdjacentLine===17&&d.autoTriageFlagCounts.veryShortOcrText===11,"OCR heuristic distribution");
check(d.triageCaveat.includes("no discriminatory value"),"marker signal caveat must remain");
check(/^[0-9a-f]{64}$/.test(d.sourceUploadedPaperSha256),"paper sha form");
check(d.browserEmulatedWidths.join(",")==="1365,768,390,360"&&d.browserEmulationPass===4&&!d.realAndroidTested,"browser test scope");
check(d.independentQuestionVerificationApproved===0&&d.finalAnswerBookletPairingApproved===0&&d.scoringApproved===0,"no grading approval");
check(!d.fullOriginalQuestionsPubliclyPublished&&!d.sourcePdfBytesAvailableInGitHubCI,"CI must not overclaim original source checks");
check(d.release==="HOLD"&&!d.vercelDeployPerformed,"release HOLD");
const report={schema:"rc29-8a-ci-manifest-v1",status:errors.length?"ERROR":"METADATA_PASS_RELEASE_HOLD",
newFirstPassDrafts:4,cumulativeFirstPassDrafts:47,remainingOCRVisualReview:103,highRiskVisualReviewQueue:43,
originalPdfReopenedInCI:false,officialQuestionVerified:0,liveScoringApproved:0,release:"HOLD",errors};
fs.mkdirSync("rc29-evidence",{recursive:true});fs.writeFileSync("rc29-evidence/rc29-8a-batch-metadata.json",JSON.stringify(report,null,2)+"\n");
console.log(JSON.stringify(report,null,2));if(errors.length)process.exitCode=2;

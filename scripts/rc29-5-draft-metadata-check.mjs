#!/usr/bin/env node
import fs from "node:fs";
const m=JSON.parse(fs.readFileSync("data/rc29-5-visual-draft-progress.json","utf8"));
const errors=[];const t=(b,s)=>{if(!b)errors.push(s)};
t(m.year===2023&&m.targetQuestionSlots===150,"year/slots");
t(m.priorOcrNonemptyCandidateSlots+m.priorOcrBlankSlots===150,"prior OCR total");
t(m.firstPassVisualTranscriptionDrafts===9,"draft total");
t(m.newlyFilledPreviouslyBlankDrafts===8&&m.previouslyNonblankButCorruptedDraftReplaced===1,"draft source split");
t(m.remainingBlankWithoutDraft===m.priorOcrBlankSlots-m.newlyFilledPreviouslyBlankDrafts,"remaining empty");
t(m.priorOcrStillAwaitingOriginalComparison===m.priorOcrNonemptyCandidateSlots-m.previouslyNonblankButCorruptedDraftReplaced,"remaining old OCR");
t(m.firstPassDraftLocationMap.length===9,"locations count");
t(new Set(m.firstPassDraftLocationMap.map(x=>x.questionNum)).size===9,"unique number");
t(m.firstPassDraftLocationMap.every(x=>x.sourcePage>=1&&x.sourcePage<=3),"source range");
t(m.firstPassDraftLocationMap.filter(x=>x.priorOcrBlank).length===8,"blank count");
t(m.priorPageHintDefect.questionKey==="2023-노동법(1)-002"&&
m.priorPageHintDefect.priorCandidateSourcePage===2&&m.priorPageHintDefect.manuallyLocatedSourcePage===1,"Q2 page correction");
t(/^[a-f0-9]{64}$/.test(m.sourcePdfSha256),"source file hash shape");
t(m.verifiedAfterIndependentVisualReview===0&&m.approvedForScoring===0&&m.officialAnswerForScoringApproved===0,"premature scoring approval");
t(m.browserCheck.status==="PASS"&&!m.browserCheck.realAndroidDeviceTested,"browser status");
t(m.originalQuestionTextPublishedToPublicGitHub===false&&m.release==="HOLD"&&m.vercelDeploymentPerformed===false,"release hold");
const result={schema:"rc29-5-draft-manifest-ci-v1",status:errors.length?"ERROR":"METADATA_PASS_RELEASE_HOLD",
 stagedFirstPassDrafts:m.firstPassVisualTranscriptionDrafts,remainingUntranscribed:m.remainingBlankWithoutDraft,
 originalPDFReadInGithubCI:false,reviewHTMLReadInGithubCI:false,independentlyReviewed:0,
 verifiedForScoring:0,release:"HOLD",errors};
fs.mkdirSync("rc29-evidence",{recursive:true});
fs.writeFileSync("rc29-evidence/rc29-5-visual-draft-metadata-check.json",JSON.stringify(result,null,2)+"\n");
console.log(JSON.stringify(result,null,2));
if(errors.length)process.exitCode=2;
#!/usr/bin/env node
import fs from "node:fs";
const x=JSON.parse(fs.readFileSync("data/rc30-source-choice-answer-evidence.json","utf8"));
const prior=JSON.parse(fs.readFileSync("data/rc29-integrated-1020.json","utf8"));
const v=JSON.parse(fs.readFileSync("vercel.json","utf8"));
const e=[];const ok=(b,msg)=>{if(!b)e.push(msg)};
ok(x.schema==="rc30-source-choice-answer-verified-file-integrity-v1"&&x.scope===1020,"RC30 source coverage");
ok(prior.slots.length===1020&&new Set(prior.slots.map(r=>r.key)).size===1020,"source slot count");
ok(x.textualStemFiveOptionsSameSourcePage+x.additionalTextSourceReview+x.year2023OCRAndDraftIndependentReviewPending+x.sourcePDFPresentButAutomaticChoiceParsingFailed===1020,"four exclusive source status groups");
ok(x.textualStemFiveOptionsSameSourcePage===715&&x.additionalTextSourceReview===123&&x.year2023OCRAndDraftIndependentReviewPending===150&&x.sourcePDFPresentButAutomaticChoiceParsingFailed===32,"private run totals");
ok(x.autoStructuredFiveOptionCandidates===897&&x.questionOriginalSourcePDFsLocated===13&&x.finalAnswerOriginalFilesLocated===5,"question source structure");
ok(x.firstPassOrPriorHWPImageAnswerMapRecords===1020&&x.localAnswerOriginalFileShaMatches===1020,"answer provenance");
ok(x.sourceAnswerImageFirstPassAgreesWithLegacyReference===565&&x.sourceAnswerImageFirstPassDiffersFromLegacyReference===0&&x.legacyAnswerUnavailableForNewQuestions===305&&x.previousYear2023HWPImageReferenceRows===150,"answer candidate crosswalk");
ok(x.sourceAnswerImageFirstPassAgreesWithLegacyReference+x.legacyAnswerUnavailableForNewQuestions+x.previousYear2023HWPImageReferenceRows===1020,"answer row partition");
ok(x.multipleAnswerCases===4&&!x.answerFileOriginsComparedDirectlyAgainstQNetDownload,"exception and provenance safeguards");
ok(x.independentSourceStemAndFiveOptionsApproved===0&&x.independentAnswerTranscriptionApproved===0&&x.scoringApproved===0,"no scoring certification");
ok(x.releaseDecision==="HOLD"&&!x.vercelDeployed&&v.git?.deploymentEnabled===false,"Vercel deployment locked");
ok(!x.originalExamTextUploadedPublicly&&!x.userInterfaceModified,"privacy and UI freeze");
const result={schema:"rc30-source-answer-public-ci-v1",technicalIntegrity:e.length?"FAIL":"PASS",fileSHAClaimsIndependentlyCheckedInPublicCI:false,
 gradingUnlockPermitted:false,releaseDecision:"HOLD",errors:e};
fs.mkdirSync("rc29-evidence",{recursive:true});
fs.writeFileSync("rc29-evidence/rc30-source-answer-metadata.json",JSON.stringify(result,null,2)+"\n");
console.log(JSON.stringify(result,null,2));if(e.length)process.exitCode=2;

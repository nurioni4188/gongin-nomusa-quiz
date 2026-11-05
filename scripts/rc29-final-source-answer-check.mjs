#!/usr/bin/env node
import fs from "node:fs";
const d=JSON.parse(fs.readFileSync("data/rc29-final-source-answer-batch.json","utf8"));
const prev=JSON.parse(fs.readFileSync("data/rc29-current-1020-source-state.json","utf8"));
const v=JSON.parse(fs.readFileSync("vercel.json","utf8"));
const failures=[];const ok=(b,s)=>{if(!b)failures.push(s)};
ok(d.schema==="rc29-final-1020-source-answer-batch-metadata-v1","schema");
ok(d.sourceScope.totalUniqueQuestionSlots===1020&&prev.slots.length===1020&&d.sourceScope.sourceMissingSlots===0,"unique scope/source presence");
ok(d.sourceScope.sourcePdfExistingCandidate===565&&d.sourceScope.sourcePdfNewExtracted===305&&d.sourceScope.year2023FirstpassDraft===59&&d.sourceScope.year2023OCRRaw===91,"source partitions");
ok(565+305+59+91===1020,"source sum");
ok(d.sourceTextRecheck.year2022to2026Legacy565SourceShaMatches===565,"PDF digests");
ok(d.sourceTextRecheck.samePDFPageStemAndFiveOptionsTextNormalized===454&&d.sourceTextRecheck.legacyNeedsAdditionalSourceReview===111,"PDF normalized text analysis");
ok(454+111===565&&d.sourceTextRecheck.normalizationTextOnlyNotVisualSignoff===true,"non-visual matching caveat");
ok(d.mathFormula.privateUseGlyphRisk===47&&d.mathFormula.sourceQuestionCrops===49&&d.mathFormula.formulaFullyRetranscribedAndReviewed===0,"formula unresolved");
ok(d.year2023.unstructuredOCR===91&&d.year2023.sourcePageImages===35&&d.year2023.ocrStructurallyCorrectedToFiveChoices===0,"OCR unverified");
ok(d.answerKeyCrosscheck.recordCount===1020&&d.answerKeyCrosscheck.distinctAnswerKeyMap===1020&&d.answerKeyCrosscheck.sourceSHA256MatchedYears===5,"official answer table provenance");
ok(d.answerKeyCrosscheck.sourceImagesCrosscheckedSingleChoiceDigits===1015&&d.answerKeyCrosscheck.sourceImageExceptionsVisuallyChecked===5&&d.answerKeyCrosscheck.sourceImageNumericMismatchUnresolved===0,"answer image transcription matching");
ok(d.answerKeyCrosscheck.manualExceptions.length===5&&Object.values(d.answerKeyCrosscheck.sourceSHA256).every(h=>/^[a-f0-9]{64}$/.test(h)),"A-type multianswers and source hashes");
ok([47,91,111,59,258,454].reduce((a,b)=>a+b,0)===1020,"exclusive content review buckets");
ok(d.browserSimulation.passed===4&&d.browserSimulation.widths.join(",")==="1365,768,390,360"&&d.browserSimulation.realAndroidDeviceTested===false,"browser simulation only");
ok(d.officialFullQuestionTextVisualSecondReviewerApproved===0&&d.officiallyScorable===0,"no officially scorable questions");
ok(d.releaseDecision==="HOLD"&&d.previewApproved===false&&d.productionApproved===false&&!d.vercelDeploymentPerformed&&v.git?.deploymentEnabled===false,"no release");
ok(!d.publicRepositoryContainsOriginalExamText&&!d.originalPDFBytesAvailableInGitHubCI,"no public copyrighted source/Ci overclaim");
const result={schema:"rc29-final-source-answer-ci-v1",metadataTechnicalStatus:failures.length?"FAIL":"PASS",
 answerImageRecordMapping:1020,answerImageNumericExceptionsResolvedLocally:5,
 exactNormalizedPDFTextOnly:454,legacyTextUnresolved:111,
 formulaTextUnresolved:47,OCRUnstructured:91,
 sourcePDFReopenedInPublicCI:false,officialExamQuestionContentApproved:0,scoringApproved:0,releaseDecision:"HOLD",errors:failures};
fs.mkdirSync("rc29-evidence",{recursive:true});
fs.writeFileSync("rc29-evidence/rc29-final-source-answer-crosscheck.json",JSON.stringify(result,null,2)+"\n");
console.log(JSON.stringify(result,null,2));
if(failures.length)process.exitCode=2;

#!/usr/bin/env node
// 2023 OCR draft metadata consistency only. This does not import/approve any answers.
import fs from "node:fs";
const m=JSON.parse(fs.readFileSync("data/rc29-3-2023-ocr-review.json","utf8"));
const errors=[];
const ok=(v,k)=>{if(!v)errors.push(k)};
ok(m.totalQuestionSlots===150&&m.existingOCRSlots===150,"subject/slot total");
ok(m.existingOCRTextPresent+m.existingOCRTextAbsent===150,"OCR count sum");
ok(m.existingOCRTextPresent===112&&m.existingOCRTextAbsent===38,"OCR count drift");
ok(m.existingOCRPageHints===112,"page hint count");
ok(m.subjectBreakdown.length===6&&new Set(m.subjectBreakdown.map(s=>s.subject)).size===6,"subjects");
ok(m.subjectBreakdown.every(s=>s.ocrPresent+s.ocrAbsent===25),"per subject 25 slots");
ok(m.subjectBreakdown.reduce((n,s)=>n+s.ocrPresent,0)===112,"OCR per subject present");
ok(m.subjectBreakdown.reduce((n,s)=>n+s.ocrAbsent,0)===38,"OCR per subject absent");
ok(m.subjectBreakdown.reduce((n,s)=>n+s.ocrPageHints,0)===112,"OCR page hint sum");
ok(m.pageCounts.management===39&&m.pageCounts.economics===41,"paper page count");
const pages=m.sharedPageImageDeduplication;
ok(pages.shared===34&&pages.managementUnique===5&&pages.economicsUnique===7&&pages.total===46,"page deduplication");
ok(Object.values(m.sourceSha256).every(s=>/^[0-9a-f]{64}$/.test(s)),"sha256 format");
ok(m.officialVerifiedQuestions===0&&m.liveScoringAllowed===0&&m.manualVisualReviewCompleted===0,"no premature signoff");
ok(m.noVercelDeploy===true&&m.status.endsWith("RELEASE_HOLD"),"no deploy hold");
const status=errors.length?"ERROR":"METADATA_PASS_RELEASE_HOLD";
const out={schema:"rc29-3-ocr-review-ci-v1",status,sourceFilesReadInCI:false,
 note:"Historical OCR candidates are unverified; this CI checks recorded counts and SHA metadata format only.",
 expected:150,legacyOCRTextPresent:112,legacyOCRTextMissing:38,
 approvedForScoring:0,realAndroidTested:false,release:"HOLD",errors};
fs.mkdirSync("rc29-evidence",{recursive:true});
fs.writeFileSync("rc29-evidence/rc29-3-ocr-review-check.json",JSON.stringify(out,null,2)+"\n");
console.log(JSON.stringify(out));
if(errors.length) process.exitCode=2;
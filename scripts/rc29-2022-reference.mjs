#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
const source=JSON.parse(fs.readFileSync("data/rc29-2022-A-reference.json","utf8"));
const outputDir=path.join(process.cwd(),"rc29-evidence");
fs.mkdirSync(outputDir,{recursive:true});
const rows=[];
const errors=[];
const subjects=new Set();
for(const subject of source.subjects) {
 if(subjects.has(subject.name))errors.push("duplicate subject "+subject.name);
 subjects.add(subject.name);
 const parts=subject.values.trim().split(/\s+/);
 if(parts.length!==25)errors.push(subject.name+": expected 25 reference answers, got "+parts.length);
 for(let i=0;i<parts.length;i++){
  const answers=parts[i].split("/").map(Number);
  if(!answers.length||answers.some(x=>!Number.isInteger(x)||x<1||x>5)||new Set(answers).size!==answers.length){
   errors.push(subject.name+" Q"+(subject.start+i)+" invalid answer labels");
  }
  rows.push({year:2022,booklet:"A",subject:subject.name,num:subject.start+i,
             officialAnswerLabelsReference:answers,
             verificationStatus:"REFERENCE_ONLY_DO_NOT_SCORE"});
 }
}
if(rows.length!==150)errors.push("Expected exactly 150 rows");
if(new Set(rows.map(x=>x.subject+"|"+x.num)).size!==150)errors.push("Duplicate subject+question key");
const find=(s,n)=>rows.find(x=>x.subject===s&&x.num===n)?.officialAnswerLabelsReference;
if(JSON.stringify(find("민법",51))!=="[4,5]")errors.push("Q51 multi-answer mismatch");
if(JSON.stringify(find("민법",72))!=="[1,2,3,4,5]")errors.push("Q72 all-answer mismatch");
if(source.audit.verifiedForLiveScoring!==0)errors.push("Reference data may NOT be promoted to verified automatically");
const localPdf=process.argv.find(x=>x.startsWith("--pdf="))?.slice(6);
let verifiedSourceBytes=false;
if(localPdf){
 const digest=crypto.createHash("sha256").update(fs.readFileSync(localPdf)).digest("hex");
 if(digest!==source.source.sha256)errors.push("PDF SHA256 mismatch");
 else verifiedSourceBytes=true;
}
const result={schema:"rc29-2022-reference-check-v1",status:errors.length?"ERROR":"REFERENCE_READY_HOLD",
 sourcePdfSha256:source.source.sha256,
 exactSourcePdfBytesVerifiedLocally:verifiedSourceBytes,
 referenceRows:rows.length,
 singleAnswerRows:rows.filter(x=>x.officialAnswerLabelsReference.length===1).length,
 multipleAnswerRows:rows.filter(x=>x.officialAnswerLabelsReference.length>1).length,
 liveScoringApproved:0,manualPaperReviewPending:125,
 originalQuestionCandidateCount:source.audit.extractedPaperCandidates,
 exactStemAndOptionsTextMatches:source.audit.completeStemAndOptionsTextMatches,
 errors};
fs.writeFileSync(path.join(outputDir,"2022-answer-reference-audit.json"),JSON.stringify(result,null,2)+"\n");
console.log(JSON.stringify(result,null,2));
if(errors.length)process.exitCode=2;

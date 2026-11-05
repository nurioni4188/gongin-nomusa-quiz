#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
const root = process.cwd();
const evidenceDir = path.join(root, "rc28-evidence");
fs.mkdirSync(evidenceDir, {recursive:true});
const outPath = path.join(evidenceDir, "question-audit.json");
const result = {
  schema:"rc28-question-audit-v1",
  dataScope:"2022-2026 1차 기출, 목표 1020문항",
  targetCount:1020, status:"HOLD", totals:{}, byYear:{}, failures:{}, samples:{}
};
function error(code, message, key){
  if(!result.samples[code]) result.samples[code]=[];
  result.failures[code]=(result.failures[code]||0)+1;
  if(result.samples[code].length<5) result.samples[code].push({key:key||"",message});
}
try {
  const html=fs.readFileSync(path.join(root,"index.html"),"utf8");
  const match=html.match(/const\s+questions\s*=\s*(\[[\s\S]*?\]);\s*let\s+currentQuestions/);
  if(!match) throw new Error("questions JSON array not found");
  const questions=JSON.parse(match[1]);
  if(!Array.isArray(questions)) throw new Error("questions is not an array");
  const relevant=questions.filter(q=>/^(2022|2023|2024|2025|2026)$/.test(String(q.year)));
  result.totals.all=questions.length;
  result.totals.targetYears=relevant.length;
  result.totals.outsideTargetYears=questions.length-relevant.length;
  result.totals.answeredNumeric=0;
  result.totals.unverifiedNull=0;
  result.totals.answerStrings=0;
  result.totals.uniqueQuestionKeys=0;
  const seen=new Map();
  for(const q of relevant){
    const y=String(q.year);
    result.byYear[y]=(result.byYear[y]||0)+1;
    const key=[y,q.subject,q.num].join("|");
    seen.set(key,(seen.get(key)||0)+1);
    if(typeof q.question!=="string"||!q.question.trim()) error("MISSING_QUESTION","Empty or invalid stem",key);
    if(!Array.isArray(q.options)||q.options.length!==5||
       q.options.some(x=>typeof x!=="string"||!x.trim())) {
      error("INVALID_OPTIONS","Exactly five non-empty options required",key);
    }
    if(q.answer===null||q.answer===undefined){
      result.totals.unverifiedNull++;
      error("ANSWER_UNVERIFIED","Official answer not verified",key);
    } else if(!Number.isInteger(q.answer)||q.answer<0||q.answer>4){
      if(typeof q.answer==="string") result.totals.answerStrings++;
      error("INVALID_ANSWER_FORMAT","Answer must be zero-based integer 0..4, not a string",key);
    } else {
      result.totals.answeredNumeric++;
    }
    if(typeof q.explanation!=="string"||!q.explanation.trim()||
       /정답은 확인 후 수정 필요|자동 생성|placeholder/i.test(q.explanation)){
      error("EXPLANATION_NEEDS_REVIEW","Explanation is missing or provisional",key);
    }
    if(!q.sourceFile||!Number.isInteger(q.sourcePage)||q.sourcePage<1){
      error("MISSING_SOURCE_PROVENANCE","Official sourceFile and positive integer sourcePage required",key);
    }
  }
  result.totals.uniqueQuestionKeys=seen.size;
  for(const [key,n] of seen) {
    if(n>1)error("DUPLICATE_QUESTION_KEY","Question key appears "+n+" times",key);
  }
  if(relevant.length!==result.targetCount) {
    error("INCOMPLETE_COVERAGE","Target 1020, found "+relevant.length);
  }
  if(html.includes("i === q.answer")&&html.includes("parseInt(selected.dataset.idx) === q.answer")){
    const anyBad=relevant.some(q=>q.answer!==null&&typeof q.answer!=="number");
    if(anyBad)error("SCORING_TYPE_MISMATCH","UI requires numeric 0..4 answers but source has strings");
  }
  result.status=Object.keys(result.failures).length?"HOLD":"PASS";
} catch(e){
  error("AUDIT_EXECUTION_ERROR",String(e&&e.message||e));
  result.status="HOLD";
}
fs.writeFileSync(outPath,JSON.stringify(result,null,2)+"\n");
console.log(JSON.stringify({status:result.status,totals:result.totals,byYear:result.byYear,failures:result.failures},null,2));
if(process.argv.includes("--strict")&&result.status!=="PASS")process.exitCode=2;

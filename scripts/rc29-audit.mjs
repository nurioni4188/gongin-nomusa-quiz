#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
const folder=path.join(process.cwd(),"rc29-evidence");
fs.mkdirSync(folder,{recursive:true});
const config=JSON.parse(fs.readFileSync("data/rc29-exam-scope.json","utf8"));
const html=fs.readFileSync("index.html","utf8");
const match=html.match(/const\s+questions\s*=\s*(\[[\s\S]*?\]);\s*let\s+currentQuestions/);
if(!match)throw new Error("Question bank not readable");
const bank=JSON.parse(match[1]);
const target=new Set(config.years.map(x=>String(x.year)));
const selected=bank.filter(q=>target.has(String(q.year)));
const map=new Map();
const issues={duplicateKeys:[],invalidNumbers:[],invalidOptions:[],orphanSubjects:[],legacyStringAnswers:0,rawNullAnswers:0,provenanceMissing:0};
const subjects=new Set(config.subjects.map(x=>x.name));
function approved(q){
 if(q.verificationStatus!=="VERIFIED_OFFICIAL_FINAL")return null;
 const p=q.provenance;
 if(!p||!p.questionFile||!Number.isInteger(p.questionPage)||p.questionPage<1||
 !p.answerFile||typeof p.officialAnswerURL!=="string"||
 !p.officialAnswerURL.startsWith("https://www.q-net.or.kr/")||
 p.booklet!=="A"||!p.checkedBy||!p.checkedAt||
 !Array.isArray(q.options)||q.options.length!==5)return null;
 const a=Array.isArray(q.acceptedAnswers)?q.acceptedAnswers:
 (Number.isInteger(q.answer)?[q.answer]:null);
 return a&&a.length>0&&a.length<=5&&a.every(i=>Number.isInteger(i)&&i>=0&&i<=4)&&
 new Set(a).size===a.length?a:null;
}
for(const q of selected){
 const id=[q.year,q.subject,q.num].join("|");
 if(!map.has(id))map.set(id,[]);
 map.get(id).push(q);
 if(!subjects.has(q.subject))issues.orphanSubjects.push(id);
 if(!Array.isArray(q.options)||q.options.length!==5||
 q.options.some(x=>typeof x!=="string"||!x.trim()))issues.invalidOptions.push(id);
 if(q.answer===null||q.answer===undefined)issues.rawNullAnswers++;
 else if(typeof q.answer==="string")issues.legacyStringAnswers++;
 if(!q.provenance?.questionFile||!q.provenance?.answerFile||
 !Number.isInteger(q.provenance?.questionPage))issues.provenanceMissing++;
}
for(const [id,rows] of map)if(rows.length>1)issues.duplicateKeys.push({id,count:rows.length});
const result={schema:"rc29-question-audit-v1",targetCount:config.targetCount,
 allBankRows:bank.length,targetYearRows:selected.length,verifiedUnique:0,
 expectedSlots:0,missingSlots:0,ambiguousSlots:0,issues,byYearSubject:[],status:"HOLD"};
const mapping=[];
for(const year of config.years){
 for(const subj of config.subjects){
  const start=(subj.session===1?0:(year.n===25?50:0))+subj.slot*year.n+1;
  const end=start+year.n-1;
  const rows=selected.filter(q=>Number(q.year)===year.year&&q.subject===subj.name);
  const coverage={year:year.year,subject:subj.name,expected:year.n,
   currentRows:rows.length,matchedUnique:0,missing:0,duplicateExtra:0,verified:0,outOfRange:0};
  for(const q of rows){
   if(!Number.isInteger(Number(q.num))||Number(q.num)<start||Number(q.num)>end){
     issues.invalidNumbers.push({year:year.year,subject:subj.name,num:q.num});
     coverage.outOfRange++;
   }
  }
  for(let num=start;num<=end;num++){
   const id=[year.year,subj.name,num].join("|");
   const candidates=map.get(id)||[];
   const ans=candidates.length===1?approved(candidates[0]):null;
   if(candidates.length===0){coverage.missing++;result.missingSlots++}
   if(candidates.length>1){coverage.duplicateExtra+=candidates.length-1;result.ambiguousSlots++}
   if(candidates.length===1)coverage.matchedUnique++;
   if(ans){coverage.verified++;result.verifiedUnique++}
   mapping.push({id,year:year.year,subject:subj.name,session:subj.session,num,
     candidates:candidates.length,finalAnswerFile:year.finalAnswer,
     officialAnswer:ans,sourcePage:candidates.length===1?(candidates[0].provenance?.questionPage||null):null,
     status:ans?"VERIFIED_OFFICIAL_FINAL":candidates.length===0?"MISSING_QUESTION":
       candidates.length>1?"DUPLICATE_HOLD":"PAPER_AND_FINAL_ANSWER_NOT_VERIFIED"});
  }
  result.byYearSubject.push(coverage);
 }
}
result.expectedSlots=mapping.length;
result.status=result.expectedSlots===config.targetCount&&
 result.verifiedUnique===config.targetCount&&!issues.duplicateKeys.length&&
 !issues.invalidNumbers.length&&!issues.invalidOptions.length?"PASS":"HOLD";
fs.writeFileSync(path.join(folder,"question-audit.json"),JSON.stringify(result,null,2)+"\n");
fs.writeFileSync(path.join(folder,"official-answer-mapping.json"),JSON.stringify({
 schema:"rc29-official-answer-mapping-v1",target:config.targetCount,
 verified:result.verifiedUnique,records:mapping,
 notice:"Unverified answer values are null by design; no guessed official answers."
},null,2)+"\n");
fs.writeFileSync(path.join(folder,"missing-official-sources.json"),JSON.stringify({
 status:"HOLD",sourceQuestionPage:config.officialQuestionPage,
 sourceAnswerPage:config.officialAnswerPage,
 years:config.years.map(y=>({year:y.year,expectedSubjects:6,finalAnswer:y.finalAnswer,
  paperStatus:"PAPER_A_TYPE_NOT_COMPLETE_IN_REPOSITORY",
  keyStatus:"OFFICIAL_FINAL_KEYS_NOT_TRANSCRIBED_AND_DOUBLE_CHECKED"}))
},null,2)+"\n");
const csv=[["year","subject","expected","existing","unique","missing","verified","bad_numbering","duplicates"],
...result.byYearSubject.map(x=>[x.year,x.subject,x.expected,x.currentRows,x.matchedUnique,x.missing,x.verified,x.outOfRange,x.duplicateExtra])]
.map(a=>a.join(",")).join("\n")+"\n";
fs.writeFileSync(path.join(folder,"year-subject-coverage.csv"),csv);
console.log(JSON.stringify({status:result.status,target:result.targetCount,registered:result.targetYearRows,
 verified:result.verifiedUnique,missingSlots:result.missingSlots,duplicates:issues.duplicateKeys.length,
 badNumbering:issues.invalidNumbers.length,byYear:result.byYearSubject.reduce((o,x)=>{
 const t=o[x.year]||(o[x.year]={expected:0,registered:0,missing:0});
 t.expected+=x.expected;t.registered+=x.currentRows;t.missing+=x.missing;return o;
},{})},null,2));

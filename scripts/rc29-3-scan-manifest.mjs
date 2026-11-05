#!/usr/bin/env node
import fs from 'node:fs';
const m=JSON.parse(fs.readFileSync('data/rc29-3-2023-scan-manifest.json','utf8'));
const errors=[];
const test=(cond,what)=>{if(!cond)errors.push(what)};
test(m.year===2023&&m.booklets.length===2,'year/booklets');
test(m.booklets.reduce((n,x)=>n+x.pages,0)===80,'page count');
test(m.visualReviewPages===80,'visual review queue');
test(m.booklets.every(x=>/^[a-f0-9]{64}$/.test(x.sha256)&&x.pages>0&&x.zeroTextPages<=x.pages),'pdf source SHA format');
test(/^[a-f0-9]{64}$/.test(m.officialAnswer.sha256),'HWP SHA format');
test(m.ocrUsed===false&&m.scoringApproved===0&&m.officialAnswerVerified===0,'unverified must stay locked');
test(m.release==='HOLD','release lock');
const out={schema:'rc29-3-ci-manifest-v1',status:errors.length?'ERROR':'MANIFEST_PASS_RELEASE_HOLD',
 sourcePdfBytesReopenedInCI:false,sourceAnswerHwpParsedInCI:false,
 visualReviewPages:m.visualReviewPages,officialAnswersVerified:0,scoringApproved:0,release:'HOLD',errors};
fs.mkdirSync('rc29-evidence',{recursive:true});
fs.writeFileSync('rc29-evidence/rc29-3-2023-manifest-check.json',JSON.stringify(out,null,2)+'\n');
console.log(JSON.stringify(out));
if(errors.length)process.exitCode=2;

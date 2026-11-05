#!/usr/bin/env node
// Safe local inspector for manually exported RC29.3/4/5 review notes.
// Usage: node scripts/rc29-5-import-review-notes.mjs /path/to/rc29_3_2023_review_notes.json
// Never approves scoring, never merges original questions, never sends network requests.
import fs from "node:fs";
const file=process.argv[2];
if(!file){console.log("NO_INPUT: Provide the local exported review JSON path. No answers or approvals changed.");process.exit(0)}
const d=JSON.parse(fs.readFileSync(file,"utf8"));
const issues=[],statusCounts={};
const allowed=new Set(["PENDING","NEEDS_CORRECTION","SOURCE_PAGE_LOCATED","VISUAL_REVIEWED_PENDING_FINAL_KEY","ILLEGIBLE"]);
if(d.schema!=="rc29-3-manual-review-export-v1")issues.push("unexpected review export schema");
if(d.status!=="HUMAN_REVIEW_ONLY_NOT_OFFICIAL_SCORING")issues.push("review file must not certify scoring");
const entries=Object.entries(d.reviews||{});
if(entries.length>150)issues.push("more than 150 keys");
for(const [key,row] of entries){
 if(!/^2023-(노동법\(1\)|노동법\(2\)|민법|사회보험법|경영학개론|경제학원론)-\d{3}$/.test(key))issues.push("unexpected key "+key);
 if(!row||typeof row!=="object"||Array.isArray(row)){issues.push("invalid row "+key);continue}
 const status=row.status||"PENDING";
 if(!allowed.has(status))issues.push("invalid review status "+key);
 statusCounts[status]=(statusCounts[status]||0)+1;
 if(row.scoringApproved===true||row.officiallyVerified===true)issues.push("unapproved claim "+key);
}
const out={schema:"rc29-5-manual-review-export-check-v1",inputRows:entries.length,reviewStatusCounts:statusCounts,
 status:issues.length?"HOLD_INVALID_EXPORT":"METADATA_OK_REVIEW_NOT_OFFICIALLY_SIGNED",
 officiallyVerified:0,scoringApproved:0,errors:issues};
console.log(JSON.stringify(out,null,2));
if(issues.length)process.exitCode=2;
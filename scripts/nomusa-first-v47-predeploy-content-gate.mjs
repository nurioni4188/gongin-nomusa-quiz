#!/usr/bin/env node
/**
 * V47: zero-approval, fail-closed PREDEPLOY CONTENT AUDIT.
 * Verify that 103 V43 drafts, 515 option reasons, 25 historical-law candidate
 * references and the V44 approval manifest have not drifted apart.
 * This is a machine-level cross-check, NOT an independent human proofread.
 * No network access, app writes, release commits, deployment or approval.
 */
import {readFileSync, writeFileSync, existsSync, mkdirSync} from "node:fs";
import {resolve} from "node:path";
import {createHash} from "node:crypto";
const ROOT=resolve(process.argv[2] || ".");
const f=(p)=>resolve(ROOT,p);
const j=(p)=>JSON.parse(readFileSync(f(p),"utf8"));
const sha=(p)=>createHash("sha256").update(readFileSync(f(p))).digest("hex");
const bad=[];
const check=(v,msg)=>{if(!v) bad.push(msg)};
const normalize=(v)=>String(v??"").replace(/\s+/g,"").replace(/[‘’'".,·()（）―\-–]/g,"").toLowerCase();
const sources=[
"review/NOMUSA_FIRST_V43_21_SOURCE_READ_ANSWER_DRAFTS_20261118.json",
"review/NOMUSA_FIRST_V43_REMAINING_17_MANAGEMENT_STEM_5OPTIONS_ANSWERS_20261118.json",
"review/NOMUSA_FIRST_V43_2021_ECONOMICS_5_SOURCE_READ_20261118.json",
"review/NOMUSA_FIRST_V43_2020_ECONOMICS_16_SOURCE_READ_CALCULATIONS_20261118.json",
"review/NOMUSA_FIRST_V43_2021_ECONOMICS_REMAINING_19_CALC_GRAPH_20261118.json",
"review/NOMUSA_FIRST_V43_TEN_2020_2021_LABOR_LAW_SOURCE_AND_DRAFTS_20261118.json",
"review/NOMUSA_FIRST_V43_SEVEN_2021_CIVIL_ORIGINAL_STATUTE_DRAFTS_20261118.json",
"review/NOMUSA_FIRST_V43_EIGHT_2021_SOCIAL_ORIGINAL_EXAM_LAW_DRAFTS_20261118.json"];
const reasoning=[
"review/NOMUSA_FIRST_V43_MANAGEMENT_21_FIVE_OPTION_REASONING_20261118.json",
"review/NOMUSA_FIRST_V43_ECONOMICS_5_FIVE_OPTION_REASONING_20261118.json",
"review/NOMUSA_FIRST_V43_10_LABOR_ALL_FIVE_CHOICE_REASONING_20261118.json",
"review/NOMUSA_FIRST_V43_CIVIL_7_FIVE_CHOICE_REASONING_20261118.json",
"review/NOMUSA_FIRST_V43_SOCIAL_8_FIVE_CHOICE_REASONING_20261118.json",
"review/NOMUSA_FIRST_V43_NINE_SHORT_FIVE_CHOICE_SECOND_READ_20261118.json"];
const first=j("review/NOMUSA_FIRST_V43_103_FIRST_PASS_SOURCE_CONTENT_QA_20261118.json");
const cross=j("review/NOMUSA_FIRST_V43_103_SECOND_PASS_515_CHOICES_AND_LAW_QA_20261118.json");
const legal=j("review/NOMUSA_FIRST_V43_25_EXAM_DATE_LAW_PRIMARY_SOURCE_TRIAGE_20261118.json");
const approvals=j("review/NOMUSA_FIRST_V44_VERIFIED_APPROVALS.json");
const original=new Map(),base=new Map();
for(const path of sources){
 const group=j(path);
 for(const q of group.rows || group.records || []){
  const options=q.options||q.optionTexts||q.originalFiveOptionsDraft||q.sourceFiveOptionsDraft||q.allFiveOptionsFromImageDraft||[];
  let answer=q.answer||q.officialAFormKey||q.officialAnswerAForm||q.officialAFormAnswer||q.officialAFormFinalAnswer;
  if(typeof answer==="number") answer=[answer];
  const image=q.originalImagePath||q.originalImage||q.sourceImage||q.imagePath||q.sourceCropImage;
  const imageHash=q.originalImageSHA256||q.sourceImageSHA256||q.imageSHA256||q.sourceCropSHA256;
  const stem=q.question||q.exactOriginalStemDraft||q.sourceStemDraft||q.exactStemFromImageDraft;
  check(!original.has(q.id),"DUPLICATE_ORIGINAL:"+q.id);
  original.set(q.id,{options,answer,image,imageHash,stem,path});
 }
}
for(const q of cross.rows) {
 check(!base.has(q.id),"DUPLICATE_CROSS:"+q.id);
 base.set(q.id,q);
}
check(original.size===103,"ORIGINAL_NOT_103:"+original.size);
check(base.size===103 && first.rows.length===103,"CROSS_NOT_103");
check(cross.checked103===103 && cross.perOptionReasonCount===515,"515_REASON_COVERAGE");
check(cross.perOptionOmissions===0 && cross.duplicateIds===0 && cross.statedSourceKeyConflicts===0,"CROSS_PRIOR_INTEGRITY");
let fullOptions=0,shaValidated=0;
for(const [id,b] of base){
 const q=original.get(id);
 check(!!q,"MISSING_SOURCE:"+id);
 if(!q)continue;
 check(typeof q.stem==="string"&&q.stem.trim().length>=5,"SHORT_STEM:"+id);
 check(q.options.length===5&&q.options.every(x=>typeof x==="string"&&x.trim()),"MISSING_5_OPTIONS:"+id);
 check(JSON.stringify(q.answer)===JSON.stringify([b.officialAFormAnswer]),"OFFICIAL_KEY_MISMATCH:"+id);
 check(q.imageHash===b.originalCropSHA256,"IMAGE_SHA_RECORD_MISMATCH:"+id);
 check(q.image && existsSync(f(q.image)),"IMAGE_MISSING:"+id);
 if(q.image && existsSync(f(q.image))){
  check(sha(q.image)===q.imageHash,"IMAGE_CONTENT_SHA_CHANGED:"+id);
  if(sha(q.image)===q.imageHash)shaValidated++;
 }
 check(b.stemAndChoiceCount===5 && b.perOptionExplanations===5 && b.softwareEvidenceCrosscheck==="PASS","SECOND_PASS_5_REASONS:"+id);
 check(b.approvedForLearningScoring===false && b.needIndependentHumanLegalOrAcademicReview===true,"UNEXPECTED_APPROVAL:"+id);
 fullOptions+=q.options.length;
}
check(fullOptions===515&&shaValidated===103,"UNVERIFIED_ORIGINAL_IMAGE:"+shaValidated);
const explained=new Map();
const falseFlags=[];
let explanationCount=0;
for(const path of reasoning){
 const group=j(path);
 for(const q of group.rows){
  check(!explained.has(q.id),"DUPLICATE_REASON_ID:"+q.id);
  const opts=q.fiveOptions||q.choices||q.options||q.originalOptions||q.improvedChoices||[];
  const source=original.get(q.id), baseRow=base.get(q.id);
  check(!!source&&!!baseRow,"REASON_NOT_IN_103:"+q.id);
  if(!source||!baseRow)continue;
  const correct=opts.filter(o=>(o.correct??o.correctOption??o.isAnswer)===true).map(o=>o.optionNumber??o.number);
  check(opts.length===5&&correct.length===1&&correct[0]===baseRow.officialAFormAnswer,"REASON_TRUE_FLAG_INCONSISTENT:"+q.id);
  opts.forEach((o,i)=>{
   const choice=o.optionText||o.option||o.text||o.statement;
   const reason=o.explanationDraft||o.reason||o.reasonDraft||o.examDateReasonDraft;
   check(normalize(source.options[i])===normalize(choice),"OPTION_WORDING_DRIFT:"+q.id+":"+(i+1));
   check(typeof reason==="string"&&reason.trim().length>=12,"MISSING_REASON:"+q.id+":"+(i+1));
  });
  explanationCount+=opts.length;
  explained.set(q.id,path);
 }
}
check(explained.size===60 && explanationCount===300,"REASON_SET_NOT_60_300");
const first53=first.rows.filter(q=>q.explanationPerOptionProvided).map(q=>q.id);
check(first53.length===52,"FIRST_PASS_52_NOT_CONFIRMED:"+first53.length);
check([...base.keys()].every(id=>explained.has(id)||first53.includes(id)),"REASON_FOR_103_UNCOVERED");
const yearCounts={};
for(const id of base.keys()){const y=id.match(/legacy1-(\d{4})-A-/)?.[1];yearCounts[y]=(yearCounts[y]||0)+1}
check(yearCounts["2020"]===38&&yearCounts["2021"]===65,"YEAR_SPLIT_DRIFT");
const legalRisks=[];
check(legal.rows.length===25,"LAW_COUNT_NOT_25");
for(const item of legal.rows){
 const b=base.get(item.id);
 check(!!b && b.examLawProof!==null,"LAW_ROW_UNMAPPED:"+item.id);
 const c=item.preExamAuthorityCandidate || {};
 let host="UNKNOWN";
 try{const u=new URL(c.url);host=u.hostname;
   check(u.protocol==="https:"&&/(^|\.)law\.go\.kr$|(^|\.)scourt\.go\.kr$|(^|\.)mohw\.go\.kr$/.test(host),"NONOFFICIAL_URL:"+item.id);
   const ef=u.searchParams.get("efYd");
   if(ef && /^\d{8}$/.test(ef))check(ef.slice(0,4)+"-"+ef.slice(4,6)+"-"+ef.slice(6) <= item.examDate,"FUTURE_LINK_EFFECTIVE_DATE:"+item.id);
   if(host.includes("law.go.kr") && u.pathname.toLowerCase().includes("lsinfop") && !ef) legalRisks.push({id:item.id,reason:"LEGAL_CANDIDATE_URL_WITHOUT_EXPLICIT_EFFECTIVE_DATE"});
 }catch{check(false,"INVALID_URL:"+item.id)}
 check((c.sourceEffectiveOrPublishedDate||"") <= item.examDate && !!c.articleOrCaseEvidence,"CANDIDATE_AFTER_EXAM_OR_BLANK:"+item.id);
 check(item.examDate===(item.id.includes("-2020-")?"2020-05-23":"2021-05-08"),"EXAM_DATE_MISMATCH:"+item.id);
 if(!item.fullExamDateAuthorityChecked)legalRisks.push({id:item.id,reason:"FULL_STATUTE_AMENDMENTS_AND_PRECEDENTS_NOT_INDEPENDENTLY_APPROVED"});
 check(item.readyForV44===false && item.independentReviewerApproval===false && item.scoringApproved===false,"LEGAL_APPROVAL_WITHOUT_PROOF:"+item.id);
}
check(legal.preExamSourcePartialAnchors===25 && legal.fullExamDateLawAndCourtHoldingProofApproved===0 && legal.finalIndependentHumanApproval===0,"LAW_EVIDENCE_CLASSIFICATION_CHANGED");
check(Array.isArray(approvals.approvals)&&approvals.approvals.length===0,"UNEXPECTED_V44_APPROVALS");
const draftRows=first.rows.filter(q=>q.independentProofread).length;
check(draftRows===0,"UNEXPECTED_INDEPENDENT_PROOFREAD_COUNT");
const outcome={
 schema:"NOMUSA_FIRST_V47_PREDEPLOY_CONTENT_AUDIT/1",
 asOf:"2026-11-18",
 scope:{sourceRecordCount:original.size,secondCrossCheckCount:base.size,allFiveOptions:fullOptions,verifiedImageHashes:shaValidated,reasonRecordCount:explained.size,reasonOptionCount:explanationCount,firstPassOriginalFiveReasons:first53.length,legalCandidates:legal.rows.length,byYear:yearCounts},
 hardErrors:bad,
 unresolvedLegalRisks:legalRisks,
 approvals:{independentHumanFullText:0,fullExamDateStatutePrecedent:0,approvedNewScoring:0},
 predeployDecision:bad.length?"BLOCKED_STRUCTURAL_ERROR":"HOLD_INDEPENDENT_NATIVE_PROOFREAD_AND_LEGAL_EXPERT_SIGNOFF",
 interpretation:"Machine-verified draft hashes, answers, text agreement and evidence candidate dates; OCR/cross-file matches are not a visually independent source or historical-law judgment.",
 mainProductionPreview:"NO_DEPLOYMENT_OR_SOURCE_PROMOTION_PERFORMED"
};
const out=f("review-artifacts/NOMUSA_FIRST_V47");
mkdirSync(out,{recursive:true});
writeFileSync(resolve(out,"NOMUSA_FIRST_V47_PREDEPLOY_CONTENT_AUDIT.json"),JSON.stringify(outcome,null,2)+"\n","utf8");
console.log(JSON.stringify({status:outcome.predeployDecision,sourceRecords:original.size,allFiveOptions:fullOptions,shaValidated,optionReasons:explanationCount,law:legal.rows.length,errors:bad.length,legalRisks:legalRisks.length}));
if(bad.length){console.error(bad.join("\n"));process.exitCode=1}

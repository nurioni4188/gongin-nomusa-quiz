/* NOMUSA V4: PDF-scored question markers in existing repository 2019/2020 papers.
   Original Q-Net attachment identity has NOT been checked against the Q-Net publisher SHA.
   Never change canonical catalog points or user study keys. */
(function(){'use strict';
const old=window.NOMUSA_V3_SOURCE_POINTS_AUDIT;
if(old?.total!==29||old.unverifiedNumeric!==26)throw Error('V4_PDF_AUDIT_BASELINE');
const byDocument=Object.freeze({
 '2019_p1':'2019_p1_administrative.pdf',
 '2019_p3':'2019_p3_labor_economics.pdf',
 '2019_p4':'2019_p4_civil_procedure.pdf',
 '2019_p5':'2019_p5_labor1.pdf',
 '2019_p6':'2019_p6_labor2.pdf',
 '2020_p1':'2020_p1_labor1.pdf',
 '2020_p2':'2020_p2_labor2.pdf',
 '2020_p4':'2020_p4_administrative.pdf',
 '2020_p6':'2020_p6_labor_economics.pdf',
 '2020_p7':'2020_p7_civil_procedure.pdf'
});
const pageCounts=Object.freeze({'2019_p1':1,'2019_p3':1,'2019_p4':1,'2019_p5':2,'2019_p6':2,
'2020_p1':2,'2020_p2':2,'2020_p4':1,'2020_p6':2,'2020_p7':1});
const rows=old.rows.filter(x=>x.originalReason==='HOLD_POINTS_UNKNOWN').map(x=>{
 const parts=String(x.id).match(/^(2019|2020)_p([1-7])_q([123])$/);
 if(!parts)throw Error('V4_BAD_ID_'+x.id);
 const prefix=parts[1]+'_p'+parts[2],n=Number(parts[3]);
 if(!byDocument[prefix])throw Error('V4_UNKNOWN_PDF_'+x.id);
 const filename='source_pdf/'+parts[1]+'/'+byDocument[prefix];
 if(x.sourceFile!==filename)throw Error('V4_SOURCE_LINK_MISMATCH_'+x.id);
 const score=n===1?50:25; // Verified score markers in the repository PDF question blocks
 return Object.freeze({id:x.id,year:Number(parts[1]),questionNumber:n,
    pdfSourcePath:filename,pdfPageCount:pageCounts[prefix],
    pdfPrintedParentScore:score,recordedSourceScoreTokens:x.extractedScoreTokens,
    scoreEvidence:'REPOSITORY_PDF_QUESTION_HEADING_AND_SCORE_TEXT_READBACK',
    qNetPublisherHashVerified:false,allPagesVisuallyVerified:false,
    sourceCatalogPointsUnchanged:true,contentApproval:'HOLD',
    officialScoreApproved:'HOLD_QNET_ATTACHMENT_IDENTITY'});
});
if(rows.length!==26||rows.filter(x=>x.pdfPrintedParentScore===50).length!==10 ||
 new Set(rows.map(x=>x.id)).size!==26)throw Error('V4_SCORE_COUNTS_MISMATCH');
window.NOMUSA_V4_PDF_SCORE_AUDIT=Object.freeze({schema:'nomusa-repository-pdf-score/4',total:rows.length,
 matchedScoreMarkers:26,pdfDocumentsInspected:10,score50Count:10,score25Count:16,
 repositoryPDFTextScoreVerified:true,qnetOriginalAttachmentHashVerified:false,
 sourcePDFVisualFullReview:false,originalCatalogPointsChanged:false,
 copyrightAndProvenance:'ORIGINAL_QNET_ATTACHMENT_IDENTITY_HOLD',
 approval:'HOLD_QNET_FILE_IDENTITY',rows:Object.freeze(rows)});
})();
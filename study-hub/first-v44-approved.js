/* V44 generated from verified approval manifest only. NEVER OCR auto-approved. */
(function(){'use strict';
const rows=[];
const explanations={};
const bank=window.NOMUSA_V108_EXPLANATIONS;
if(!bank||!bank.entries)throw Error('V44_REQUIRES_EXPLANATION_BANK');
for(const [id,ex] of Object.entries(explanations)){if(bank.entries[id])throw Error('V44_EXPLANATION_DUPLICATE_'+id);bank.entries[id]=Object.freeze(ex)}
window.NOMUSA_FIRST_V44_APPROVED=Object.freeze(rows.map(x=>Object.freeze(x)));
window.NOMUSA_FIRST_V44_SCORING_IDS=Object.freeze(rows.map(x=>x.k));
window.NOMUSA_FIRST_V44_GATE=Object.freeze({verified:rows.length,reviewRequired:789-rows.length,source:'V43_V46_MANIFEST_WITH_DOUBLE_REVIEWER',noOCRPromotions:true});
})();

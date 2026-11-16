/* V11.72 explicit independent 25+25 outlines and verified historical scholarly reference.
 * No change to source ID, points, original compressed text, or score approval.
 */
(function(){'use strict';const c=window.N27_CATALOG;if(!c?.items||!window.NOMUSA_V1171_GATE)throw Error('V1172_REQUIREMENTS');
const id='legacy2-2009-hrm-q2';const r=c.items.find(x=>x.id===id);if(!r||r.points!==50||r.contentRevision!=='V11.71_50PT_SUBSTANTIVE_EXPANSION')throw Error('V1172_COMPOSITE');
const part1={part:1,points:25,targetHandwrittenPages:4,topic:'고령인력 활용을 위한 인력예측기법',outline:['직무별 인력수요와 내부 공급 분석','추세·비율·회귀·마코프 전이의 가정과 한계','고령 숙련인력 대체 가능성과 중요업무 공백','퇴직·계속고용 시나리오와 승계·훈련 설계'],keyTheory:['정량·정성 인력예측','마코프 전이분석','핵심숙련 대체기간'],contentVerification:'HOLD'};
const part2={part:2,points:25,targetHandwrittenPages:4,topic:'직무중심 대 인간중심 평가관리제도',outline:['직무성과·책임과 인간역량·성장가능성 구분','직무중심의 명확한 과업지표와 한계','인간중심의 역량개발 장점과 평정편향','고령근로자의 지식전수·난도·협업 평가사례'],keyTheory:['직무분석과 성과기준','역량 및 잠재력 평가','공정한 행동증거와 개발 피드백'],contentVerification:'HOLD'};
const next={...r,independent25PointStudyPlan:[part1,part2],contentRevision:'V11.72_2009_HRM_SPLIT_STUDY_DRAFT',approved:false,scoringApproved:false,contentApproval:'HOLD',handwritingVerified:false};
c.items=c.items.map(x=>x.id===id?next:x);
const hist='legacy2-2008-organization-q1',o=c.items.find(x=>x.id===hist);if(!o?.examFullLengthDraft)throw Error('V1172_GREINER');
c.items=c.items.map(x=>x.id===hist?{...x,verifiedBibliographyDraft:[...(x.verifiedBibliographyDraft||[]),{authors:'Larry E. Greiner',title:'Evolution and Revolution as Organizations Grow',journal:'Harvard Business Review',year:1972,volume:50,issue:4,verificationUrl:'https://openurl.ebsco.com/c/mlnjjy/openurl?id=ebsco%3ABSU%3A3866992&prompt=true&sid=ebsco%3Aplink%3Adirect',note:'Originally published 1972; HBR Classic reprint 1998, not a separate original study',bibliography:'VERIFIED',theoreticalClaims:'REVIEW_HOLD'}],approved:false,contentApproval:'HOLD'}:x);
window.NOMUSA_V1172_GATE=Object.freeze({compositeId:id,parts:2,independentPagesPerPart:4,greinerOriginalYear:1972,sourceClaims:'PARTIAL_HOLD',handwriting:'NOT_VERIFIED',preview:'NOT_DEPLOYED'});})();
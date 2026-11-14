/* V10.8.7: audited image-to-text OCR corrections. data.js (original bank) is unchanged. */
(function(){'use strict';
const fixes={"2023-경영학개론-101":{"question":"다음 특성에 모두 해당되는 기업의 형태는? 대규모 자본 조달이 용이하다. 출자자들은 유한책임을 진다. 전문경영인을 고용하여 소유와 경영의 분리가 가능하다. 자본의 증권화를 통해 소유권 이전이 용이하다.","options":["개인기업","합명회사","합자회사","유한회사","주식회사"],"image":"2023-BM-101.png"},"2023-경영학개론-102":{"question":"다음 BCG 매트릭스의 4가지 영역 중 시장성장률이 높은(고성장) 영역과 상대적 시장점유율이 높은(고점유) 영역이 옳게 짝지어진 것은? ㄱ. 현금젖소(cash cow) ㄴ. 별(star) ㄷ. 물음표(question mark) ㄹ. 개(dog)","options":["고성장: ㄱ, ㄴ / 고점유: ㄴ, ㄷ","고성장: ㄱ, ㄴ / 고점유: ㄴ, ㄹ","고성장: ㄱ, ㄹ / 고점유: ㄱ, ㄴ","고성장: ㄴ, ㄷ / 고점유: ㄱ, ㄴ","고성장: ㄴ, ㄷ / 고점유: ㄱ, ㄷ"],"image":"2023-BM-102.png"},"2023-경영학개론-103":{"question":"경영환경을 일반환경과 과업환경으로 구분할 때, 기업에게 직접적인 영향을 주는 과업환경에 해당하는 것은?","options":["정치적 환경","경제적 환경","기술적 환경","경쟁자","사회문화적 환경"],"image":"2023-BM-103.png"},"2023-경영학개론-118":{"question":"최종소비자의 수요변동 정보가 전달되는 과정에서 지연이나 왜곡현상이 발생하여 재고부족 또는 과잉 문제가 발생하고 공급사슬 상류로 갈수록 수요변동이 증폭되는 현상은?","options":["채찍 효과","포지셔닝 효과","리스크 풀링 효과","크로스 도킹 효과","레버리지 효과"],"image":"2023-BM-118.png"},"2023-경제학원론-121":{"question":"A국의 15세 이상 생산가능인구는 200명이다. 실업률이 10%, 경제활동참가율이 60%일 때, 취업자수는?","options":["54명","100명","108명","120명","180명"],"image":"2023-EC-121.png"},"2023-경제학원론-123":{"question":"A국의 매 기간 동안 실직률(취업자 중 실직하는 사람의 비율)은 2%, 구직률(실직자 중 취업하는 사람의 비율)은 8%일 때, 균제상태(steady state)의 실업률은?","options":["10%","12%","16%","20%","25%"],"image":"2023-EC-123.png"}};
window.NOMUSA_SOURCE_FIXES=Object.freeze(fixes);
const bank=window.QDATA || [];
for(const q of bank){
 const correction=fixes[q.k];if(!correction)continue;
 if(q.img!==correction.image || q.y!==2023 || q.tx!=='scan' || (q.o||[]).length!==0)continue;
 q.q=correction.question;
 q.o=correction.options.slice();
 q.tx='image_verified';
 q.sourceImageTextRestored=true;
}
})();

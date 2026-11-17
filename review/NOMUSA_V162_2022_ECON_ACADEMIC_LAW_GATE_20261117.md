# NOMUSA V16.2 — 2022년 첫 완성연도 근거·그래프 검산 및 미승인 관문

검토 기준일: 2026-11-17
브랜치: `review/nomusa-auto-v1-20year-gate-20261115`
**운영보호**: 기존 문항ID, 배점, 저장키, RC27·RC35, `main`, Production, 기존 Vercel 배포 변경 없음. 새 Preview 배포 없음.

## 1. 노동경제학 제1문 50점 수학·그래프 정의
원문: `rc27_essay_catalog.js`의 `2022-econ-1` 전사.

| 물음 | 가로축 E | 세로축 C(만원) | 그래프 정의 | 독립 내부수치검산 |
|---|---|---|---|---|
| 1(30점) | 0~15 | 0~15 | C=E, 0≤E≤15 | 절편(0,0), 끝점(15,15) |
| 2(10점) | 0~12 | 0~12 | C=E, 0≤E≤12 | 제한 끝점(12,12); 기존 E*>12면 재최적화 |
| 3(10점) | 0~15 | 0~18.5 | C=E(0≤E≤8), C=1.5E-4(8<E≤15) | 절점(8,8), C(12)=14, C(15)=18.5 |

- 위 좌표·식은 예산선 **수학 검산 PASS**. 위 세 물음의 예산기회를 혼합해서 그래프를 그려서는 안 된다.
- 문제는 소비(C)–노동시간(E) 평면에서 '소비의 한계대체율 체증/체감'을 명시한다. 원전에서 MRS 분자·분모 및 축 정의를 확인하기 전에는 '체감=반드시 경계해' 같은 단정 결론을 금지한다. 현행 V16 서술의 'MRS 체감이면 교점이 극소일 수 있다'는 설명도 특정 정의·2계 조건에 의존하므로 최종 승인 HOLD.
- 시간제약만으로 최적 노동시간 E*를 숫자로 결정할 수 없다. 비근로소득·효용함수가 추가되지 않은 상황에서 추정 수치·임의 곡률을 창작하지 않는다.
- 실제 문제지 PDF 내 표/그래프 시각대조 및 학생에게 표시되는 **실제 정적/동적 그래프의 브라우저 렌더 검증 미실시**. 그러므로 그래프 검증 전체 상태는 **PARTIAL_HOLD**.

## 2. 노동경제학 제2문 정량검산
로렌츠: (0,0)→(.5,.2)→(1,1); B1=0.05, B2=0.30, B=0.35; G=1-2B=0.30. 소득 20·80, 평균 50에 관한 쌍별 차이 120으로 교차검산 G=120/(2×4×50)=.30. **산술 PASS**.
제3문은 파급·위협·대기실업 효과를 분리했으나 도식·선호/수요가정의 독립 경제학 검토는 HOLD.

## 3. 학술 문헌 원문 대조 범위(총 6개)
| ID | 제목 / 원전 | 검증한 내용 | 상태 |
|---|---|---|---|
| 2022-org-1 | Rahim (1983), *A Measure of Styles of Handling Interpersonal Conflict*, Academy of Management Journal 26(2), 368–376, DOI 10.5465/255985 | 자기/타인 관심에 따른 다섯 갈등유형 | 연구 초록 대조 PASS; 문항1·3 출처 HOLD |
| 2022-org-2 | Tversky & Kahneman (1974), *Judgment under Uncertainty: Heuristics and Biases*, Science 185(4157), 1124–1131, DOI 10.1126/science.185.4157.1124; Staw (1976), *Knee-Deep in the Big Muddy*, OBHP 16(1), 27–44, DOI 10.1016/0030-5073(76)90005-2 | 가용성·고착과 몰입심화의 이론적 원전 | 3개 부분 PASS; 나머지 2개 편향의 독립 원전 HOLD |
| 2022-org-3 | Perrow (1967), *A Framework for the Comparative Analysis of Organizations*, ASR 32(2), 194–208, DOI 10.2307/2091811 | 과업 다양성·분석가능성 2축, 네 유형 | 서지·분류 PASS; 통제범위의 방향·인과성 설명 HOLD |
| 2022-hr-1 | Kirkpatrick (1959~1960) *Techniques for Evaluating Training Programs*; Goldstein (1978) *The Pursuit of Validity in the Evaluation of Training Programs*, DOI 10.1177/001872087802000202 | 반응·학습·행동·결과와 Goldstein 훈련/성과/조직내/조직간 타당도 4단계 | 공개 원전 대조 PASS; ROI 원전·금액 산정 HOLD |
| 2022-hr-2 | 내부모집의 장단점 | 원장상 장점3·단점3 구조 확인 | 특정 서지 미확인 HOLD |
| 2022-hr-3 | 노사교섭 포용·압박·회피 전략 | 원장상 3전략별 실행방안 2개 구조 확인 | 전략 분류 원전·연도 미확인 HOLD |

출처:
- https://journals.aom.org/doi/10.5465/255985
- https://pubmed.ncbi.nlm.nih.gov/17835457/
- https://www.sciencedirect.com/science/article/pii/0030507376900052/pdf
- https://www.jstor.org/stable/2091811
- https://assets.td.org/m/4a306d561507658e/original/TECHNIQUES-FOR-EVALUATING-TRAINING-PROGRAMS.pdf
- https://journals.sagepub.com/doi/10.1177/001872087802000202

## 4. 2022 법률 25점 검증
- `2022-labor1-2`: 대법원 2022.4.28. 선고 2019다238053(정기상여금) 공개 판시요지 원문 및 국가법령정보센터 판례요지 확인. 재직조건을 다른 협약·취업규칙 규정·지급 관행과 함께 해석하여 근무일수 비례분의 고정성을 인정하는 결론과 소스 일치. https://www.scourt.go.kr/portal/news/NewsViewAction.work?gubun=4&seqnum=8404
- `2022-labor2-2`: 대법원 2020.7.29. 2017도2478 산별노조 간부의 30분 사업장 현장순회 사건과 사실관계 대조. 한국노동연구원 판례리뷰 요지 확인. https://www.kli.re.kr/kli/prcdntView.es?currentPage=10&keyField=&keyWord=&keyYear=&mid=a10202000000&prcdnt_no=135285
- 나머지 `2022-admin-2`, `2022-admin-3`, `2022-civil-2`, `2022-civil-3`: 기출 원장 텍스트와 답안의 논점 연결만 확인. 시험일 시행 법령·공식 판결문 전문의 **독립 대조 HOLD**.
- 이번 근거 보충파일 `second/nomusa-v162-2022-academic-and-labor-precedent.js`는 2022 경영·인사 6문항과 노동법Ⅱ 25점 1문항에 주석을 추가하되 이전 답안·자동채점·문항 ID를 수정하지 않음.

## 5. 브라우저 및 필기분량 게이트
- GitHub 모의 canonical 데이터에서 위 7개 모두 source note 적용·기존 답안 보존·`scoringApproved=false` **7/7 PASS**. 두 HTML 경로가 새 파일을 연결함 **PASS**.
- **실제 Chromium PC 1440px 및 모바일 390px/360px** 브라우저를 인증·실행하는 도구는 이번 실행환경에서 제공되지 않아 **E2E NOT RUN/HOLD**. 과거 E2E 통과증거를 현재 V16.2 변경의 재검증으로 대체하지 않음.
- 앱의 500자/쪽 환산은 실제 시험장 수기 50점 8~10장·25점 4장을 보증하지 않으므로 **수기 분량 HOLD**.
- 모든 2022 19개 정식 내용승인은 **HOLD**. '2022 최종 완성'으로 표시하거나 Preview·Production에 자동 배포하지 않는다.

**최종 판정: 산술 검산 PASS / 원전·판례 공개요지 부분검증 PASS / 문항 7개 출처 연결 PASS / 원문 시각·판례전문·실제 필기분량·브라우저 E2E·독립 승인 HOLD.**

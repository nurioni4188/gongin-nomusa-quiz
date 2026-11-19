# NOMUSA V16.3 — 2022 첫 완성연도 세 관문 실증 검증 결과 (2026-11-17)

브랜치: `review/nomusa-auto-v1-20year-gate-20261115`. 범위: 2022년 2차 기출 원장 **19개 대문항**. GitHub main·Vercel Production·기존 Preview·저장키·문항 ID·배점 불변. 신규 Preview 배포 없음.

## A. 실제 실전답안 분량 관문 — 아직 HOLD

- 원장 `review/NOMUSA_309_CANONICAL_SELECTION_V1_20261116.json`의 2022 `primary` 19개를 전수 합산: **50점 7개, 25점 12개 = 650점(모든 선택과목 합산)**.
- 사용자 고정 분량 설계(50점 8~10장, 25점 4장) 적용 시 **목표 104~118장**(7×8~10+12×4). 이는 *모든 선택과목 학습답안의 가정 목표 장수*이며, 실제 응시자 1인의 답안 장수나 실측 필기량이 아니다.
- 소문항 예: 노동경제학 제1문 50점은 30+10+10점. 50점 8~10장 기준 배분하면 30점 4.8~6장, 각 10점 1.6~2장. 다만 시험장 장수 표기 시 반올림 및 그래프 배치 고려 필요.
- 현재 상세답안의 글자수와 앱 자체의 임의 환산식만으로 수기분량·필기 소요시간 보증 불가. 19개 전체 물리적 답안지 샘플 및 속도 검증 **HOLD**.
- 개별 답안의 길이 결함을 숨기지 않는다. 최종 승인수 0.

## B. 근거검증 — 부분 PASS, 최종 HOLD

- **시험일 기준**: 제31회 2차 공인노무사 시험은 2022.9.3.(토)~9.4.(일). 출처: 한국산업인력공단 2022년도 시행계획 공고(언론의 공고 전문) https://www.lec.co.kr/news/articleView.html?idxno=734276. 시험과목별 해당일을 확인해 판례 선고일·법령 시행일·부칙을 검증한다.
- **2022-admin-2**: 2020.2.20. 대법원 전원합의체 2019두52386은 구제절차 중 정년·기간만료로 복직 불능일 때도 임금상당액 구제에 관한 소의 이익을 인정. 대법원 공개 판시요지 https://jifi.scourt.go.kr/portal/news/NewsViewAction.work?gubun=4&seqnum=7000 . 대법원 2022.7.14. 판결은 구제신청 이전 근로관계 종료와 진행 중 종료의 차이를 강조. https://www.scourt.go.kr/portal/news/NewsViewAction.work?gubun=4&seqnum=8655 . 원문 2022년 기출의 금전보상 청구·정년규정 시행 사실과 구분 후 적용해야 함.
- **2022-hr-1**: 기존 V16.2의 Goldstein (1978) *Human Relations* 표기는 **출판지 오류**. 실제 출판지 *Human Factors*, **20(2), 131–144**, DOI:10.1177/001872087802000202. 학술지 공식 페이지 https://journals.sagepub.com/doi/10.1177/001872087802000202 직접 대조. 이 학술출처 교정을 `second/nomusa-v163-2022-citation-corrections.js`에 추가.
- 이전 V16.2의 Rahim/Perrow/Kirkpatrick, 노동법2 2017도2478, 노동법1 2019다238053 등 공개 원전·판시요지 확인은 유지하지만, *원문 전체 문장·시험일 시행법령/부칙의 19문항 독립 검증*은 여전히 HOLD.
- HR 내부모집 및 노사교섭 세 전략의 특정 서지·연도, Perrow 모형의 통제범위에 관한 정확한 경향, 2022 경제학 MRS 분자·분모 및 곡률·그래프 해석은 추가 검증 필요.

## C. 실제 Chromium PC/모바일 E2E — PASS (테스트 범위 명시)

- 기존 Github Actions `.github/workflows/nomusa-canonical-e2e.yml`는 `review/nomusa-auto-v1-20year-gate-20261115`의 검토 커밋만 대상으로 checkout하고, `playwright==1.56.0` Chromium을 설치하여 `scripts/nomusa-canonical-shared-browser-gate.py`를 실행한다.
- 기존 실제 공통 학습 화면 저장·복원/탭 이동·화면 간 공유 및 오버플로 검사 **2026.11.17 run 44030044079 PASS**. https://github.com/nurioni4188/gongin-nomusa-quiz/actions/runs/44030044079
- 이번에 기존 테스트 스크립트에 **2022 19개 ID의 상세·압축답안 두 화면 일치, 미승인 상태, V16.1 보강 13개와 V16.2 메모 7개 로드 확인**을 PC1440, mobile390, mobile360별로 추가했다. 검증 대상 커밋 `c95a48b5d2ebb1615752b4b4e45c71fbbd7298d6`.
- **실제 run 44030673658 결론 SUCCESS**, 테스트의 3 viewport 모두 통과. https://github.com/nurioni4188/gongin-nomusa-quiz/actions/runs/44030673658
- 검증 범위의 한계: 2022년 19개 개별 문제 모두에서 필기 저장·복원을 반복하지는 않았고, 이론·사안포섭의 정답을 검증한 것도 아니다. 테스트는 GitHub checkout 코드에서 실행됐으며, Vercel 보호 Preview URL 자체의 최종 접속 인수검사는 아님.
- Github Actions의 이어지는 취소된 runs는 push 동시 실행 방지 `cancel-in-progress`에 의한 교체로, 최종 SUCCESS 실행을 무효화하지 않는다.

## D. 기존 앱에 반영한 수정

- `second/nomusa-v163-2022-citation-corrections.js`: Goldstein 출판지 오류 정정; 2022 행정쟁송법 25점 금전보상·정년 판례 시점 구별.
- 두 학습 화면 `second/index.html`, `study-hub/index.html`에 V16.3의 출처교정 파일 로드 연결.
- 근거보충 2개 레코드의 모의 JS 적용 **2/2 PASS**, 이전 원고 보존, 자동채점 승인 유지=false.
- `scripts/nomusa-canonical-shared-browser-gate.py`: 2022 19개 전수 데이터 병치 확인 및 3종 viewport 회귀검증 강화.

## 결론
| 게이트 | 결과 |
|---|---|
| 2022 19개 기출 연결·상세·압축 PC·모바일 실제 Chromium 데이터 동등성 | PASS |
| 저장·복원 공통 회귀검증 | PASS |
| 2022 원본 PDF 전체 시각대조 및 문항별 개별 입력/저장 복원 | HOLD |
| 노동경제학 예산선·지니 산술 | PASS / 선호곡선 완전 검증 HOLD |
| 일부 공개 판례·학술서지 대조 | PARTIAL PASS |
| 시험 당일 법령·판례 전체 독립 내용검증 | HOLD |
| 50점 8~10장·25점 4장 실제 필기분량 | HOLD |
| 독립 전문가의 학술·법리 최종 승인 | HOLD |
| Vercel Preview 인수검사 및 Production 배포 | 미실시 / HOLD |

**2022 학습 기능의 GitHub 검토 브랜치 Chromium 핵심 E2E PASS, 그러나 '2022 최종 완성연도' 선언은 아직 HOLD.** 다음 작업은 기능 개발보다 19개 답안 분량·법리의 실제 최종 승인에 집중한다.

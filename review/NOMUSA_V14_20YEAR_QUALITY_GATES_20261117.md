# NOMUSA V14 — 20개년 문항별 품질평가 착수 및 검증 관문

- 기준: GitHub review branch V13 `f09e1b2e50655c74169b8d941e6e4cf2ee2cf283`.
- 범위: 2007~2026, 기존 377문항 카탈로그와 328개 학습답안 후보. 50점 답안 113개.
- 데이터의 원본 ID/배점/localStorage/원본 문서/운영 UI를 변경하지 않는 **검토용 기록**.
- 아래 판정은 답안의 **내용 품질에 대한 최종 승인**을 의미하지 않는다.

## 평가 기준 (100점)
- 원문·출제의도 10
- 쟁점·목차 15
- 법령·판례 또는 해당 과목의 학술 근거 20
- 논증의 깊이 15
- 사안포섭 또는 이론·계산의 응용 20
- 결론·풀이의 완결성 10
- 시험장 실전 적합성 10

## 단계
- 1: 자료 확보(0~39)
- 2: 기본 초안(40~59)
- 3: 상세답안 구축(60~79)
- 4: 실전형 고도화(80~89)
- 5: 검증된 모범답안(90~100, 중대 오류 0, 근거/원문 대조 완료, 실전 학습 기능 검증)
- **UNASSESSED**: 원문·답안 전문·근거를 직접 심사하지 않아 점수와 단계를 부여할 수 없음. UNASSESSED는 1단계나 미작성으로 해석하지 말 것.

## V13 직접 확인된 12개 문항 — 구조 증빙만 확보, 품질 단계 미확정
| 연도 | 문항 ID | V13 상세 글자 수 | 판정 |
|---|---|---:|---|
| 2022 | 2022-labor1-1 | 5105 | UNASSESSED_CONTENT |
| 2022 | 2022-labor2-1 | 4506 | UNASSESSED_CONTENT |
| 2022 | 2022-admin-1 | 4308 | UNASSESSED_CONTENT |
| 2022 | 2022-civil-1 | 4911 | UNASSESSED_CONTENT |
| 2023 | 2023-labor1-1 | 4929 | UNASSESSED_CONTENT |
| 2023 | 2023-labor2-1 | 4411 | UNASSESSED_CONTENT |
| 2023 | 2023-admin-1 | 4880 | UNASSESSED_CONTENT |
| 2023 | 2023-civil-1 | 4066 | UNASSESSED_CONTENT |
| 2025 | 2025-labor1-1 | 4782 | UNASSESSED_CONTENT |
| 2025 | 2025-labor2-1 | 4568 | UNASSESSED_CONTENT |
| 2025 | 2025-admin-1 | 5245 | UNASSESSED_CONTENT |
| 2025 | 2025-civil-1 | 5551 | UNASSESSED_CONTENT |

V13에서 상세·압축·암기카드가 보강되었고 브라우저 검증 18/18 PASS이나, **판결 전문 직접대조 0건, 필기 검증 0건, 최종 승인 0건**. 자동으로 4·5단계를 부여하지 않는다.

## 전체 20개년 현황 (등급이 확정된 문항 수)
| 연도 | 확인된 V13 고도화 문항 | 5단계 최종완료 |
|---|---:|---|
| 2007 | 0 | 미집계 |
| 2008 | 0 | 미집계 |
| 2009 | 0 | 미집계 |
| 2010 | 0 | 미집계 |
| 2011 | 0 | 미집계 |
| 2012 | 0 | 미집계 |
| 2013 | 0 | 미집계 |
| 2014 | 0 | 미집계 |
| 2015 | 0 | 미집계 |
| 2016 | 0 | 미집계 |
| 2017 | 0 | 미집계 |
| 2018 | 0 | 미집계 |
| 2019 | 0 | 미집계 |
| 2020 | 0 | 미집계 |
| 2021 | 0 | 미집계 |
| 2022 | 4 | 미집계 |
| 2023 | 4 | 미집계 |
| 2024 | 0 | 미집계 |
| 2025 | 4 | 미집계 |
| 2026 | 0 | 미집계 |

## 전체 50점 답안의 후속 대상
- 법률 개별심화 30개, 법률 기본초안 28개, 비법률 개별심화 3개, 비법률 기본초안 52개.
- V14 우선: 법률 기본초안 28개 **문항 ID·문제 원문·배점 원장으로 식별한 뒤** 개별 재작성.
- 다음: 2019·2020 법률 50점 8개 상세 논증 보강. V13 12개는 판결 전문 직접대조.
- 2007~2011 HWP 문항 등 원문 시각 대조가 필요한 문항은 원문 확정 전에 5단계 승인 금지.
- 검증 없이 일반형 논술을 반복하거나 글자 수만 늘리는 작업 금지.

## 문항별 평가 원장의 필수 필드
`year, subject, questionId, points, sourceVerified, sourcePage, answerExists, actualCharacters, rubricScores{source,issue,evidence,argument,application,conclusion,exam}, totalScore, stage, caseLawVerified, substantiveErrors, handwritingVerified, browserVerified, reviewer, reviewedAt, outstandingIssues, evidenceLinks`.

각 문항에 대해 문서/원문/판례가 없는 상태에서 점수를 채우지 말 것. 검증된 단계 5만 연도별 완료율의 분자에 사용:
`finalCompletionRate = stage5Count / catalogQuestionCount * 100`.

## V14 실제 검토 관문 및 차기 실행
1. 377 카탈로그 ID·연도별 분모를 추출하고 328답안과 LEFT JOIN하여 전수 문항 ID 행 생성.
2. 우선 법률 기본초안 28개·2019/2020 8개·V13 12개 = 48개 각 답안의 원문 대조·실질 채점.
3. 28개 재작성은 각 문제와 일치하는 근거 및 독립적인 소문항별 포섭을 충족해야 '완료'로 기록.
4. 5단계 인증 전에 판례 원문·시행 당시 법령, 시험장 압축답안, 모바일 기능 확인.
5. GitHub 검토 브랜치만 수정; main/Production/Preview 배포/저장키 불변.

## 현재 판정
**V14_QUALITY_GATES_DEFINED / V13_SOURCE_VERIFIED / ITEM_LEVEL_GRADING_HOLD / V14_CONTENT_REWRITE_NOT_STARTED / DEPLOY_NOT_RUN**.

이 문서는 평가 체계를 실제 GitHub 검토 브랜치에 기록한 첫 단계다. 단순 검증표를 완성된 모범답안으로 보고하지 않는다.

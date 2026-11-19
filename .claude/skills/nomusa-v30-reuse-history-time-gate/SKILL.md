---
name: nomusa-v30-reuse-history-time-gate
description: "공인노무사 2차 20개년 328개 학습답안에서 V9~V29 기존 교정·검증을 재활용하고, 시험 이후 법령·판례의 참고와 소급적용을 구분해 실제 오류가 확인된 경우만 교정 대상으로 추리는 Claude Code 프로젝트 스킬."
---

# NOMUSA V30 — 이미 수행된 실질 교정 재사용, 시험일 법령·판례 잔여 관문

## 목적
- 기존 검토 브랜치 `review/nomusa-auto-v1-20year-gate-20261115`, Draft PR #3에서 328개 답안의 교정 작업을 중복하지 않는다.
- 2022년 19개는 V27 6 + V28 13 **부분 주장 근거** 연결 완료. 나머지 309개도 V9~V20의 실질 편집·보강이 진행됨을 인정한다.
- **다시 전면 집필하지 않는다.** 근거 오류·시점 혼입이 실제로 확인될 때만 문항별로 보존형 교정한다.
- `main`, RC27, RC35, Production, 기존 Preview, 기출 원본, 문제 ID, localStorage 저장키, 기존 원고는 무단 변경하지 않는다.

## 입력 자산 (선행 작업을 버리지 말 것)
- `review/NOMUSA_V23_VALIDATION_LEDGER.json`: 328개 공식 Q-Net 출처 연결·텍스트 SHA, 법령/판례·학술 후보.
- `review/NOMUSA_V27_2022_PRIMARY_CONTENT_CROSSCHECK_20261118.json` / `review/NOMUSA_V28_2022_REMAINING_13_SOURCE_CROSSCHECK_20261118.json`: 2022년 19건 부분 주장 교차확인.
- `second/nomusa-v12-apply.js` 20건, `second/nomusa-v13-apply.js` 12건, `second/nomusa-v15-labor_a.js`/`labor_b.js` 14건, `second/nomusa-v20-apply-substantive-88.js` 88건 보강, V9 실제 4건.
- `scripts/nomusa-v29-2022-baseline-review.py`: Chromium 20개년 328개 표시 답안 SHA 검증.
- `review/NOMUSA_V28_2022_19_EXECUTION_20261118.md`: Goldstein 서지 및 교육기법 1건 **이미 교정**; 이번 V30에서 중복수정 금지.

## 빠른 재실행 명령
1. `python scripts/nomusa-v30-reuse-history-time-gate.py --self-test`
2. `python scripts/nomusa-v30-reuse-history-time-gate.py .` — V23/V27/V28/V9/V12/V13/V15 연결 빠른 전수확인.
3. `python scripts/nomusa-canonical-shared-browser-gate.py .` — 실제 PC 1440px, Mobile 390/360px 및 저장·복원 원고 추출.
4. `python scripts/nomusa-v30-reuse-history-time-gate.py . --rendered` — 실제 화면 328개 원고 SHA·V20 88개 문항별 보강 및 연혁 경고 연결.
5. 결과물은 `review-artifacts/NOMUSA_V30/`의 JSON·328개 CSV·연도별 보고서. CI artifact에서 내려받는다.

## 선별 우선순위와 해석
- 1차 시점 집중점검 7건: 2007년 교섭창구단일화(당시 비적용), 2009년 원청 사용자성 후속 2010 판결, 2009년 해고예고 2014/2019 규정, 2012년 통상임금 2013 이후 판결, 2013년 취업규칙 2023 전원합의체, 2020년 행정기본법 2023 시행 조문, 2022년 통상임금 2024 전합.
- 판결문 전문 추가대조 3건: `2014_p2_q1`(2011두7526), `2022-labor1-1`(2012다81609), `2026-행정쟁송법|2|0`(2024구합76393). 일부 외부 근거 보강이 기존에 있었음; '허위 사건번호'로 단정 금지.
- OCR 원문 글자별 검토 1건: `2016_p5_q2`(V23~V29 MEDIUM).
- 전체 P1 77 분량 위험 검토 및 P2 35, P3 197은 **이미 작성된 원고를 보존**하면서 실제 논증·실전분량 전문가 심사를 위해 순차 정렬한다.
- 2022년 V27/V28은 **부분 원전 근거 확보**, 내용 전체 승인 불가. 309개도 기존 법령·판례 확인 이력을 없었던 것처럼 처리하지 않는다.
- 후대 판례·법령의 `시험 후 참고` 표시는 **허용되는 비교 학습**이고, 정답 소급적용과 다르다. 선고 연도만으로 시험일 이후임을 확정할 수 없으니 시험일·선고일·시행일·부칙을 먼저 비교한다.

## 교정 조건
- 구체적인 현행 오류가 원판결 전문/연혁법령/공식 시험문항 원본 등으로 재현될 때만 `CORRECTION_REQUIRED` 확정.
- 구 원고 SHA·변경 전 상세/압축·해당 문장·원전 출처·시험일/시행일을 기록. 과거 화면과 저장키를 깨뜨리지 않는다.
- 법률과목은 시험일 기준 연혁법령·부칙/판결문 전문/사안포섭, 이론은 원저서·원논문, 경제는 원본 수치·기호·그래프와 수기장수 확인.
- 외부 독립 검토자 자격·검토일·서명·근거·특정 현재 텍스트 SHA가 없으면 `FINAL_APPROVAL=HOLD_0_OF_328` 유지. 승인·서명 위조 금지.
- 본 스킬은 저장소 안의 Claude Code 프로젝트 스킬이다. 전역 설치나 타 서비스 자동연결을 뜻하지 않는다.

## 결과·금지
- `review-artifacts/NOMUSA_V30/NOMUSA_V30_328_REUSED_HISTORY_AND_TIME_GATE.json`
- `review-artifacts/NOMUSA_V30/NOMUSA_V30_328_REVIEW_QUEUE.csv`
- `review-artifacts/NOMUSA_V30/NOMUSA_V30_TIME_EFFECT_DELTA_REPORT.md`
- CI `.github/workflows/nomusa-v30-history-time-effect-review.yml`는 contents:read, no write/commit/deploy/email.
- **자동검증 PASS**는 법령·판례·학술 전문 정합성 또는 전문가 최종승인이 아님.

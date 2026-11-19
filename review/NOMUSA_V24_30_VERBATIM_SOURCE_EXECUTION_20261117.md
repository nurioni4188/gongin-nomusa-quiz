# NOMUSA V24 — 2015~2018·2021년 인사/조직 30개 기출 요지문항 원문 전사 교체 결과

2026-11-17(한국시간) · 프로젝트: `nurioni4188/gongin-nomusa-quiz` · 검토 브랜치 `review/nomusa-auto-v1-20year-gate-20261115`.

## 최종 판정

**PASS_30_SOURCE_TEXT_REPLACEMENTS / PASS_CHROMIUM_REGRESSION / HOLD_INDEPENDENT_CHARACTER_PROOFREAD / HOLD_EXPERT_APPROVAL**.

- 2007~2026년 20개년 전체 328개 기존 학습문항·상세·압축답안 구조 보존.
- V23에서 공식 기출의 **요지**로 표시한 2015~2018·2021년 인사노무관리론·경영조직론 **30개를 PDF 원전 이미지에 근거한 상세 전사문으로 교체**, 5개년 × 6개(인사3·조직3), 50점 10개/25점 20개.
- **기존 298개 문항의 전체 본문 SHA 불변**, V24 30개의 sourceText만 변경해 새 본문 SHA를 생성. 이전 원고는 `sourceTextBeforeV24`로 브라우저 카탈로그 오버레이에 보존.
- **Q-Net 공식 첨부파일 해시 동일 328/328** 유지. 기출 전사문 교체 후 V23 `storedQuestionIsSummary=0`, 자동 겹침 등급 HIGH 325/MEDIUM 3, 기존 공식 출처연결 328/328.
- MEDIUM 3개: **2016_p5_q2**(이 V24 교체대상, 겹침률 0.80), 기존 비대상 **2019_p4_q3**(0.7826) 및 **2020_p7_q3**(0.8077). 기계적 문자 중첩률은 글자별 독립 교열 결과가 아니므로 2016_p5_q2 재확인 권장.
- 2018 경영조직론 제1문 소문항 배점은 공식 인쇄 원본 **20점·30점**이며 OCR '90점'은 오독. 2021 경영조직론 '1971년 올슨(J. Olsen) 등' 공식 지문 그대로 보존, 후대 학술 정정은 시험원문에 넣지 않는다.
- **독립 전문가 내용승인 0/328, FINAL_APPROVAL=HOLD.** 법령·판례 전문 검토, 학술 문헌 원서, 실제 수기 필기분량·전문가 서명, 개별 PDF 글자별 교열은 완료되지 않았다.

## 실행증빙

- V24 원본 PDF 페이지 이미지: GitHub Actions [run 44094781250](https://github.com/nurioni4188/gongin-nomusa-quiz/actions/runs/44094781250), [artifact 14332204049](https://github.com/nurioni4188/gongin-nomusa-quiz/actions/runs/44094781250/artifacts/14332204049).
- 실제 완성 검증: GitHub Actions [run 44097717695](https://github.com/nurioni4188/gongin-nomusa-quiz/actions/runs/44097717695) **completed/success**.
- 실행 범위: Python V19/V21/V22/V23/V24 self-test → 양 학습 화면 V24 overlay smoke → Chromium 1440/390/360 PC·모바일 저장복원 E2E → V19/V21/V22 구조 → 30개 원문교체/298개 SHA 불변 → V23 328개 원장 재생성 → 자동 불변식 검사 → 기존 검토 브랜치에만 ledger 자동커밋.
- V24 워크플로 시작/완료(UTC): **2026-11-17 13:56:10 ~ 13:57:58**, 약 **108초**. V23 원장 재생성 스크립트 22.007초.
- GitHub Actions [결과 artifact 14335230984](https://github.com/nurioni4188/gongin-nomusa-quiz/actions/runs/44097717695/artifacts/14335230984)에는 30개 전사문별 SHA 감사원장과 재생성 V23 328개 원장이 포함됨.
- 자동 재생성 ledger review branch 커밋: `8a2b145d0025cfc6a4d9e0b783eeb53f43b0fa58`.
- 초기 V24 실패: [run 44097033642](https://github.com/nurioni4188/gongin-nomusa-quiz/actions/runs/44097033642) 및 [run 44097487905](https://github.com/nurioni4188/gongin-nomusa-quiz/actions/runs/44097487905). 원인은 2018/2021 요지 표기 방식의 차이로 30개 원자적 반영 사전검사 HOLD → 기존 V23 요지 감지 정규식과 일치시켜 수정 후 전체 PASS.

## 변경된 파일(검토 브랜치 내부만)

- `second/nomusa-v24-verbatim-2015-2016.js` (12개), `second/nomusa-v24-verbatim-2017-2018.js` (12개), `second/nomusa-v24-verbatim-2021.js` (6개).
- `second/nomusa-v24-apply-verbatim-30.js` 및 두 UI loader `second/index.html`, `study-hub/index.html`.
- `scripts/nomusa-v24-target-source-images.py`, `scripts/nomusa-v24-browser-overlay-smoke.py`, `scripts/nomusa-v24-verbatim-check.py`.
- `scripts/nomusa-v23-validation-ledger.py` 수동 요지 등급의 교체 후 재검증 정합성 수정.
- `.github/workflows/nomusa-v24-source-page-review.yml`, `.github/workflows/nomusa-v24-verbatim-30-gate.yml`.
- 재생성 `review/NOMUSA_V23_VALIDATION_LEDGER.json`, 신규 스킬 `.claude/skills/nomusa-v24-verbatim-source/SKILL.md`.

## 후속 승인관문

1. 공식 PDF 이미지와 교체된 30개 `sourceText`를 **독립 교열자**가 글자별 대조한다. 특히 2016_p5_q2, 2018년 영어 원전 용어, 2021년 영문 표기·표·구두점.
2. 오자 발견 시 해당 문항의 `sourceText`만 수정, ID·배점·원본 파일·학습 저장키·상세/압축답안 불변을 유지하고 SHA 갱신 후 동일 CI 재검증.
3. 역사 법령·판례 전문·학술원전 확인, 실제 손글씨 분량, 독립 전문가 자격·서면 심사의견이 있어야만 개별 답안을 승인한다.
4. GitHub main, Production, 기존 Preview 및 RC27/RC35는 변경하지 않는다. 이메일 발송·새 배포·Draft PR 병합 없음.

**결론: 30개 원문 요지 교체와 PC/모바일 기술 QA 완료, 글자별 독립 교열 및 최종 내용승인 HOLD (0/328).**

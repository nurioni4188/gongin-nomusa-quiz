---
name: nomusa-v24-verbatim-source
description: "공인노무사 2차 2015~2018년·2021년 인사노무관리론/경영조직론 30개 요지문항을 Q-Net 공식 PDF 원문 이미지 전사문으로 교체, 검토 브랜치에서 PC/모바일 자동검증·V23 원장 SHA 갱신. 전사문의 독립 글자별 교열 및 최종 전문가 승인은 HOLD."
---

# NOMUSA V24 — 30개 공식 기출 원문 전사·교체·회귀검증

## 시작 지시
"V24 스킬로 2015~2018년 및 2021년 인사노무관리론·경영조직론 원문 30개를 검증하고, 328개 답안의 학습 저장·복원·배점·원고 SHA를 회귀검증하여 독립 전문가 검토패킷을 준비하라."

**이 스킬은 저장소 내부의 Claude Code용 재사용 지침이다. ChatGPT 전역 스킬 설치를 의미하지 않는다.**

## 불변 조건
- GitHub `nurioni4188/gongin-nomusa-quiz`, 검토 브랜치 `review/nomusa-auto-v1-20year-gate-20261115`, Draft PR #3.
- GitHub `main`, Vercel Production/Preview, RC27/RC35, 기존 수험생 저장키, 기존 문제 ID, 모든 공식 PDF/HWP 바이너리는 변경 금지.
- 원전·내용 전문가 심사와 소스 전사 교정은 별개다. 독립 서면승인과 수기분량 실측 없는 항목의 FINAL_APPROVAL=HOLD, 승인 0/328.
- 기존 V23 328문항/Q-Net 공식 첨부 해시 일치 PASS·고정된 PDF/HWP/배점 원장은 재사용한다. 불필요한 재개발·공식 URL 중복 다운로드 금지.

## V24 실행 결과 (2026-11-17)
- **30개 전사 텍스트 교체 PASS**: 2015,2016,2017,2018,2021년 × 6문항=30개; 각 연도 인사노무관리론3 + 경영조직론3.
- 50점 10개/25점 20개. 2018 경영조직론 제1문 물음1은 원본 20점, 물음2 30점. OCR의 '90점'은 오인식.
- 2021 경영조직론 쓰레기통 의사결정 모형 공식 문제의 '1971년 올슨(J. Olsen) 등'은 당시 시험 원문 표기로 그대로 보존. 학술 연구 논문의 보편적 인용연도와는 내용심사에서 따로 구별할 것.
- V23 최종 재생성 원장: 328 고유 ID·원본파일 동일성 328/328, 저장된 요지문항 0개, 원전 텍스트 일치등급 HIGH 325/MEDIUM 3, 전문가 0, FINAL_APPROVAL=HOLD.
- 기존 비대상 298개 문항 SHA 불변. 대상 30개는 sourceText만 변경하며 기존 상세/압축 본문·이전 요지 복구 스냅샷 유지.
- 실행: [GitHub Actions V24 44097717695](https://github.com/nurioni4188/gongin-nomusa-quiz/actions/runs/44097717695) completed/success, 2026-11-17 13:56:10~13:57:58 UTC (약 108초); 본문 V23 ledger 계산 22.007초.
- 결과 artifact: [14335230984](https://github.com/nurioni4188/gongin-nomusa-quiz/actions/runs/44097717695/artifacts/14335230984).
- 검토 브랜치 재생성 원장 커밋 SHA: `8a2b145d0025cfc6a4d9e0b783eeb53f43b0fa58` (해당 실행 후 기록 기준).
- 사람의 독립적인 PDF 원문 **글자별 교열·판결문 전문/학술 인용 검증은 아직 HOLD**. AI 시각 전사는 공식 문서 자체가 아니며 오자/용어/문장부호 교정 대상이다.

## 원본 증빙과 배치 파일
- Q-Net 공식 첨부 SHA 매니페스트: `review/NOMUSA_V23_QNET_OFFICIAL_MANIFEST.json`.
- PDF 파일 원본: `source_pdf/2015/2015_second_full_original.pdf` 등 2015~2018년, `source_pdf/2021/2021_day1.pdf`, `source_pdf/2021/2021_day2.pdf`.
- 원문 시각 검토를 위한 이미지 렌더링: `scripts/nomusa-v24-target-source-images.py`, `.github/workflows/nomusa-v24-source-page-review.yml`, Actions [44094781250](https://github.com/nurioni4188/gongin-nomusa-quiz/actions/runs/44094781250), PNG artifact [14332204049](https://github.com/nurioni4188/gongin-nomusa-quiz/actions/runs/44094781250/artifacts/14332204049).
- 전사 데이터: `second/nomusa-v24-verbatim-2015-2016.js` (12), `second/nomusa-v24-verbatim-2017-2018.js` (12), `second/nomusa-v24-verbatim-2021.js` (6).
- 안전 적용: `second/nomusa-v24-apply-verbatim-30.js` (대상/배점/원장 요지 사전검사, 오리지널 sourceTextBeforeV24 보존, scoringApproved=false).
- 학습 UI 양쪽: `second/index.html`, `study-hub/index.html`에서 V20 답안 적용 후 네 V24 스크립트를 로드.
- 검증: `scripts/nomusa-v24-browser-overlay-smoke.py` (양 페이지 오버레이), `scripts/nomusa-v24-verbatim-check.py` (30 SHA 변경/298 불변/승인 0), 기존 `scripts/nomusa-canonical-shared-browser-gate.py` (PC1440/모바일390/360 저장복원).
- V23 ledger 원본대조 스크립트의 **구 요지 수동 등급**은 요지문항에서만 사용하고, 전사로 교체한 문항은 PDF/OCR과의 실제 겹침률을 새로 계산한다: `scripts/nomusa-v23-validation-ledger.py`.
- 자동 실행: `.github/workflows/nomusa-v24-verbatim-30-gate.yml` (ubuntu-24.04, Actions에서 30문항 검증과 V23 원장 재생성 및 **검토 브랜치로만 원장 커밋**).
- 산출물: `review-artifacts/NOMUSA_V24_30_TRANSCRIPTION_AUDIT.json` 및 `.md`, `NOMUSA_V24_V23_SHA_DIFF.json`, 갱신된 `review/NOMUSA_V23_VALIDATION_LEDGER.json`.

## 다음 사람 검수 단계
1. 원본 PNG/PDF와 30개 `sourceText`를 **글자별·문단별로 독립 교열**한다. 이미지와 OCR 차이, 숫자·수식·영문 용어, 한글 띄어쓰기와 인쇄 구두점을 별도 검토한다.
2. HIGH/MEDIUM 자동 일치 등급은 독립 교열 승인과 무관하다. MEDIUM 3건은 집중 검토한다.
3. 원문 교정이 필요할 때 문항 ID, 점수, 상세/압축 답안, 저장키 불변; sourceText 변경으로 SHA256 바뀌므로 재검증 후 새 문항별 승인 대상 해시로 고정한다.
4. 내용·해설의 학술/법리 원전 및 실제 필기분량/전문가 서면승인은 별도 관문. 신원·자격·검토일·근거 확인 전 0/328 유지.

## 재현 명령
```bash
python scripts/nomusa-v24-verbatim-check.py --self-test
python scripts/nomusa-v24-browser-overlay-smoke.py .
python scripts/nomusa-canonical-shared-browser-gate.py .
python scripts/nomusa-v24-verbatim-check.py .
python scripts/nomusa-v23-validation-ledger.py .
```
전체 재현을 위해 Playwright==1.56.0, PyMuPDF==1.26.7, olefile==0.47, cryptography==44.0.0, sympy==1.13.3이 필요하다. 반드시 검토 브랜치에만 남기고 배포하지 않는다.

## 오류에서 배운 재현 조건
- 2018·2021년 요지표시는 2015~2017년과 다르므로 preflight의 요지 감지 정규식은 `scripts/nomusa-v23-validation-ledger.py`의 본문 판정과 맞추어야 한다. 이전 두 Actions 실패 44097033642·44097487905를 수정하고 44097717695 PASS.
- 2018·2021년 스크립트 적용 전에 30개 **전부** 원장 사전검사를 통과해야 원자적으로 30개를 변경한다. 사전검사 실패 시 변경 0, HOLD.
- Q-Net PDF 파일 해시 동일과 수험생 웹앱에 표시한 전사 문구의 글자별 정확도는 다른 검증 축이므로 동일한 PASS라고 표기 금지.

---
name: nomusa-v25-three-medium-pdf-proofread
description: "공인노무사 2차 V24 후속으로 2016 경영조직론 및 2019·2020 민사소송법의 공식 PDF 전사 MEDIUM 3개를 원본 이미지로 재확인하고 두 OCR·머리말 오류만 수정하며 328개 회귀검증을 수행하는 재사용 Claude Code 스킬."
---

# NOMUSA V25 — MEDIUM 3개 공식 PDF 원전 시각 교차대조

## 실행지시
"기존 review/NOMUSA_V25_MEDIUM_3_PRIMARY_PAGE_CROSSCHECK_20261118.json과 .claude/skills/nomusa-v25-three-medium-pdf-proofread/SKILL.md를 읽고 3개 MEDIUM 원문 검증을 재현하라."

## 절대 불변
- 저장소: `nurioni4188/gongin-nomusa-quiz`; 브랜치 `review/nomusa-auto-v1-20year-gate-20261115`; Draft PR #3.
- 기존 20개년 328개 원고, IDs, 인사/조직 V24 30개, 상세·압축 답안, 수험생 저장키 보존.
- GitHub main, Vercel Production/Preview, RC27/RC35, 원본 PDF/HWP, 이메일 발송, PR 병합 금지.
- AI PDF 페이지 육안 대조는 독립 전문가 심사·공식 글자별 교열의 대체가 아니다. FINAL_APPROVAL=HOLD(0/328).

## 3개 원본 PDF 시각 대조 결론 (2026-11-18)
1. `2016_p5_q2` 경영조직론 25점, `source_pdf/2016/2016_second_full_original.pdf` p.7.
   - 원문: **"2. 조직관리에서 학습의 중요성, 학습과정 그리고 학습의 주요 원리로서의 강화에 대하여 각각 설명하시오. (25점)"**
   - 기존 V24 표시 원고가 인쇄면과 일치한다. 과거 Tesseract OCR은 ‘그리고’를 ‘그러고’로 오독 → sourceText 수정 불필요, OCR 일치율 0.80 자체는 기출 인쇄 오류가 아니다.
2. `2019_p4_q3` 민사소송법 25점, `source_pdf/2019/2019_p4_civil_procedure.pdf` p.1.
   - 인쇄: **"【문제 3】 공동소송참가에 관하여 설명하시오. (25점)"**
   - 기존 전사는 `공동소송참가에관하여설명하시오`처럼 띄어쓰기·문제번호가 사라지고 시험지 하단 footer까지 포함. sourceText만 원전 인쇄 형식으로 교체.
3. `2020_p7_q3` 민사소송법 25점, `source_pdf/2020/2020_p7_civil_procedure.pdf` p.1.
   - 인쇄: **"【문제 3】 유사필수적 공동소송에 관하여 설명하시오. (25점)"**
   - 기존 전사의 띄어쓰기·문제번호·하단 footer 혼입만 교정.
- 정확한 PDF SHA256, Q-Net 게시물 URL, 확인 등급은 `review/NOMUSA_V25_MEDIUM_3_PRIMARY_PAGE_CROSSCHECK_20261118.json`에서 확인한다.
- 원본 이미지: `scripts/nomusa-v25-medium-source-images.py`, Actions [44159068617](https://github.com/nurioni4188/gongin-nomusa-quiz/actions/runs/44159068617)와 artifact `nomusa-v25-three-medium-source-pdf-pages`. PNG 3문항 원전 확인용.
- **독립 교열이 끝났다고 주장하지 말 것**. 원본 PDF 이미지와 대조한 AI 사전검토는 시각 대조 후보(PASS_AI_VISUAL), 법리·학술 전문가 승인은 HOLD.

## 반영 및 검증
- `second/nomusa-v25-apply-medium-source-3.js`: V24 gate PASS 전제, 3개 대상 ID·연도·과목·25점 점검. 2016 원문은 변경하지 않고 2019·2020 두 문항만 교체, 이전 원문 `sourceTextBeforeV25` 보존.
- `second/index.html` 및 `study-hub/index.html`: 동일 순서로 V24 다음 V25 원문 오버레이 적용.
- `scripts/nomusa-v25-browser-source-smoke.py`: 양 페이지 3대상 원문/2016 보존·2019·2020 변경/328 전체 캐논/저장키 안전확인.
- `scripts/nomusa-canonical-shared-browser-gate.py`: Chromium PC1440/모바일390/360 실제 저장·복원 전체 E2E.
- `scripts/nomusa-v25-medium-source-gate.py`: 기존 V23 328개 해시를 기준으로, 2019_p4_q3·2020_p7_q3 **두 개만 변경**, 나머지 326개 SHA 그대로, 2016 원문 동일, 배점/과목/ID/공식 원본 그대로, 전문가 0으로 검사.
- `scripts/nomusa-v23-validation-ledger.py`: 최신 sourceText에 맞춰 기존 V23 검증원장을 재생성. V23 원전 동일 328/328·요지문항 0 유지, OCR 텍스트 기계적 겹침률을 별개로 기록.
- 워크플로: `.github/workflows/nomusa-v25-medium-source-gate.yml` (ubuntu-24.04, 검토 브랜치에만 V23 ledger 변경 사항 커밋).
- 기존 V24 전용 마이그레이션 워크플로 `.github/workflows/nomusa-v24-verbatim-30-gate.yml`은 **기완료 결과의 일회성 30개 이동 점검이므로 workflow_dispatch 전용으로 전환**. V25 재검증 워크플로는 자동 push / 수동 실행을 지원함.

## 판정규칙
- PASS_SOURCE_PROOFREAD_AI_VISUAL: 이미지에서 3개 인쇄 문장 대조; 2019·2020 sourceText 교체 확인.
- PASS_TECHNICAL: 328 전체 점수·문항ID·저장키·원본파일/본문SHA 안전검증, 실제 PC/모바일 Chromium E2E.
- HOLD_HUMAN_CHARACTER_PROOFREAD: 독립 교열 담당자가 직접 원본과 한 글자씩 대조한 기록 없음.
- HOLD_LEGAL_ACADEMIC: 답안 내용 자체 법령·판례·학술원전 검증·실측분량 미완료.
- HOLD_EXPERT_APPROVAL: **0/328**, 구체적 독립 전문가 자격·신원·검토일·서면근거 미확보.
- 임의로 HIGH/MEDIUM 수치를 조정하거나 이미 존재하는 판례 3건/학술 검토 HOLD를 자동 해제하지 않는다.
- 작업 후 GitHub Actions 결과 링크, commit SHA, 실제 실행시간, artifact 이름, 오류 수정 이력, 다음 검토 대상과 V23 원장 최신 SHA를 문서로 기록한다.

## 재현
```bash
python scripts/nomusa-v25-medium-source-gate.py --self-test
python scripts/nomusa-v25-browser-source-smoke.py .
python scripts/nomusa-canonical-shared-browser-gate.py .
python scripts/nomusa-essay-approval-v21.py .
python scripts/nomusa-v25-medium-source-gate.py .
python scripts/nomusa-v23-validation-ledger.py .
```

**주의:** V25 사전검증은 이미 교정된 최신 ledger SHA를 기준으로 재실행하면 2개 SHA 변화가 0으로 나올 수 있다. 이 경우 이전 V24 기준원장/Actions 증빙과의 diff를 별도로 사용해야 하며, 미변경이라고 오류 주장하거나 새 답안 수정으로 건수를 맞추지 않는다.

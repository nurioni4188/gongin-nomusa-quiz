---
name: nomusa-v25-primary-source-proofread
description: "V24 이후 공식 원본 이미지와 30개 전사문을 대조하고, V23 HIGH/MEDIUM 자동 겹침률과 실제 원전의 차이를 구분하는 검토 전용 스킬."
---

# NOMUSA V25 — PDF 원문 교열과 자동 일치도 검증

## 현재 확인한 사실 (2026-11-18)
- `2016_p5_q2`: 2016년 공식 경영조직론 PDF 7쪽 원본 이미지와 V24 sourceText의 문장·25점 배점이 일치. **AI 시각 대조 PASS**, 독립 제3자 교열 및 최종 내용승인 HOLD.
- 원본 이미지 증빙: V24 GitHub Actions run `44094781250`, artifact `14332204049`, `2016_second_full_original__page07.png`.
- V24 328개 원장 ZIP의 실제 JSON을 기준으로 `matchBand`와 `questionTextOverlap`의 임계값 HIGH≥0.85, MEDIUM≥0.5, LOW<0.5 간 불일치 **0/328**.
- MEDIUM 3개: `2016_p5_q2`(0.8000), `2019_p4_q3`(0.7826), `2020_p7_q3`(0.8077).
- V25 검토기록: `review/NOMUSA_V25_MEDIUM_SOURCE_VISUAL_PROOFREAD_20261118.md`.

## 다음 순서
1. 공식 PDF와 V24 30개 원문 전사문을 글자·배점·수식·문장부호별로 확인. 2016_p5_q2는 확인된 이미지 문구를 재사용하고 불필요한 본문 수정을 하지 않는다.
2. `2019_p4_q3`, `2020_p7_q3`의 원본 PDF 텍스트층과 현재 sourceText의 불일치 위치를 찾아 검토표에 기록. 자동 겹침률만으로 오기라고 단정하지 않는다.
3. 실제 오류가 발견된 문항의 `sourceText`만 검토 브랜치에서 수정. 기존 328개 ID·저장키·배점·상세/압축답안·공식 PDF/HWP 파일 불변, 새 SHA 및 Chromium PC/모바일 E2E 재검증.
4. `SOURCE_TEXT_AI_VISUAL_PASS`와 `INDEPENDENT_HUMAN_PROOFREAD_APPROVED`, `FINAL_CONTENT_APPROVED`는 각각 별도 필드. 인간의 독립 교열과 전문가 서면 승인 없이 뒤 두 값은 HOLD.
5. GitHub main, Vercel Production/Preview, Draft PR 병합 금지. 기존 스킬 `.claude/skills/nomusa-v24-verbatim-source/SKILL.md`를 기반으로 반복.

## 기록상 주의
- 원본 PDF SHA 일치가 앱 문항 전사 정확도를 보증하지 않는다.
- 공식 기출의 시대적 표기(예: 2021년 '1971년 올슨')를 최신 학술 설명으로 덮어쓰지 않는다.
- GitHub API 결과에서 특정 overlap 값이 의심될 경우, V24 Actions 산출물 `review/NOMUSA_V23_VALIDATION_LEDGER.json` 원본을 직접 열어 재계산한다.

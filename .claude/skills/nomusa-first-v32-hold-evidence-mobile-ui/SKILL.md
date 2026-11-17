---
name: nomusa-first-v32-hold-evidence-mobile-ui
description: "공인노무사 1차 기존 정답검증 HOLD의 원전·정답·채점 단계를 구분하고 모바일 중복표시를 개선하는 프로젝트 스킬"
---

# NOMUSA FIRST V32 — 1차 HOLD 증거 수준과 중복 UI 정리

## 원칙
- 기존 GitHub 검토 브랜치 `review/nomusa-auto-v1-20year-gate-20261115`, Draft PR #3에서만 수행한다.
- `main`·Production·기존 Preview·원본 문제·정답·ID·학습 저장키 `nomu1-progress-v2`는 변경하지 않는다.
- 2008~2021년 등록 문제풀이 1,259건, 별도 과거 정답 후보 3,400건, 공식 Q-Net PDF 연결 900건은 **서로 다른 단위**이다.
- 2022~2026년 RC35의 1,020문항 채점·저장·복원은 종전대로 유지한다. 2008~2021년 자동채점은 계속 금지한다.

## 재활용 출처·검증의 정확한 단계
- `review/NOMUSA_FIRST_V61_ANSWER_AUDIT_20261115.json`: 3,400건 정답 후보·전건 승인 대기. Q-Net PDF 연결 900건 중 텍스트층 300, OCR 위치 후보 556, 미확정 페이지 44.
- `review/NOMUSA_FIRST_V62_SCAN_RECHECK_20261115.json`: 3개 원본 이미지 위치 확인과 2020~2021 정답표 600셀 분석 기록.
- `review/NOMUSA_FIRST_V70_QNET_44_PAGE_OCR_AND_ANSWERS_20261115.json`: 미확정 페이지 44개(후속 검증 여부 별도 구분). OCR 후보를 확정으로 바꾸지 않는다.
- `review/NOMUSA_FIRST_V71_14_VISUAL_PAGES_600_ANSWERS_20261115.json`: PDF 문항번호 14건 이미지 확인, 2020~2021 정답표 600셀 자동비교, 특수셀 4건 시각대조. 독립 사람의 서명·정답 승인 0건.
- `review/NOMUSA_FIRST_V71_OFFICIAL_QNET_14PAGE_600CELL_FINAL_GATE_20261115.json`: 인쇄 페이지·전체 지문·수식의 전수 교열 및 공식 채점승인은 HOLD.

## V32 화면 변경
- `study-hub/first-v32-proof-status.js`: 900건 개별 PDF 근거 단계와 600개 정답표 자동대조 수준을 실제 해당 원장 및 V62/V71 ID에 연결한다. 모든 `scoringApproved:false`.
- `study-hub/first-legacy-answers.html`: 3,400건 정답 검토 테이블의 반복적 HOLD 셀을 원문/정답 이미지 증거 단계로 변경하고 모바일 카드형·접을 수 있는 설명 제공.
- `study-hub/index.html`·`study-hub/app.js`: 별도 반복 안내 배너 제거, 하나의 검토 페이지 링크 유지.
- `index.html`: 연도별 반복 HOLD 타일을 채점 전 `선택` 기록으로, 문제풀이의 중복 HOLD 메시지를 하나로 조정. 검증정보 링크 제공.
- **원본의 제한된 확인 사실을 전체 정답승인으로 표현하지 않는다.**

## 자동검증
```bash
python scripts/nomusa-first-v32-status-ui-gate.py
python scripts/nomusa-first-v71-visual-page-gate.py
python scripts/nomusa-first-v6-fullhub-gate.py .
```
- 1440/390/360px에서 900건 상태, 600셀 대조, V62 3/V71 14, 특수셀 4, PDF 연결과 1차 채점 차단을 테스트.
- 2008년 선택 전 안내와 선택 후 HOLD 메시지가 중복되지 않고 `fb.info`가 1개인지 확인한다.
- 독립 검수 서면승인 또는 시험일별 정확성 증빙이 없는 항목에 자동으로 채점 승인 부여 금지.
- 모든 자동검증 PASS 이후에만 기존 Vercel 프로젝트에 **새 Preview 1회**, `main`·Production과 이전 Preview URL 보존.

## 다음 실질 검토
- 기존 44개 페이지 HOLD 중 3+14 제한적 시각확인을 재활용하고 나머지의 원문 지문·선택지·수식·인쇄쪽수를 공식 PDF 이미지로 대조.
- 2020·2021년 정답표 600개는 기계적 비교와 일부 예외시각대조만 완료. 정답 승인 0건 유지.
- 검토가 끝난 문항만 개별 서면 근거/원문 해시/검토자 확인과 연결한 후 채점 승인을 별도 결정.

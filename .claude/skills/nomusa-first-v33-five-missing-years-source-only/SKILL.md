---
name: nomusa-first-v33-five-missing-years-source-only
description: "공인노무사 1차 학습앱 2008~2021 수록 누락 5개 연도 2013/2016/2018/2020/2021의 실제 구기출 정답 후보 1500건을 원본 기반으로 재연결하고 검증한다. 미검증 문제 본문 생성이나 자동채점 허용을 금지한다."
---

# NOMUSA FIRST V33 — 1차 빠진 연도 재연결

## 범위·안전
- 기존 저장소 검토 브랜치 `review/nomusa-auto-v1-20year-gate-20261115`, Draft PR #3만 사용한다. `main`, Production, RC27·RC35 기존 Preview, 문제 ID/저장키/원본 Q-Net 파일은 변경하지 않는다.
- 2008~2021 문제은행에 반영된 문제는 9개 연도 1,259문항, 기존 2022~2026 문제 1,020문항(총 2,279문항).
- 누락된 **2013, 2016, 2018, 2020, 2021**은 해당 연도 실제 문제지의 지문·선택지까지 학습앱에 구축된 것이 아니다. 각 연도 **A형 150 + B형 150 = 300개** 기존 정답 *후보*만 확인됐다. 총 1,500개 정답 후보는 기존 3,400 원장의 부분집합이며 학습앱 문항 수에 더하지 않는다.
- 2020/2021은 V61·V69·V70·V71의 Q-Net 공식 문제지/정답표 링크, PDF SHA, 일부 원본 페이지 이미지 대조를 재사용. **정답 600개 셀 이미지 대조와 내용 독립 승인/전체 문제 지문 전사 완료는 별개**.
- 2013은 정답 후보 A/B, 2016은 문제지 파일명 힌트, 2018은 ZIP 파일명 힌트가 있으나 원본 지문·쪽수의 원장 연결은 미완료. 원문에 없는 지문/보기/문제는 절대 생성하지 않는다.
- 부분누락 **2010 25, 2011 1, 2012 1, 2017 6, 2019 8 = 총 41문항(A형 기준)**. 기존 정답 후보만으로 QDATA 문항을 생성하지 않는다.
- 미승인 과거 정답 3,400건 자동채점·오답판정·정답강조 금지, 기존 RC35 1,020문항 채점 유지.

## 기존 실질 자료
- `review/NOMUSA_FIRST_V66_BATCH.json`: 연도별 A형 편입, OCR·수식·인쇄레이아웃 보류.
- `review/NOMUSA_FIRST_V67_HUB_ENTRANCE_GATE_20261115.json`: 누락 5개 연도 및 부분 문항별 실제 수.
- `review/NOMUSA_FIRST_V61_ANSWER_AUDIT_20261115.json`: 정답 후보 3,400건 (A/B).
- `review/NOMUSA_FIRST_V71_OFFICIAL_QNET_14PAGE_600CELL_FINAL_GATE_20261115.json`: 2020/2021 공식 PDF·정답표 시각대조 범위.
- `study-hub/legacy-first-v2-staged.js`, `study-hub/legacy-first-v4-2014-2021-review.js`, `study-hub/legacy-first-v5-correction.js`: 이전 실제 후보 정답/특수 다답 기록.
- `study-hub/legacy-first-v61-sources.js`: 2020/2021 A/B 문제지·정답표 원문 다운로드 및 레코드 링크.

## 반영된 1차 화면
- `study-hub/first-v33-missing-year-coverage.js`: 5개 누락연도, 연도별 A/B 300건, 부분누락 41개와 **실제 문제은행 수 0** 구분.
- `index.html`: 1차 문제풀이 설정의 연도 아래 '문제 지문 미편입 · 기존 정답 후보 자료'로 5개 연도 링크 추가. 기존 1차 실제 문항 QDATA, ID, 저장키, 점수 함수 무변경.
- `study-hub/app.js`·`study-hub/index.html`: 통합 허브 2008~2026 연도 현황에서 누락 5개를 읽기용 정답 후보 링크로 열람, 부분누락은 편입 대기 수 표기.
- `study-hub/first-legacy-answers.html`: `?year=2013&type=A` 또는 B형 딥링크, 보존된 150개 정답 후보, 2020/21 공식 Q-Net PDF 다운로드 링크; 2016/18 미연결 파일명은 참고로만 표기.
- 계층 구분: **정답 후보 조회 가능** ≠ **문제지 지문 화면 편입** ≠ **최종 내용·채점 승인**.

## 자동검증
```bash
node scripts/nomusa-first-v33-existing-source-gap-gate.mjs .
python scripts/nomusa-first-v33-missing-year-browser-gate.py .
python scripts/nomusa-first-v32-status-ui-gate.py
python scripts/nomusa-first-v71-visual-page-gate.py
python scripts/nomusa-auto-v12-browser-gate.py . --first-only
python scripts/nomusa-canonical-shared-browser-gate.py .
```
- V33: 실 데이터 2,279 문항·3,400 정답 후보, 누락연도 실제 문제 0/후보 1,500, ID 충돌 0.
- PC 1440/Mobile 390/360에서 5개 연도 A형 150건 직접 조회, 2021 B형 150건, 통합 허브 링크·수평넘침·원본근거·기존 학습 보존 검증.
- V32 안전표시 17개, V71 공식 PDF 42개, RC35 1차 6개 및 최신 canonical 2차 회귀검증 모두 통과해야 Preview 배포 후보.
- 주의: CI나 Q-Net 문서 링크가 과거 후보 정답을 승인한 것이 아니며, 로그인된 원격 보호 Preview 실사용은 별도.

## 이후 실질 문제풀이 확장을 위한 순서
1. 2020·2021 공식 PDF의 실제 문제지 원문·선택지·그림을 각 125~150개 A형 문항 ID별로 직접 연결·전수 대조(압축·이미지·쪽수 검증).
2. 2016·2018 과거 문제지 원본 파일을 확보하여 실제 책형과 지문 구조 검증. 2013 공식 원본 문제지를 새로 확보해야 한다.
3. 2010·2011·2012·2017·2019 부분 누락 41개 원문·선택지·수식 검증 후에만 QDATA 편입.
4. 정답 자동채점 승인은 독립 내용검토가 별도로 끝난 문항만 승인·통합 가능.

### 프로젝트 스킬 안내
저장소의 `.claude/skills/` 아래에 생성된 Claude Code 프로젝트 스킬이며, 사용자 계정 전체에 자동 설치되지 않는다.

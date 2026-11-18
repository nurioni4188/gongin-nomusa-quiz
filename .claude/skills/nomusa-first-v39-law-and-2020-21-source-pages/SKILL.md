---
name: nomusa-first-v39-law-and-2020-21-source-pages
description: "공인노무사 2026 사회보험법 40개 해설의 시험일 법령 조문·부칙 정확성을 심사하고, 2020·2021 A형 300개 기존 정답후보에 Q-Net 공식 88개 원본 페이지 이미지를 연결하여 274개 위치 후보만 미채점 연습하도록 안전하게 확장하는 프로젝트 스킬"
---

# NOMUSA V38/V39 — 2026 법령 및 2020·2021 원본 연습

**작업원칙**: 기존 GitHub `nurioni4188/gongin-nomusa-quiz` 검토 브랜치 `review/nomusa-auto-v1-20year-gate-20261115`, Draft PR #3만 수정. main·Production·기존 Preview·1차 RC35 1,020개·2차 328개 원문·저장키 변경 금지.

### 2026 사회보험법 37개 해설 검사
- `explanations-2026-social-v36.js`는 기존 3개(41·46·60) 보존, 나머지 37개 정확한 2026 원문·정답·5개 선택지로 연결. 수정은 해설 원장만, 정답 키 불변.
- **43번** 위탁기관 `사회보장기본법 제44조 제2항` (시행령 제16조의2 아님).
- **63번** 건강손상자녀 직업재활급여 `산업재해보상보험법 제36조 제1항 단서` (제91조의12는 업무상 재해 인정 기준).
- **68번** 2027-01-01 출산크레딧 개정은 2026-05-23 문제 풀이에 소급 금지.
- **72번** 1500만원 **또는** 20%로서 하나만 충족해도 공표대상 규정. 시험후 2026-05-26 개정은 소급금지.
- 42/47/50/55/58/65의 공식 규범과 기존 해설을 대조·갱신. **10개 조문 검증과 37개 전체 독립승인은 다르다**. 독립 승인 0 / 2026-05-23 시험일 법령 원문·부칙·선택지별 완결 검사 HOLD 유지.

### 2020·2021 A형 300개 원본 페이지 학습
- `study-hub/legacy-first-v61-sources.js` 원본 Q-Net 공식 PDF SHA 4개 + 각 시험지 쪽수. `scripts/nomusa-first-v38-2020-2021-native-page-source.py`로 4개 원본 파일 다운로드하고 SHA·파일형식·쪽수 검증, **274개 OCR 후보 위치가 가리키는 88쪽만 중복 없이 JPEG 이미지 생성**.
- `study-hub/first-v38-2020-2021-source-pages-practice.html`와 `study-hub/first-v38-2020-2021-source-pages-app.js`: 2020/21 150개씩 300개 후보 조회, 274개 추정페이지 이미지 보기+자체 1~5 선택 저장, 26개 위치HOLD는 선택 버튼 비활성, 정답후보 명시적 열람, 복습표시·JSON 백업. 메인 QDATA 미편입/채점 금지.
- 연습의 페이지 위치는 OCR로 **자동 추정**된 것이며 개별 지문/수식/선택지 시각 검증의 증빙이 아님. 274를 274개 정식 문제 등록/정답 최종 승인이라고 말하지 말 것.
- `review/NOMUSA_FIRST_V38_88_NATIVE_PAGE_SOURCE_20261118.json`에서 각 원본 PDF SHA·렌더 JPG SHA·26개 미확정 ID 검토. 페이지 편입은 사람이 실제 문항번호를 확인한 뒤 개별 이미지로 분리하는 것이 다음 단계.

### 빠른 검증
```bash
node scripts/nomusa-first-v34-791-original-source-queue.mjs .
python scripts/nomusa-first-v38-2020-2021-native-page-source.py
python scripts/nomusa-first-v38-300-page-practice-browser-gate.py .
python scripts/nomusa-first-v36-social-40-browser-gate.py .
python scripts/nomusa-first-v37-14-image-practice-gate.py .
python scripts/nomusa-first-v32-status-ui-gate.py
python scripts/nomusa-canonical-shared-browser-gate.py .
```
- GitHub Actions V38 #44228950899 PASS, 페이지 4/SHA·88/JPEG·18/브라우저 E2E, 기존 1차·2차 복원 PASS.
- 사이트 변경은 검토 브랜치만·보호 Preview 배포만. main/Production 절대 손대지 않음.

### 이후 우선순위
- 274개 OCR 페이지 위치를 원본 PDF 문항 번호로 직접 검증해 단일문항 이미지(보기·그림 포함)로 자른 뒤 별도 상태로 승격; 26개 위치 HOLD 원본 수동대조.
- 2013·2016·2018년 공식 A형 문제지의 각 기출 원문·보기 구조 확보, 누락 2010·2011·2012 부분 원문 완성.
- 2026 사회보험법 37개 시험당시 조문·부칙/행정해석/판례 선택지별 정확성 독립검토 후 승인받기.

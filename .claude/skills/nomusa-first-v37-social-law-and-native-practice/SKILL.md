---
name: nomusa-first-v37-social-law-and-native-practice
description: "공인노무사 1차 2026 사회보험법 해설 누락 37개를 원문·정답 기준으로 복원하고 2017·2019년 Q-Net 원본 이미지 14문항을 안전한 미채점 연습 화면으로 제공하며 1차·2차 회귀검증하는 Claude Code 프로젝트 스킬."
---

# 1차 2026 사회보험법 40문항 및 원본 이미지 14문항: V36·V37

## 대상 및 변경 불가 원칙
- 저장소 `nurioni4188/gongin-nomusa-quiz`의 검토 브랜치 `review/nomusa-auto-v1-20year-gate-20261115`, 기존 Draft PR #3 사용.
- `main`, Production, 기존 Preview, RC35 1차 `data.js`/정답/문항 ID/저장키, 2차 328답안 미변경.
- 이전 2008~2021년 정답 후보 3,400개는 승인 0이며 **채점 금지**. 원본 이미지에서 답을 선택하는 기능과 공식 정답·오답 채점은 다르다.

## 2026 사회보험법 누락 원인
- `data.js`의 2026 사회보험법은 41~80번 총 **40문항 전부 문제·보기·정답 있음**.
- `explanations-v108.js`에 41·46·60번 3건만 존재했고, 나머지 **37건은 미등록**. 기존 3건은 정답과 5개 보기가 정확히 일치해 화면 연결 정상.
- `explanations-2026-social-v36.js`는 없는 37건만 추가. 원문 `q`, 정답 `a`, 보기 `o`와 각각 완전 일치해야만 `index.html`에서 해설 표시.
- 각 추가 초안: 핵심 법리·5개 선택지별 이유·관련 법령명/조문 주제·국가법령정보센터 출처·암기어. `validationStatus=LEGAL_EXAM_DATE_REVIEW_HOLD`, 독립 최종 승인 0. 법령 링크가 시험일자 시행본 조문/부칙을 완전히 검증한다는 의미 아님.

## 2017·2019 공식 원본이미지 선택연습
- Q-Net PDF 실제 SHA/문항번호로 잘라낸 JPG 검토자료 14건(2017년 6, 2019년 8)을 `review/NOMUSA_FIRST_V35_14_NATIVE_QNET_SOURCE_PROOF_20261118.json`에서 복원.
- `study-hub/first-v37-native14-practice.html`: 원본 JPEG 보면서 ①~⑤ 선택, 2017/2019 필터, 이전·다음 이동, 별도 로컬 자동저장·새로고침 복원, 복습 표시, JSON 내보내기, 후보답안 펼치기.
- 저장키 `nomusa1-v37-native14-choice-review-v1` 별도 사용. 기존 주 학습앱 `QDATA`에는 14건을 임의 편입하지 않음. 기존 1차 2,279 실제 문항수 그대로. 정답 후보에 따른 자동채점·정오표시 없음.
- 791개 미편입 A형 중 14개만 별도 **원본 이미지 선택 연습 가능**, 나머지는 여전히 본문·선택지 검증 대기. 791개 완성으로 표시 금지.

## 자동검증
```sh
python scripts/nomusa-first-v36-social-40-browser-gate.py .
python scripts/nomusa-first-v37-14-image-practice-gate.py .
node scripts/nomusa-first-v34-791-original-source-queue.mjs .
python scripts/nomusa-first-v32-status-ui-gate.py
python scripts/nomusa-canonical-shared-browser-gate.py .
```
- GitHub Actions `NOMUSA FIRST V37 original image 14 questions ungraded practice and 2026 SI`에서 PC1440 / 모바일 390·360, 2026 사회보험법 40/40 해설, 실제 이미지 14, 로컬 저장·복원, 후보답안 미채점, 기존 RC35·2차 328 답안 회귀검증 PASS.
- CI/Preview 빌드 PASS는 법령·판례 내용의 최종 독립 승인 아님.
- 검증 성공 후 기존 Vercel 프로젝트의 **별도 보호 Preview만** 배포. `main`/Production 보존.

## 후속 실질 과제
- 2026 사회보험법 각 37건의 **2026-05-23 시행법령 원문·부칙·시행령·시행규칙과 법리 정확성**을 직접 독립 대조하고 잘못된 문장만 최소 수정.
- 2017·2019 원본 이미지 14건의 전체 지문/그림/선택지 완전 교열 후 승인 가능한 것부터 1차 문제은행에 편입.
- 2013·2016·2018·2020·2021 원본문제 스캔형은 Q-Net 실제 PDF와 각 문항 페이지·5개 선택지·공식 정답 일대일 확인. OCR만으로 확정 또는 자동채점 승인 금지.
- 과거 미편입 791문항의 기술상 문항 ID와 내용 검증 단계를 별도 관리, 0건 승인과 구분.

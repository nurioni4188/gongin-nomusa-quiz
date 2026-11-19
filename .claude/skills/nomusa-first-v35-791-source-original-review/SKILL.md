---
name: nomusa-first-v35-791-source-original-review
description: "공인노무사 1차 791개 미편입 A형 원문을 Q-Net 원전 SHA, 문항 원본 이미지, 선택지·수식 검증 단계별로 복원하는 보수적 재사용 스킬. 미검증 채점·가짜 지문 금지."
---

# NOMUSA FIRST — 791개 누락 A형 문항 원본 복원·개별검증

## 절대 원칙
- GitHub `nurioni4188/gongin-nomusa-quiz` 기존 검토 브랜치 `review/nomusa-auto-v1-20year-gate-20261115`만 변경. Draft PR #3 미병합. `main`/Production/RC35 저장키/문항 ID/2022~2026 1,020문항/2차 328답안 원본 불변.
- 2013·2016·2018·2020·2021년 각 150개 A형 총 750 + 2010(25)·2011(1)·2012(1)·2017(6)·2019(8) 총 41 = **791개**. 기존 2,279문항 QDATA와 겹치지 않는 실제 기존 정답 후보 ID 기준.
- 3400개의 A/B형 과거 정답은 **미승인 후보**이며 실제 원문 791개나 자동채점 승인 숫자로 잘못 더하지 않는다.
- 공식 PDF/SHA가 확인된 것, 문항번호·문항 위치가 확인된 것, 5개 선택지·도식·수식 전체가 보이는 것, 독립 전문가가 원문/정답을 승인한 것을 **각기 다른 단계**로 둔다.
- 미확인 Q-Net 문제지 또는 스캔된 문제에 지문·선택지·수식·정답을 추측·자동생성하여 문제은행에 추가하지 않는다.

## 실제 재활용 원전
- `review/NOMUSA_FIRST_V66_BATCH.json`, `review/NOMUSA_FIRST_V61_ANSWER_AUDIT_20261115.json`, V69~V71 공식 Q-Net 페이지 근거.
- `study-hub/legacy-first-v61-sources.js`는 2020/2021 A/B 공식 문제지 SHA 연결 600건. 새로 6종(2020/21 A 경영/경제, B 경영)을 재다운로드해 **6종 동일 SHA/텍스트층 0** 확인. 이 스캔은 무검증 자동 텍스트 전사 금지.
- 2016 공식 경제학 A PDF QNet 2162962: 이미지 스캔; 2018 QNet ZIP 2186568/2186569: 4개 A/B PDF 스캔.
- 2017 QNet 2182807 ZIP은 A/B 경영·경제 4개 PDF의 텍스트층 존재, 2019 QNet 2190603/2190604 PDF는 텍스트층 존재. 원본 source SHA는 V34 실행 로그/증빙에 기록.

## 재현·진행
```bash
node scripts/nomusa-first-v34-791-original-source-queue.mjs .
python scripts/nomusa-first-v34-official-source-probe.py
python scripts/nomusa-first-v34-qnet-2016-2019-source-structure.py
python scripts/nomusa-first-v35-qnet-native-original-14.py
```
- 원본 텍스트층이 있는 2017/2019의 기존 미편입 14개는 Q-Net PDF 다운로드 SHA 일치, 공식 A형/문항번호 125개 연속, 원본 해당 문항 시작좌표, 원본 JPEG 해시·픽셀 크기를 확인하여 **원문 이미지 검토 페이지로만** 먼저 분리한다. 원래 PDF 내용 외 인위적인 선택지 생성 없음.
- 원본 이미지 영역 시각검사 결과가 전문가 승인 대용이 아니다. 수식·도표·선택지 독립 검증 및 클릭 학습 UI 품질 검증 후에만 별도 승인 단계로 문제은행에 넣는다.
- 2016/2018/2020/2021 스캔형은 공식 PDF 파일과 원본 후보 페이지 링크를 제공하되, 0개가 승인됐다면 그대로 0개로 기록한다. OCR 후보를 사람의 독립 원전 대조로 승격하면 안 된다.
- `study-hub/first-legacy-answers.html`의 공식 Q-Net 원문 페이지 링크는 자동 OCR 후보일 수 있으므로 `PDF n쪽 · 자동 판독 후보`와 명시한다. 2016/2018은 공식 게시물 링크만 검증, 문항별 원문 확인을 의미하지 않는다.
- Preview 배포 전 PC 1440/Mobile 390/360, 선택 저장/복원, 2차 canonical SHA, 1차 미승인 자동채점 차단 검증 PASS. Production은 건드리지 않는다.

## 완료 판정 예시
- `PRIMARY_PDF_SHA_PASS`, `QUESTION_NUMBER_PAGE_PASS`, `NATIVE_IMAGE_CROP_REVIEW_PASS`, `EXACT_STEM_OPTIONS_FORMULAS_PASS`, `INDEPENDENT_KEY_APPROVAL`을 별도 필드로 기록.
- 검증 실패/인쇄 레이아웃 애매한 문제는 `HOLD`를 유지하고 원본 링크·사유·다음 교열 대상만 남긴다.
- GitHub Actions CI 결과는 소스·기능 기술검증이지 시험 당시 법령/정답의 독립 내용승인 아님.

기존 Claude Code 프로젝트 스킬(전체 계정에 전역 설치되지는 않음).

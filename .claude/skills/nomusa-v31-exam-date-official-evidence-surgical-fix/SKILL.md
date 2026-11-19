---
name: nomusa-v31-exam-date-official-evidence-surgical-fix
description: "공인노무사 2차 11개 집중 검토대상의 기존 작업을 재사용하면서 국가법령정보센터·대법원·공식 기출 근거 수준을 구분하고, 출처가 불명확한 2026 행정쟁송법 만인율 집행정지 날짜표기 1문장만 교정하여 328답안 SHA를 검증하는 Claude Code 재사용 스킬."
---

# NOMUSA V31 — 공식 근거 11건 점검·1문장 최소교정

## 관리 원칙
- 기존 GitHub `nurioni4188/gongin-nomusa-quiz`의 `review/nomusa-auto-v1-20year-gate-20261115`, Draft PR #3에 한정한다.
- 새 학습 허브를 만들거나 `main`/Production/기존 Preview/RC27·RC35/문제ID/점수/저장키/공식 PDF·HWP를 수정하지 않는다.
- V9~V30의 이미 작성한 학습답안을 다시 작성하지 않는다. 실제 근거가 확인된 **2026 행정쟁송법 1문장**만 V31에서 최소 교정했다.
- 학습용 내용의 최종 독립전문가 승인 **0/328 HOLD**; 화면 작동 PASS와 내용 승인 혼동 금지.

## 기존 확인된 11개 핵심 분류
- 시험 당시/이후 법령·판례 비교 7개: 2007 노Ⅱ, 2009 노Ⅱ·노Ⅰ, 2012 노Ⅰ, 2013 노Ⅰ, 2020 행정쟁송, 2022 노Ⅰ. 기존의 `시험 후 참고` 표시는 유지한다.
- 판례 3개: 2011두7526(한국노동연구원 연구자료 사건번호·선고일·법리 확인), 2012다81609(공식 법원 후속판결에서 원사건 인용), 2024구합76393(서울행정법원 공식 본안 판결 소개에서 처분성 인정·원고 청구기각 확인). **세 사건 모두 원판결 전문을 이번 작업에서 완독했다고 선언하지 않는다.**
- 2016_p5_q2: V25 AI PDF 페이지 시각대조로 이미 원문과 일치; OCR 오독으로 MEDIUM 유지, 독립 교열 서명만 HOLD.
- 2020 행정기본법 제36조는 **2023-03-24 시행**, 2020 시험 법리에 적용 불가(제정법 공식 시행일 확인).
- 2022 통상임금 후속 대법원 2024-12-19 전합은 시험 이후 판례로만 구분.

## 실제 최소 교정
- 문항 ID: `2026-행정쟁송법|2|0`.
- 파일: `second/nomusa-v11-admin-2024-2026.js`.
- 기존 근거 미확정 표현: `2026년 초 서울행정법원...` 한 문장을, **2025-08-12 보도로 확인되는 별도 집행정지 인용 사례**와 **2024구합76393의 본안 청구기각**을 명확히 구분하는 문장으로 교체.
- 실질 법리·포섭·결론, 다른 327개 답안, 기출문구와 저장키는 변경하지 않는다. 소급적용 오류 확정이나 전문가 최종 내용 교정이라고 표시하지 않는다.
- 근거 원장: `review/NOMUSA_V31_11_PRIMARY_SOURCE_EXAM_DATE_EVIDENCE_20261118.json`.
- 출처: 서울행정법원 2024구합76393 공식 소개 `https://www.scourt.go.kr/portal/dcboard/DcNewsViewAction.work?cbub_code=000220&gubun=44&scode_kname=&searchOption=&searchWord=&seqnum=27433`; 2025.8.12 보도 `https://www.dnews.co.kr/uhtml/view.jsp?idxno=202508121351210960459`.

## 자동 재현 순서
1. `python scripts/nomusa-v31-11-primary-evidence-one-edit-gate.py --self-test`.
2. V23 현재 기존 원장 `review/NOMUSA_V23_VALIDATION_LEDGER.json`을 별도 위치에 복제(변경 전 328개 원고 SHA 보존).
3. `python scripts/nomusa-canonical-shared-browser-gate.py .` — PC1440/Mobile390/360 표시본문 328개와 저장·복원 시험.
4. `python scripts/nomusa-v23-validation-ledger.py .` — 정확히 1문장 반영한 새 SHA로 328 원장 재생성(검토 브랜치 전용).
5. `python scripts/nomusa-v30-reuse-history-time-gate.py . --rendered` — 선행 88개 V20 보강·328개 SHA 및 2022년 19개 근거 연결을 그대로 유지.
6. `python scripts/nomusa-v31-11-primary-evidence-one-edit-gate.py . --before-ledger /tmp/v31_baseline.json` — **2026 행정쟁송법 한 ID만 원고 SHA 변경, 나머지 327개 SHA 불변, 328개 Q-Net 공식 원문/배점 및 Goldstein V28 이전 교정 불변** 검증.
7. `python scripts/nomusa-v26-substantive-review-packets.py .` — 새 원고 SHA를 반영한 7과목 328개 외부 전문가 심사 ZIP 재생성.
8. `review-artifacts/NOMUSA_V31` 결과물 JSON/CSV/MD 저장, 동일 검토 브랜치에 변경된 V23 SHA 원장만 커밋, 메인/배포 없음. GitHub Actions에서 검증 스텝이 실패하면 커밋/배포 금지.

## 검증 후에도 HOLD인 것
- 2011두7526/2012다81609/2024구합76393 각각 원 판결문 전문과 완전한 사안포섭.
- 2016_p5_q2 원문 사람의 독립 교열·서명.
- 모든 학습답안 328개 시험일별 법령 부칙/연혁 전수, 수기 장수/전문가 정답성 최종 확인.
- 자동검증 PASS는 이 HOLD의 승인이나 내용완성 선언이 아니다.

## 스킬 관련 주의
프로젝트 저장소 내부 Claude Code 스킬로서, 사용자 전체 계정에 일괄 설치되거나 다른 도구의 응답을 자동변경하지 않는다.

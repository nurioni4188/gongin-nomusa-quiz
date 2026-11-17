---
name: nomusa-v22-primary-source-expert-gate
description: "공인노무사 2차 328개 원고 원본 PDF 후보 대조, 2022년 19개 전문가 검토패킷 및 페이지 이미지 생성. 원전 진위·역사법령·학술·독립전문가 승인은 별개 HOLD."
---
# NOMUSA V22 — 원전 PDF 대조·독립전문가 심사 스킬

## 사용 지시
"V22 스킬로 V21 승인원장의 328개를 공식 기출문제 및 저장소 PDF 후보와 비교하고 2022년 19개 심사패킷을 재생성한 후 GitHub 검토 브랜치에서 자동검증하라."

이 스킬은 GitHub 저장소 내부의 재사용 지침이며 ChatGPT에 전역 설치했다고 주장하지 않는다.

## 프로젝트 범위
- Repository: nurioni4188/gongin-nomusa-quiz.
- Branch: review/nomusa-auto-v1-20year-gate-20261115. 기존 Draft PR #3.
- 2007~2026년 20개년 328개, 2022년 19문항/32소문항, V20 심화 88개, 분량 프록시 77개.
- main/Production/기존 Preview/문항 ID/저장키/RC27/RC35/기출 PDF 원본 불변. 신규 프로젝트·신규 배포·PR 병합 금지.

## 1단계 — 정확한 원전 매핑과 자료 진위
- Q-Net 2022 공인노무사 2차 공식 기출문제 게시물: https://www.q-net.or.kr/cst003.do?artlSeq=5210985&boardId=Q004&gId=05&gSite=L&id=cst00302
- 저장소 source_pdf/2022/ 이하 과목별 7개 PDF를 문항 ID/과목과 연결하고 SHA256, PDF 페이지 수, 텍스트층을 확인한다.
- PDF에서 문항과 겹치는 8글자 연속조각 비율과 가장 잘 맞는 페이지를 구한다. 이는 원전 동일성이나 수식·표·그림 검증의 확정 증거가 아니다.
- Q-Net ZIP 첨부파일의 바이너리와 저장소 PDF 파일 SHA가 실측 일치하기 전까지 OFFICIAL_IDENTITY_HOLD.
- 2022 PDF 페이지를 PNG로 렌더링해 전문가가 시각 대조하도록 제공한다.
- 2007~2012년 HWP 파일은 원래 해시 명세가 있더라도 저장소에 실제 바이너리가 없으면 SOURCE_BINARY_MISSING.
- 2021 day1/day2 원전 후보가 동시에 있을 경우 문항별 페이지 연결을 확인하기 전까지 MULTIPLE_DAY_CANDIDATES_HOLD.
- 2023~2026년 및 2013~2020년 원본 PDF 경로가 존재해도 해당 문제지의 공식 첨부와 일치한다고 자동 주장하지 않는다.

## 2단계 — 실제 브라우저 원고 무결성
- scripts/nomusa-canonical-shared-browser-gate.py: PC 1440, 모바일 390/360, 저장·복원·앱 ID·원고 표시 검사.
- scripts/nomusa-essay-quality-v19.py: 328개/배점 26개 등 기술검증.
- scripts/nomusa-essay-approval-v21.py: 승인원장·2022 19개·32소문항·77개 검토큐·본문 SHA256.
- scripts/nomusa-v22-original-expert-packets.py: V21 SHA와 최종 브라우저 원고의 일대일 일치, 328개 원본 파일 후보 라우팅, 2022년 19개 문항별 원문/상세/압축 패킷 생성.
- .github/workflows/nomusa-v22-primary-expert-packets.yml: 위 전체를 보호 검토 브랜치에서 자동 실행하고 아티팩트로 업로드.

## 3단계 — 법리·학술·수식의 최종 검증
- 노동법·행정쟁송법·민사소송법: 시험일 당시 국가법령정보센터 연혁법령·부칙, 대법원 판결서 또는 종합법률정보의 사건번호·판시 법리·선고일 원전 확인.
- 노동경제학: 기출 원문 수치와 변수·단위·목적함수·일차/이차조건·경계해·그래프를 독립 검산.
- 인사노무관리·경영조직: 학자·원전 저서·논문·발표 연도·이론의 적용 조건과 비판 확인.
- AI 간 동의, 사건번호 패턴 검출, 기출 PDF 텍스트 유사도는 전문가 승인이 아니다. 독립 원전·검토자 실명·검토일·근거가 없으면 HOLD.

## 4단계 — 전문가 심사자료 및 승인조건
- review-artifacts/NOMUSA_V22_328_SOURCE_EXPERT_ROUTING.csv: 전체 문항별 원전 PDF 후보, SHA, 검증상태.
- review-artifacts/NOMUSA_V22_328_ORIGINAL_AUDIT.json: 328개 상세 상태.
- review-artifacts/NOMUSA_V22_2022_EXPERT_PACKETS: 2022년 19개 문항별 원문·소문항·상세답안·압축답안·SHA 및 체크리스트.
- review-artifacts/NOMUSA_V22_2022_PDF_PAGE_PREVIEWS: PDF 전체 페이지 이미지.
- review-artifacts/NOMUSA_V22_ORIGINAL_COMPARE_REPORT.md: 심사 요약.
- review/NOMUSA_V21_INDEPENDENT_REVIEW_TEMPLATE.json: 독립 전문가 검토양식. 원문 PDF 해시, 시험 당시 법령·판례/학술 확인, 수기 분량과 전문 판단, 검토자 자격/실명/날짜/근거·의견 및 원고 SHA를 모두 요구.
- 수기 분량 목표 50점 8~10장, 25점 4장, 15점 3장, 10점 이하 2장. 직접 필기 실측 없으면 HOLD.
- 내용승인 0/328 상태는 실제 독립 전문가 검토자료가 들어오기 전까지 바꾸지 않는다.

## 보고 판정
- PASS_SOURCE_PACKETS: 검토용 저장소 PDF 매핑 및 2022년 심사자료 자동생성 성공.
- HOLD_OFFICIAL_IDENTITY: 공식 Q-Net ZIP과 저장소 PDF의 해시 동등성 미검증.
- HOLD_HISTORIC_AUTHORITIES: 역사 법령/판례/학술 원전 독립검증 미완료.
- HOLD_HANDWRITING / HOLD_EXPERT_APPROVAL: 실측 및 전문가 서면승인 미확보.
- HOLD_DEPLOY: 기존 Preview/Production 보존.
- 항상 GitHub Actions run, commit SHA, 아티팩트, 정확한 실행 완료 범위와 미확인 항목을 함께 보고한다.

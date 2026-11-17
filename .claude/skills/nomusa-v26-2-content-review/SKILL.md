---
name: nomusa-v26-2-content-review
description: "2022년 19개·32소문항 및 V21 분량 프록시 77개, 총 96개 공인노무사 2차 답안의 원전 근거 후보·법령 시점·판례·학술·계산 검토 대상 자동 분류. 승인/배포 없음."
---

# NOMUSA V26-2 — 96개 답안 근거 중심 내용검증 사전심사

## 목적과 범위
- 기존 20개년 328개 원고의 2022년 **19개 P0·32개 소문항**, 별도 **77개 P1 단순 글자수 프록시**를 합친 **96개**를 우선 심사한다.
- 기존 기출 원본·배점·판례번호·수식에 관한 V23 검증원장과 실제 Chromium 출력 20년치를 연결한다. 새 판례·학자·시험연도 법령을 상상하여 채우지 않는다.
- **이 검증은 AI/코드 사전점검이며 원판결 전문·역사 법령·학술 원저 확인, 독립 전문가 검토 및 수기분량 실측은 별도 HOLD**이다.

## 현재 불변 경계
- 저장소: nurioni4188/gongin-nomusa-quiz
- 브랜치: review/nomusa-auto-v1-20year-gate-20261115 / Draft PR #3
- main, Production, 기존 Preview, RC27/RC35, 원본 Q-Net 파일, 기존 문제 ID·저장키, 상세/압축 답안 원고는 수정하지 않는다.
- 독립 전문가 승인 **0/328**, FINAL_APPROVAL=HOLD. AI가 독립 전문가 서명을 대신할 수 없다.

## 사전점검 입력
1. review/NOMUSA_V23_VALIDATION_LEDGER.json (공식 기출 원본 328 SHA 매핑, 시점·판례·학술·수식 등)
2. review/NOMUSA_V23_QNET_OFFICIAL_MANIFEST.json
3. review/NOMUSA_V22_2022_OFFICIAL_PRECEDENT_CROSSCHECK.json (2022년 판시요지 4개; 원판결 전문은 HOLD)
4. review/NOMUSA_V23_CASE_3_CORROBORATION_20261117.json (판례 3건 별도 근거; 원판결 법리·사안포섭 HOLD)
5. 기존 Chromium 20개년 JSON 출력 및 V19/V21/V22의 검증 결과.

## 실행
- GitHub Actions: .github/workflows/nomusa-v26-2-3-packets.yml
- 재현: python scripts/nomusa-v26-substantive-review-packets.py .
- 재현 전 선행: python scripts/nomusa-canonical-shared-browser-gate.py . / python scripts/nomusa-essay-approval-v21.py . / python scripts/nomusa-v22-original-expert-packets.py .
- 스크립트는 정확히 328 ID·원고 SHA·공식 파일 해시·소문항 32·P0 19·P1 77을 강제검증하고 실패 시 HOLD로 종료.
- 2022 19개를 가장 먼저, 분량 프록시 77개는 이후 도메인별로 검토. AI가 확인하는 것은 법 조문 표기·판례번호/날짜 후보·학술 저자/연도 후보·수식 등식 계산 및 증빙 경로와 원고 해시까지다. 정확한 법리/필기분량은 증명할 수 없다.
- 상세 보고서: review-artifacts/NOMUSA_V26/NOMUSA_V26_2_96_PRECHECK_REPORT.md
- 기계 가독 원장: review-artifacts/NOMUSA_V26/NOMUSA_V26_2_96_CONTENT_PRECHECK.json
- 우선심사 파일: review-artifacts/NOMUSA_V26/NOMUSA_V26_2_PRIORITY_2022_19_PLUS_77.zip

## 검증/승인 구분
- PASS_TECHNICAL: 96·328 대상 ID와 SHA 일치, 기존 공식 파일 원장 연결, 판례·학술·수식 근거 후보 매핑.
- REVIEW_CANDIDATE: 실제 답안 학술·법률 정확성 확인 대상. 오류로 확정된 것이 아님.
- HOLD_CONTENT: 실제 시험일 법령/부칙, 원판결 전체, 이론 원저, 수식 및 그래프, 실전필기 전문가 검증.
- HOLD_EXPERT: 자격·독립성·서면의견·검토일·본문 SHA 일치 외부 승인 전까지 0/328.
- 검증 불확실성을 숨기거나 AI 프록시 플래그를 전문 검증 완료로 보이지 말 것.

## 다음 독립검증
외부 자격 검토자에게 원전 PDF/HWP 인쇄면과 각 학술·판례 원문 전문을 함께 보게 하고, 수정안→SHA 갱신→검토서의 순서로 처리. 무단 이메일 발송/배포 금지.

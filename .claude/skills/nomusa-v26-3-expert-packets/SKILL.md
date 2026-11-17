---
name: nomusa-v26-3-expert-packets
description: "20개년 공인노무사 2차 328개 기출/상세·압축답안을 7개 과목별 독립 전문가 심사 ZIP·빈 회신 JSON·발송대장 CSV로 일괄 구성하며 이메일·배포·자동승인을 금지하는 반복 실행 스킬."
---

# NOMUSA V26-3 — 전체 328개 / 7과목 독립 전문가 심사패킷

## 목적
- 2007~2026년 20개년 328개 문항을 **노동법Ⅰ·Ⅱ, 행정쟁송법, 민사소송법, 노동경제학, 인사노무관리론, 경영조직론** 7개로 분류한다.
- 검토 문항별 **원문전사, 50/25점 및 소문항 배점, 상세/압축 답안 전문, 원고 SHA-256, Q-Net 공식 첨부 링크·구성원 SHA, 기존 판례/학술/수식 확인 후보, 미해결 검토사유**를 포함한다.
- **검토자 실명·자격·날짜·서명·의견은 절대 추정하거나 채우지 않는다.** 빈 원본 서식을 제공한다.
- 첨부 Q-Net 원본 PDF/HWP 바이너리는 ZIP에 넣지 않는다. 공식 게시물 링크와 SHA를 제공하고 검토자가 원본을 직접 대조한다.

## 사용방법
1. 코드 브랜치 review/nomusa-auto-v1-20year-gate-20261115 및 Draft PR #3 상태 확인.
2. review/NOMUSA_V23_VALIDATION_LEDGER.json, review/NOMUSA_V21_INDEPENDENT_REVIEW_TEMPLATE.json, V22/V23 판례 근거 기록을 읽는다.
3. 선행 20년 Chromium JSON 출력을 가져온 후 python scripts/nomusa-v26-substantive-review-packets.py . 실행.
4. 출력 폴더 review-artifacts/NOMUSA_V26/NOMUSA_V26_3_SUBJECT_ZIPS/의 **7개 과목별 ZIP**을 별도로 배포할 수 있는 후보 파일로 확인한다.
5. review-artifacts/NOMUSA_V26/NOMUSA_V26_3_328_DISPATCH_TRACKER.csv에서 미발송/미회신 상태를 관리하고 실제 수신인과 발송/회신일이 확보될 때만 사람이 기입한다.
6. 별도 zip NOMUSA_V26_2_PRIORITY_2022_19_PLUS_77.zip은 96개 우선검토 모음; 같은 문항이 7과목 ZIP에도 존재하므로 이를 **424개 고유문항**이라고 보고하지 않는다.

## 핵심 결과물 및 검증
- NOMUSA_V26_3_EXPERT_PACKETS/{subject}/questions/ 에 328개 개별 검토 문서.
- NOMUSA_V26_3_EXPERT_PACKETS/{subject}/attestations/ 에 328개 **빈** 독립전문가 서면심사 JSON.
- NOMUSA_V26_3_SUBJECT_ZIPS/ 에 7개 ZIP.
- NOMUSA_V26_3_328_ROUTING.json 에 328개 분류·경로·현재 SHA 연결.
- NOMUSA_V26_3_328_DISPATCH_TRACKER.csv 에 발송·회신 관문.
- NOMUSA_V26_3_DISPATCH_INDEX.md 에 과목별 구성·전송 안내.
- 모든 ZIP의 CRC와 모든 검토자 서식 328개 수가 일치해야 PASS. 사용자의 명시 승인 없는 발송은 하지 않는다.

## 보호 규칙
- main, Production, Preview, 기존 RC27·RC35, 원문 PDF/HWP, 학습자 저장키·문항 ID, 상세/압축 답안 불변.
- **FINAL_APPROVAL=HOLD, 독립 전문가 승인 0/328.** 실제 서명·자격·독립성·검토일·원전 근거와 같은 SHA 일치 없이는 승격 금지.
- JSON 빈 서식의 신원·서명을 AI가 채우는 것은 금지.
- GitHub Actions artifact는 다운로드와 배포 허가를 뜻하지 않는다. 전문가 이메일 발송 금지.
- 본 스킬은 GitHub 저장소 내 Claude Code용 재사용 지침이며 전역 모델 스킬 설치가 아니다.

## 재사용/다음 작업
실제 전문가 검토 결과를 수령하면 ID·원고 SHA 검증 후 재심사 대장을 만들고, 반려/추가수정/HOLD/사람 승인 후보를 분리한다. 새 출처 확인이나 법리 분석을 AI가 했어도 독립 전문가의 승인서가 없으면 HOLD이다.

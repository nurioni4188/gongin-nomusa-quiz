---
name: nomusa-v27-2022-real-source-claims
description: "공인노무사 2차 2022년 19문항 중 공식 판결문과 학술지 출판사 서지·초록을 직접 확인한 6개 문항의 제한적 원전 교차검증을 재현하고, 오류 정정 후보·기출 원고 SHA·0/328 전문가 HOLD를 유지."
---

# NOMUSA V27 — 2022년 19개 중 6개 문항 실제 원전 주장 검증

## 시작
기존 GitHub 검토 브랜치 `review/nomusa-auto-v1-20year-gate-20261115`, Draft PR #3에서만 실행한다. `main`/Production/Preview/RC27·RC35/문제 ID/저장키/기출 PDF·HWP/원고 답안은 수정하지 않는다. 전문가 이메일 발송 금지.

## 이전 작업 재사용
- 2022년 19개·32소문항 전체의 Q-Net 파일 동일성·문항 SHA·배점 및 PC·모바일 Chromium 검증: V23~V26.
- 328 답안의 과목별 심사패킷과 96개 우선검토: `.claude/skills/nomusa-v26-2-content-review/SKILL.md`, `.claude/skills/nomusa-v26-3-expert-packets/SKILL.md`.
- 외부 교차검증 증빙: `review/NOMUSA_V27_2022_PRIMARY_CONTENT_CROSSCHECK_20261118.json`. 실제 확인 날짜·URL·대상 본문 SHA·판단범위·미확인 범위 기록.
- 스크립트 `scripts/nomusa-v27-2022-primary-content-check.py`, GitHub Actions `.github/workflows/nomusa-v27-2022-content-check.yml`.
- 원고 검증은 현재 Chromium 출력 20개년의 `sourceText+detailed+compressed` SHA와 V23 328행의 일치를 요구한다.

## 실제 원전의 제한된 교차검증 범위
1. `2022-admin-2`: 대법원 2019두52386(2020.2.20.), 2021두46285(2022.7.14.)의 **구제신청 중 정년 도달 vs 신청 전 지위 종료** 법리 구별 — 국가법령정보센터의 판결문 공개 HTML에서 해당 부분 확인. 정확한 정년 취업규칙 효력 및 사례의 금전보상 신청 포섭은 독립 검토 HOLD.
2. `2022-labor1-2`: 2019다238053(2022.4.28.)의 정기상여금 지급조건·퇴직자 일할 계산·통상임금성 — 국가법령정보센터 판결문 관련 법리 확인. 후속 변경 판례와 2022년 시험 당시 법리 구별.
3. `2022-labor2-2`: 2017도2478(2020.7.29.)의 산별노조 간부 시설출입, 안전목적·관행·수단·시설관리권 — 공식 판시요지 확인. 원판결 전체 사실인정 및 민·형사 적용은 HOLD.
4. `2022-hr-1`: Goldstein(1978)의 공식 출판사 SAGE에서 **Human Factors 20(2):131–144, DOI 10.1177/001872087802000202** 확인. 이 답안의 V16.2에 옛 오류 `Human Relations`가 남고 V16.3에 `Human Factors`로 정정이 함께 있어 **P1 편집 교정 후보**. 관리층 교육기법 여섯 번째를 액션러닝 vs 경영 시뮬레이션으로 서로 달리 열거하여 원고 통일 후보. 실제 교정 시 원고 SHA 새로 발급하고 모든 전문가 패킷 재생성.
5. `2022-org-2`: Tversky & Kahneman(1974, Science), Staw(1976, Organizational Behavior and Human Performance), Nickerson(1998, Review of General Psychology), Fischhoff(1975, JEP:HPP의 BMJ 공개 재간행물)의 **공식 학술 서지/공개 초록 범위** 확인. 유료 논문 전문 전체 실험결과와 논증 적용은 HOLD.
6. `2022-econ-2`: 2인 소득점유 20%/80%의 로렌츠 점과 면적 B=0.35, 지니계수 G=0.30을 별도 독립 재계산. 수기 그래프 축·표시는 검증 HOLD.

## 정확한 판정 표현
- 위 6개는 **일부 주장에 대한 원전·학술 출판사 근거 확인**이다. 19개 전체 승인 또는 6개 전체 내용승인으로 표현 금지.
- 나머지 **2022년 13문항은 이 V27 배치에서 새로운 외부 원전 교차검증을 시행하지 않았다.** 기존 기출 공식성 PASS와 전문가 내용승인을 혼동하지 말 것.
- **전문가 승인 0/328**, 2022년 19개 모두 최종승인 HOLD. 모든 실제 독립 전문가의 서면 검토는 별도로 필요.
- 새로운 출처가 확인되지 않거나 인쇄 원전·판결문 전체·시험 당시 연혁법령·학술 원서 전문을 읽지 못한 경우 정확하게 HOLD.

## 실행 및 결과
```bash
python scripts/nomusa-v27-2022-primary-content-check.py --self-test
python scripts/nomusa-canonical-shared-browser-gate.py .
python scripts/nomusa-v27-2022-primary-content-check.py .
```
- GitHub Actions artifact: `review-artifacts/NOMUSA_V27/NOMUSA_V27_2022_19_REVIEW_LEDGER.json`와 `NOMUSA_V27_2022_19_REPORT.md`, 공식 URL 목록 포함.
- 이 스킬은 GitHub 저장소 내부 Claude Code용이며 ChatGPT의 전역 스킬이 아니다.

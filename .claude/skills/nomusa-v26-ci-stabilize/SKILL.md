---
name: nomusa-v26-ci-stabilize
description: "NOMUSA GitHub 검토 브랜치의 legacy V20·V21·V22·공통 Chromium Actions Ubuntu 26.04/Playwright 1.56 실행 실패를 Ubuntu 24.04로 정비하고 328개 원문/저장/복원 회귀검증. main/Production/Preview 유지."
---

# NOMUSA V26-1 — 기존 GitHub Actions 실행환경 안정화

## 안전 경계
- Repo `nurioni4188/gongin-nomusa-quiz`; 브랜치 `review/nomusa-auto-v1-20year-gate-20261115`; 기존 Draft PR #3.
- `main`, Production, Preview, RC27/RC35, 데이터 저장키, 문항 IDs, 채점/전문가 승인 및 기출 PDF 원본 변경 금지.
- 이 스킬은 저장소 안의 재사용 절차이며 ChatGPT 또는 Claude의 전역 스킬 설치를 뜻하지 않는다.

## 변경 이유 및 조치
- 이전 Actions 실패 이력에서 `ubuntu-latest`가 `ubuntu-26.04`로 해석되었고 Playwright==1.56.x `chromium --with-deps` 설치가 `does not support chromium on ubuntu26.04-x64`로 실패했다.
- 네 파일의 `runs-on: ubuntu-latest`를 `runs-on: ubuntu-24.04`로만 변경:
  - `.github/workflows/nomusa-canonical-e2e.yml`
  - `.github/workflows/nomusa-v20-content-review.yml`
  - `.github/workflows/nomusa-v21-approval-audit.yml`
  - `.github/workflows/nomusa-v22-primary-expert-packets.yml`
- 소스/기출/앱/승인대장 재작성 없이 단일 커밋 `a3c27b1674930bb488bc20ffd1c1f5d3fa9e8a13`으로 기존 검토 브랜치에만 반영.
- 동일 커밋으로 자동 트리거된 4개 워크플로가 `success`인지 확인하고 실행 중에는 PASS라고 선언하지 않는다.

## 확인 항목
1. GitHub Actions 로그에서 OS가 Ubuntu 24.04인지, 브라우저 설치가 성공했는지 확인.
2. 기존 Chromium PC1440/모바일390·360 저장/복원·ID·기출·압축답안 회귀검증 재사용.
3. V20 88개 추가 논증 원장, V21 328개 전문가 사전검증, V22 PDF 원전 패킷이 기술적으로 성공했는지 각각 다른 run URL로 확인.
4. V23/V25 최신 원장 `qnetOfficialByteIdentical=328`, `sourceVerifiedQuestion=328`, HIGH 327/MEDIUM 1, `storedQuestionIsSummary=0`, 독립 내용승인 0/328 HOLD를 보존.
5. 원전 PDF/문항ID/사용자 로컬 저장키, main SHA, Draft PR 상태, Vercel Preview/Production 배포 불변 확인.
6. 실패 시 OS 문제와 답안 내용·검증기준 오류를 구분하고 스크립트 수정 전 해당 오류의 실제 로그를 기록.

## 금지 사항
- 전문가가 실제 서명하지 않은 논술답안의 최종승인 금지.
- 추가 GH Actions 계산 예산 과소비를 방지하기 위한 불필요한 전체 CI 반복 실행 금지.
- 기존 운영환경, Preview, main 변경·배포·PR merge·이메일 발송 금지.

## 재실행
- GitHub 검토 브랜치에서 수동 workflow_dispatch 가능. 다만 최근 같은 SHA PASS라면 재실행하지 않는다.
- 동일 파일 수정으로 트리거하는 push run을 사용할 때 여러 파일을 한 커밋으로 관리하고 각 워크플로의 concurrency/cancel-in-progress를 고려한다.

## 보고
- 유효한 GitHub run URL·완료 여부·OS·run ID/commit SHA만 PASS 근거로 사용.
- 사용자가 main/Production/Preview 변경의 호불호만 요청하면 간단히 답한다: **변경하지 않는 것이 좋음**.

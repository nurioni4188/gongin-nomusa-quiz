# AGENTS.md — 공인노무사 기출 퀴즈 저장소 AI 작업 규칙

Codex, ChatGPT, Claude 등 이 저장소를 여는 모든 AI 에이전트는 작업 전에 이 파일을 따른다.

## 1. 작업 범위
- 작업 브랜치: `review/nomusa-auto-v1-20year-gate-20261115` (기존 Draft PR #3). 새 PR은 꼭 필요할 때만.
- **변경 금지:** `main`, Production, 기존 Vercel Preview(`gongin-nomusa-rc27-preview`), RC27/RC35, 문제 ID, 수험생 저장키, `source_pdf/`의 공식 원본 파일.
- **금지 행위:** 배포, Draft PR 병합, 신규 Vercel 프로젝트·DB·서버, AI 자동채점, 이메일 자동 발송.
- 변경 허용: 검토 브랜치의 검증 스크립트, 근거 자료, CI, 심사 패킷, 보고서, 스킬.

## 2. 먼저 읽을 파일 (순서대로)
1. `.claude/skills/nomusa-v23-opus55-validation/SKILL.md` — 현재 검증 절차·판정 규칙·재현 명령 (일반 마크다운이라 어떤 에이전트도 읽을 수 있음)
2. `review/NOMUSA_V23_OPEN_ISSUES.md` — 남은 오류와 HOLD 목록
3. `review/NOMUSA_V23_CLAUDE_RUN_LOG.md` — 실행 명령·커밋·GitHub Actions 결과
4. `review/NOMUSA_V23_VALIDATION_LEDGER.json` — 328개 문항별 검증원장
5. 이전 단계 스킬: `.agents/skills/` (V19~V22)

## 3. 현재 상태 (2026-11-17, V23)
- 2007~2026년 답안 328개. Q-Net 공식 첨부파일과 SHA-256 동일성 **328/328**.
- 문항·배점 대조 328 통과. 단 2015~2018·2021 인사노무관리론/경영조직론 **30개는 요지이므로 공식 원문으로 교체 필요**.
- 판례 HOLD 3건: 2012다81609, 2011두7526, 2024구합76393.
- 시험 당시 법령, 판결문 전문, 학술 원서, 손글씨 분량은 HOLD.
- **독립 전문가 승인 0/328, FINAL_APPROVAL=HOLD.**

## 4. 반드시 지킬 검증 규칙
- 이미 PASS된 검증을 다시 개발하지 말고 기존 스크립트를 재사용한다.
- 확인하지 못한 출처·판례·연도는 HOLD로 둔다. 사건번호·URL·연도·저자를 만들어 내지 않는다.
- AI 검토(어떤 모델이든, 여러 모델이 일치해도)는 전문가 승인이 아니다. 승인 수를 0/328에서 늘리지 않는다.
- 승인은 외부 독립 전문가가 실명·자격·검토일·확인 원전·결론·서명을 같은 `textSHA256` 원고에 서면으로 제출할 때만 가능하다.
- 원고(`sourceText`/`detailed`/`compressed`)를 바꾸면 `textSHA256`이 바뀌므로 V21→V22→V23을 다시 실행한다. 문제 ID·저장키는 유지한다.
- 실제로 실행하지 않은 검증을 완료했다고 보고하지 않는다. 결과는 커밋 SHA, Actions run URL, 실제 소요시간으로 증빙한다.

## 5. 재현 명령
```bash
pip install playwright==1.56.0 pymupdf==1.26.7 olefile==0.47 cryptography==44.0.0 sympy==1.13.3
python -m playwright install chromium
python scripts/nomusa-canonical-shared-browser-gate.py .
python scripts/nomusa-essay-quality-v19.py . --expected-total 328 --baseline 88
python scripts/nomusa-essay-approval-v21.py .
python scripts/nomusa-v22-original-expert-packets.py .
python scripts/nomusa-v23-validation-ledger.py .
```
- CI: `.github/workflows/nomusa-v23-opus55-validation.yml` (runs-on `ubuntu-24.04`; `ubuntu-latest`=26.04에서는 Playwright 1.56 설치 실패).
- 공식 원전 재확인(네트워크 필요): `python scripts/nomusa-v23-qnet-official-fetch.py /tmp/qnet --manifest /tmp/qnet.json`
- 공식 출처: Q-Net 공개문제 게시판(boardId=Q004), 국가법령정보센터 `https://www.law.go.kr/`, KCI `https://www.kci.go.kr/`.

## 6. 작업 기록
- 결과는 `review/NOMUSA_V23_*` 형식(또는 다음 버전 V24)의 원장·오류보고서·실행기록으로 남기고, 스킬 파일의 재현 경로를 갱신한다.
- 같은 브랜치를 여러 에이전트가 동시에 수정하지 않는다. 한쪽 작업이 커밋된 뒤 다음 작업을 시작한다.
- 생성물 `review-artifacts/`는 커밋하지 않는다(CI artifact로 게시).

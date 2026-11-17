# NOMUSA V23 — Claude Opus 5.5 자동검증 인수인계 / 2026-11-17

> **이 문서만 Claude Code에 붙여 실행해도 이미 GitHub에 있는 원전·스크립트·리뷰 기록을 이어서 사용할 수 있다.** ChatGPT Work 세션의 토큰·이력에 접근할 필요가 없다. 프로젝트 내 스킬: `.claude/skills/nomusa-v23-opus55-validation/SKILL.md`.

## 연결할 정확한 대상
- GitHub: `nurioni4188/gongin-nomusa-quiz`
- 작업 브랜치: `review/nomusa-auto-v1-20year-gate-20261115`
- 기존 Draft PR: #3 (현재 미병합, 새 PR은 꼭 필요한 경우가 아니면 만들지 말 것)
- Vercel 기존 프로젝트: `gongin-nomusa-rc27-preview`, 팀 `onnuri4188gmailcoms-projects`.
- 변경 허용: **기존 review 브랜치의 새 검증 스크립트, 근거 자료, CI, 심사패킷, 보고서, 스킬만.** main / 기존 Preview / Production / RC27/RC35 / 문제 ID / 수험생 저장키는 변경 금지.
- 승인 없는 Vercel 배포, 새로운 Vercel 프로젝트·DB·서버·AI 채점, Draft PR 병합 금지.
- 기존 2022년 전문가 과목별 ZIP 7개는 사용자에게 이메일로 전달된 상태이나 **전문가의 검토 완료는 아니다**. 이메일 발송을 반복하지 말 것.

## 실제 확인 완료된 상태
- V20: 20개년(2007~2026) 고유 답안 328개, 시험장 상세/압축 초안 88개에 원문연동 추가 논증(50점 32, 25점 56). 기술 QA PASS. 실제 전문학술 승인 HOLD.
- V21: `scripts/nomusa-essay-approval-v21.py`에서 328개 문항, 2022년 19개·32소문항, 배점 근거 26개, 분량 500자/쪽 프록시 77개(50점29, 25점48) 검증. [실제 Actions run 44059089809](https://github.com/nurioni4188/gongin-nomusa-quiz/actions/runs/44059089809) SUCCESS, 전문가 최종승인 0.
- V22: `scripts/nomusa-v22-original-expert-packets.py`에서 전체 328개 원본 PDF 후보 라우팅, 2022년 19개 PDF 텍스트 높은 유사도, 과목별 7개 PDF에서 원본 페이지 미리보기, 19개 별도 전문가 패킷 생성. [실제 Actions run 44061790296](https://github.com/nurioni4188/gongin-nomusa-quiz/actions/runs/44061790296) SUCCESS.
- V22의 328개 분류: 2022년 19개 높은 텍스트 일치 / 기타 209개 저장소 원본 PDF 후보 있으나 공식 첨부 동일성 미확인 / 2021년 6개 day1/day2 경로 혼선 / 2007~2012년 94개 원본 HWP 바이너리 미확인.
- V22 공식 판시요지 참고 연결: `review/NOMUSA_V22_2022_OFFICIAL_PRECEDENT_CROSSCHECK.json`, 2022년 3개 문항/대법원 판례 4건. 판시요지 확인을 판결문 전문·모범답안 법리 완결 승인으로 혼동 금지.
- 스킬 기존: `.agents/skills/nomusa-v22-primary-source-expert-gate/SKILL.md`; Claude 전용 새 스킬: `.claude/skills/nomusa-v23-opus55-validation/SKILL.md`.
- 해당 원본 문제지·저장소 PDF는 국가공식 Q-Net ZIP 첨부파일과 바이트 단위 동등성이 아직 확인되지 않음. PDF 텍스트 유사도는 시험문항의 그래프·배점·공식성 검증을 대신하지 못함.
- 지금까지 328개 중 실제 독립 전문가 서면승인 **0건**. 어떤 모델도 심사자 자격·실명·검토일·서명·원전 확인을 만들어 승인할 수 없음.

## 원전 및 재현 경로
- 공식 기출: 한국산업인력공단 Q-Net 2022 2차 기출문제 게시글 `https://www.q-net.or.kr/cst003.do?artlSeq=5210985&boardId=Q004&gId=05&gSite=L&id=cst00302`. 2007~2026년 원전별 게시물은 별도 검색·증빙.
- 법령: 국가법령정보센터 `https://www.law.go.kr/` → 시험 당시 연혁법령/부칙.
- 판례: 대한민국 법원/대법원 공식 판결문 또는 `https://www.law.go.kr/` 판례.
- 학술: KCI `https://www.kci.go.kr/kciportal/main.kci`와 저자 원저서/원논문.
- 스크립트: `scripts/nomusa-canonical-shared-browser-gate.py`, `scripts/nomusa-essay-quality-v19.py`, `scripts/nomusa-essay-approval-v21.py`, `scripts/nomusa-v22-original-expert-packets.py`.
- CI: `.github/workflows/nomusa-v22-primary-expert-packets.yml` 포함 기존 Actions.
- 기록: `review/NOMUSA_V22_SOURCE_EXPERT_GATE_EXECUTION_20261117.md`, `review/NOMUSA_V21_APPROVAL_EXECUTION_RECORD_20261117.md`, `review/NOMUSA_V21_INDEPENDENT_REVIEW_TEMPLATE.json`.

## 실행 우선순위
1. GitHub 원격 최신 HEAD와 2026-11-17 실행기록·배포 보호 규칙 확인.
2. 기존 Chromium/배점/내용 SHA 328개 재현. 기존 성공한 부분은 재개발 금지.
3. **2022년 19개**: 기출 원문/배점/그림/수식과 공식 ZIP 동일성 확인, 법률/학술/계산 원전의 직접 인용을 검토. 실제 근거를 가져올 수 없으면 HOLD. 고위험 쟁점만 수정 제안.
4. **2021년 6개** day1/day2 PDF 매핑, **2007~2012년 94개** HWP 원본 바이너리 복구 경로 검토. 획득하지 못하면 원본검증 HOLD.
5. 나머지 **309개 전부** 과목×연도 그룹으로 실행 가능한 원전 대조 배치. 프록시 77개, 법률 시행일/판례, 학술 저자·발행 연도, 노동경제학 수식·그림 오류를 우선 처리. 각 ID와 원전 URL·직접 대조 구간·시간·검증 등급 기록.
6. 검증 결과 각 항목에 `SOURCE_VERIFIED / MODEL_RECALCULATED / ACADEMIC_OR_CASE_HOLD / CORRECTION_REQUIRED / EXPERT_SIGNOFF_PENDING` 등 명확한 상호 구분 태그. 검증되지 않은 출처에 가공 링크/사건번호/연도 쓰지 말 것.
7. 완성된 과목별 검토 패킷은 전문가에게 전달 가능한 ZIP/MD/CSV로 생성하고 GitHub Actions에 artifact 또는 Draft PR 댓글 링크로 증빙. 요청되지 않은 이메일 전송 금지.
8. 작업이 크므로 범위를 순차 분할해도 좋으나, 각각 전수처리 대상 ID/실제 소요시간/통과·HOLD·오류 항목을 반드시 남겨 이어서 실행할 수 있게 한다.

## 출력 요구
- `review/NOMUSA_V23_VALIDATION_LEDGER.json`: 328개 전수 + 질문ID/연도/과목/텍스트SHA/원문 PDF·HWP 출처/시험 당시 법령·판례·학술 원전 링크/검산 흔적/불일치·수정안/검증 수준/전문가 승인 HOLD.
- `review/NOMUSA_V23_OPEN_ISSUES.md`: 원본자료 부족 및 위험 오류 우선순위.
- `review/NOMUSA_V23_CLAUDE_RUN_LOG.md`: 실제 실행한 명령·성공/실패·변경 SHA/CI run URL/배포 불변/소요시간.
- `.claude/skills/nomusa-v23-opus55-validation/SKILL.md` 재현 명령과 오류 교정 시 최신화.
- CI 기술검증/실제 학술·법리 확인/전문가 내용승인 각각 독립된 PASS/HOLD 표.
- 전문가 승인 0/328을 허위로 늘리지 않는다. 외부 전문가가 서면 검토하고 정확히 같은 SHA의 원고에 서명할 때만 승인 가능.

## Claude에게 바로 복사할 단축 실행명령
```text
Claude Opus 5.5, Claude Code 실행환경에서 GitHub nurioni4188/gongin-nomusa-quiz의 기존 브랜치 review/nomusa-auto-v1-20year-gate-20261115를 열어 주세요. 반드시 review/NOMUSA_V23_CLAUDE_OPUS55_HANDOFF.md와 .claude/skills/nomusa-v23-opus55-validation/SKILL.md를 먼저 읽고 /nomusa-v23-opus55-validation 을 실행하세요. V22에서 PASS된 구조 검증을 재활용하고, 2007~2026 328개 답안의 기출 원전·시험 당시 법령/판례·학술·노동경제학 수식/그래프를 실제 공식 원전과 교차검증하세요. 2022년 19문항은 기준연도로 먼저, 나머지 309개는 과목/연도별 배치로 자동처리하세요. 확인되지 않은 근거는 무조건 HOLD, 독립 전문가 최종승인은 0/328 유지. 결과 및 소요시간은 V23 JSON/MD 대장과 스킬을 수정해 기존 Draft PR #3 review 브랜치에만 커밋하고 GitHub Actions에서 PC·모바일 검증한 후 run URL·artifact·SHA·HOLD 사유를 보고하세요. main, Production, Vercel Preview, RC27/RC35, 문제 ID, 저장키, 신규 프로젝트, 자동채점, 무단 이메일/배포는 전혀 변경하거나 실행하지 마세요. 필요한 GitHub 연결 권한은 제 계정에서 허용한 다음 실행하세요.
```

**Claude Code 웹 모드는 저장소와 브랜치를 정확하게 선택하고 Code 실행 세션을 사용한다. 일반 Claude 채팅만으로 GitHub 수정/로컬 Chromium/CI 실행을 완료했다고 판단하지 않는다.**

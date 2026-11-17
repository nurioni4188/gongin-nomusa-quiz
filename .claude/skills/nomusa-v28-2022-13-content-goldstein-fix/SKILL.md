---
name: nomusa-v28-2022-13-content-goldstein-fix
description: "공인노무사 2차 2022년 남은 13개 문항의 법원·학술 출판사 근거 후보를 실제 원전 한정 범위로 대조하고, 2022-hr-1 Goldstein 서지 오류와 교육훈련 기법의 불일치만 수선해 328개 SHA 및 PC/모바일 저장복원을 회귀검증하는 재사용 Claude Code 프로젝트 스킬."
---

# NOMUSA V28 — 2022년 19개 출처별 대조, Goldstein 단일답안 편집교정

## 실행 배경
- GitHub 저장소: `nurioni4188/gongin-nomusa-quiz`
- 작업 브랜치: `review/nomusa-auto-v1-20year-gate-20261115`; 기존 Draft PR #3
- V27: 2022년 19개 중 6개 답안에 대해 개별 원전·공식 서지·판례요지·수식의 제한적 근거를 대조함. 19개 답안 전체의 내용확정이나 인간 전문가 승인 0/328.
- V28: 나머지 13개 답안의 **각기 다른 확인 가능한 주장을 공식 재판례/학술출판사·학술기관/기출 수식으로 추적**. 원전의 제한된 본문·서지·초록 또는 모델 연산 결과가 확인된 범위에만 PASS 부여.
- 기존 328개 공식 Q-Net 첨부파일 해시·배점 확인 V23~V25 검증 결과 재사용, 별도 본문/원본 자료 재작성 금지.

## 입력 및 근거
- `review/NOMUSA_V23_VALIDATION_LEDGER.json` (328행, 원본파일 SHA, 학술/판례/계산 검토중)
- `review/NOMUSA_V27_2022_PRIMARY_CONTENT_CROSSCHECK_20261118.json` (V27 6개, **교정 전** `2022-hr-1` 문항 SHA이므로 현재 SHA로 무단 재표시 금지)
- `review/NOMUSA_V28_2022_REMAINING_13_SOURCE_CROSSCHECK_20261118.json` (V28 13개 근거와 URL·확인범위)
- `second/nomusa-v28-goldstein-2022-hr1.js` (2022-hr-1 단일원고의 해시 변경 편집교정)
- `scripts/nomusa-v28-browser-editorial-smoke.py` + `scripts/nomusa-v28-2022-13-and-goldstein-gate.py`
- `.github/workflows/nomusa-v28-2022-claims-and-editorial.yml`

## 교정의 범위
- 출판사 SAGE 원본 `https://journals.sagepub.com/doi/10.1177/001872087802000202` : Goldstein(1978) **Human Factors 20(2):131–144**, 기존 누적 원고에 오기인 *Human Relations*가 남음. 맞는 출판지로 정정하고 과거 오기 해설을 중복 노출하지 않음.
- 훈련기법 6번째가 옛 상세/압축의 일부에는 `경영 시뮬레이션`, 주요 상세·압축 본문에는 `액션러닝`으로 서로 달라서, 2022-hr-1의 여섯 번째 예시를 **액션러닝**으로 통일.
- 사용자 화면에 상세 원문 `detailed`와 압축 `compressed`를 함께 수정, 원래 항목은 `detailedBeforeV28` / `compressedBeforeV28`로 되돌릴 수 있게 보존.
- **문제 원문·배점·문제ID·기존 저장키, 나머지 327개 답안, Q-Net 첨부파일 불변.**
- 원전 학술지 전체 실험 설계·법령시점 등은 실명 검토자가 승인하지 않았으므로 `FINAL_APPROVAL=HOLD`.

## V28 13개 항목 내용범위
- `2022-admin-1`: 취소소송 제3자 환경상 이익/예방적 금지소송의 원칙과 법인 원고적격 구별. 특정 산지 영향권과 법인 보호규정 포섭 HOLD.
- `2022-admin-3`: 2014두37122(원칙 처분시 기준)와 2019다264700(신청 처분 관련 새 법령·경과규정) 법리의 관련 부분. 2022 특별법 부칙 HOLD.
- `2022-civil-1`: 98다22253 전원합의체의 예비적 병합 및 상소심 이심 법리. 복수 선정당사자 일방의 자백효력은 별도 HOLD.
- `2022-civil-2`: 2016다46338 상계항변 기판력 특칙. 항변 전반의 분류/시험 당시 시행 민사소송법 전체 검토 HOLD.
- `2022-civil-3`: 2021다305796 공시송달 후 추완항소, 민사소송법 제451조 제1항 제11호 허위 주소/재심. 역사 시행본·사안포섭 HOLD.
- `2022-econ-1`: 임금 1·1.5, 시간 8·12·15에서 예산선/효용 예시 독립 검산. 모든 선호함수 최적화 일반화와 수기 그래프 HOLD.
- `2022-econ-3`: 노조 조직 위협효과와 비노조 비교집단 변화의 NBER 초록 근거; 대기실업 효과 세부 원저 독립 검증 HOLD.
- `2022-hr-2`: Doeringer & Piore(1971) 연구기관 서지, Breaugh(2013) Annual Reviews 원저 초록. 내부모집 장·단점 전부 원저 실증이라고 단정하지 않는다.
- `2022-hr-3`: Walton & McKersie(1965) 원서 서지, 시험의 '포용·압박·회피' 분류와 원서 4교섭 과정의 동일 기원 **HOLD**.
- `2022-labor1-1`: 2018다253680(저성과 통상해고), 2017다226605(해고사유가 없는 서면통지) 대법원 판시. 개별 사실관계 판단 HOLD.
- `2022-labor2-1`: 2015도1927(원청 사업장 수급인 노조 쟁의행위) 법리. 대체근로 저지 별도 형사구성요건 HOLD.
- `2022-org-1`: Rahim(1983) Academy of Management Journal 발행 정보·학술 초록, 갈등관리 5유형 참고. 10개 갈등 대응기법을 원논문에서 전부 입증했다고 말하지 않는다.
- `2022-org-3`: Perrow(1967) American Sociological Review 발행·기술 이론 서지, 통제범위 보편 법칙의 원문 직접 대조 HOLD.

## 재현 순서
1. 최신 PR HEAD와 V27 6개·V28 13개 근거/원장 328개를 읽고 19 ID가 중복 없이 채워졌는지 확인.
2. `python scripts/nomusa-v28-browser-editorial-smoke.py .` — 두 화면의 V28 원자적 적용과 수정 외 원고·원본 불변 검사.
3. `python scripts/nomusa-canonical-shared-browser-gate.py .` — PC1440/모바일390·360 저장/복원 실검증.
4. `python scripts/nomusa-essay-quality-v19.py . --expected-total 328 --baseline 88`, `python scripts/nomusa-essay-approval-v21.py .`, `python scripts/nomusa-v22-original-expert-packets.py .` 기존 검증 재사용.
5. `python scripts/nomusa-v28-2022-13-and-goldstein-gate.py .` — 13개 출처·V27 6개 결합, 1개 SHA 변경/327개 SHA 불변, 독립 전문가 0.
6. `python scripts/nomusa-v23-validation-ledger.py .` — 최신 328개 원고 SHA 재생성·검토 브랜치에만 커밋.
7. `python scripts/nomusa-v26-substantive-review-packets.py .` — V28 신규 SHA를 반영한 전체 **7개 과목별 328 심사패킷과 96개 우선대상** 재생성; 이전 V26 ZIP은 수정 전 Goldstein SHA를 참조하므로 과거 스냅샷으로만 보관.
8. [V28 GitHub Actions](https://github.com/nurioni4188/gongin-nomusa-quiz/actions/workflows/nomusa-v28-2022-claims-and-editorial.yml) 작업결과 및 artifact와 실행시간/실제 커밋을 확인.

## 주의
- 인간 검토자·자격·검토일·서명·원전 확인을 자동으로 생성하거나 가정하지 않는다.
- 출판사 서지확인, 판시요지 확인, 독립 산술검산은 **문항 전체 내용 최종승인과 다르다**. 19개 원고 모두 전문가 최종승인 HOLD.
- GitHub `main`, Production·Preview, RC27·RC35, 문제ID, 학습 저장키, 원본 PDF/HWP 변경·새 사이트/프로젝트/DB 생성·이메일 발송 금지.
- V25 오래된 원본시각검증 워크플로는 V28 이후 재현성이 없으므로 자동 push 실행 대신 `workflow_dispatch`만 유지; 최신 회귀검증은 V28로 수행한다.

## 다음 실제 심사
시험일 법령·부칙의 효력/원판결 전문 및 적용, 학술 논문 전체 실험·원저서 본문, 실제 필기 시간·장수, 328개 중 우선 96개 독립 전문가 서면검토를 진행한다. 전문가 승인 0/328을 위조·자동승격하지 않는다.

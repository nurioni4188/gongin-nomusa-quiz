# NOMUSA V23 Claude 실행기록 (2026-11-17)

- 실행: Claude Code 원격 세션(Claude Opus 5.5), 스킬 `/nomusa-v23-opus55-validation`
- 브랜치: `review/nomusa-auto-v1-20year-gate-20261115` (기존 Draft PR #3). 시작 HEAD `c4797a314e9cf445dfe22d58dc22c59bd055e719`
- `main` = `9ea46fc9134c55a4312241b55a82b237e86ed4a8` — 작업 전후 동일(변경 없음). Vercel/Production/Preview/RC27/RC35/문제 ID/저장키 변경 없음, 배포·이메일 없음.
- 세션 작업시간(실측): 2026-11-17 약 12:14 UTC 클론 → 13:10 UTC 문서화. 자세한 단계 시간은 아래.

## 1. 실행 명령과 결과

| 단계 | 명령 | 결과 | 실측 |
|---|---|---|---|
| 기존 도구 재현 | `nomusa-essay-quality-v19.py --self-test`, `nomusa-essay-approval-v21.py --self-test`, `nomusa-v22-original-expert-packets.py --self-test` | PASS×3 | — |
| Chromium PC1440/모바일390·360 | `python scripts/nomusa-canonical-shared-browser-gate.py .` (로컬 Chromium 153) | PASS | 25.2s |
| V19/V21/V22 | 동일 스크립트 본실행 | PASS_STRUCTURAL / PASS_AUTOMATED_PRECHECK (승인 0) / PASS_REPO_PDF (94·209·6·19) | 26.5s 합계 |
| 네트워크 | 기본 환경은 Q-Net·law.go.kr 차단(403) → 개인 환경 `gongin-nomusa-quiz` 생성(허용: q-net, law.go.kr, scourt, kci) 후 전환 | Q-Net·law.go.kr 200, glaw.scourt.go.kr 502 | — |
| Q-Net 공식 첨부 | `python scripts/nomusa-v23-qnet-official-fetch.py /tmp/.../official --manifest review/NOMUSA_V23_QNET_OFFICIAL_MANIFEST.json` | 20개년 게시물·24개 첨부·63개 구성파일 SHA 기록 | 172.8s |
| 동일성 | 저장소 `source_pdf/**` 55개 해시 ↔ 매니페스트 | 55/55 바이트 동일; 2007~2012 HWP 6개 해시 = 기존 `NOMUSA_AUTO_V1_20YEAR_SOURCE_MANIFEST.json` | — |
| HWP 본문 | `scripts/nomusa_v23_hwp_text.py` (배포용 문서 ViewText AES-128 복호화) | 6개년 본문 추출 | <1s |
| OCR | Tesseract 5.3.4 kor, 200dpi, `review/NOMUSA_V23_OCR_TEXT_CACHE.json` | 이미지 PDF(2015~2018, 2021, 2024 5과목, 2013 배점용) 93페이지 | ≈60s (1차 300dpi 시도는 스레드 과다로 타임아웃 실패 → OMP_THREAD_LIMIT=1로 수정) |
| 판례 | `scripts/nomusa_v23_case_lookup.py` (law.go.kr precScListR) → `review/NOMUSA_V23_CASE_LOOKUP_CACHE.json` | 100개 중 97 확인. 1차 파서가 "전원합의체 판결"을 놓쳐 7건 오탐 → 수정 후 재조회 | ≈3분 |
| 계산 | `scripts/nomusa_v23_arith_check.py` | 숫자 29·SymPy 10, 불일치 0 (초기 오탐: 천단위 쉼표·½·변수계수 → 파서 수정) | — |
| 원장 | `python scripts/nomusa-v23-validation-ledger.py .` | 아래 요약 | 30.3s |

## 2. V23 원장 요약 (`review/NOMUSA_V23_VALIDATION_LEDGER.json`)

| 항목 | 값 |
|---|---|
| 전체 / 2022 기준연도 / 나머지 | 328 / 19 / 309 |
| Q-Net 공식 첨부와 바이트 동일 | **328/328** |
| 공식 원문 대비 문항·배점 대조 통과 | 328 (자동 HIGH 296, OCR MEDIUM 2, 수동 OCR 판독 30) |
| 문항이 요지(원문 아님) → 수정 필요 | 30 |
| 판례 인용(고유 사건번호) / law.go.kr 확인 | 216회(100) / 97 |
| 선고일 표기 대조 / 불일치 | 105 / **0** |
| 학술 저자·연도 쌍 | 153 (AI 사전점검만, 원전 HOLD) |
| 계산 재검증 | 숫자 29 + SymPy 10 + 수동 3문항, 불일치 0 |
| 전문가 승인 | **0/328, FINAL_APPROVAL=HOLD** |

## 3. 판정표 (서로 독립)

| 축 | PASS | HOLD | 비고 |
|---|---:|---:|---|
| CI 기술검증 (PC·모바일·구조·SHA 잠금) | 328 | 0 | PASS_TECHNICAL |
| 공식 기출 원전(문항·배점·파일 동일성) | 328 | 0 | VERIFIED_PRIMARY_SOURCE (단, 30건은 원문 교체 필요) |
| 법령·판례·학술 실제 내용 확인 | 0 | 328 | 판례 존재·선고일만 확인; 판결문 전문·연혁법령·원서 미열람 |
| 손글씨 분량 | 0 | 328 | HOLD_HANDWRITING |
| 독립 전문가 내용승인 | 0 | 328 | HOLD_EXPERT_APPROVAL |

## 4. 커밋과 CI

| 커밋 | 내용 | Actions |
|---|---|---|
| `8db43c4598fe6f253d1b84bdcfe22424c5274ac2` | V23 엔진·캐시·HWP 원본·원장·워크플로 | V23 [44088696196](https://github.com/nurioni4188/gongin-nomusa-quiz/actions/runs/44088696196) **실패**(ubuntu-latest=26.04에서 Playwright 1.56 미지원); V22 [44088696061](https://github.com/nurioni4188/gongin-nomusa-quiz/actions/runs/44088696061) 같은 이유로 실패 |
| `43885622334add0b20829e1864f14dacd96a956c` | V23 러너 `ubuntu-24.04` 고정 | V23 [44088809989](https://github.com/nurioni4188/gongin-nomusa-quiz/actions/runs/44088809989) **성공**, 13:02:39~13:06:42 UTC(4분 3초). 자체 테스트 4종 PASS, Chromium PC/모바일 PASS, V19/V21/V22 PASS, **Q-Net 실시간 재다운로드 126s → 63/63 해시 동일**, 원장 재현 일치. [artifact](https://github.com/nurioni4188/gongin-nomusa-quiz/actions/runs/44088809989/artifacts/14331700228) |
| (이 문서 커밋) | 학술 사전점검 보정, 오류보고서·실행기록·스킬 갱신 | 최종 run은 PR #3 댓글과 최종 보고에 기록 |

## 5. 다음에 이어서 할 정확한 명령

```bash
python scripts/nomusa-v23-validation-ledger.py .            # 캐시만으로 재현(네트워크 불필요)
python scripts/nomusa-v23-qnet-official-fetch.py /tmp/qnet --manifest /tmp/qnet.json   # 공식 첨부 재확인
python -c "import sys;sys.path.insert(0,'scripts');from nomusa_v23_case_lookup import lookup;print(lookup('2012다81609'))"
```

남은 일: (1) 30개 요지문항 원문 전사·교체(사람 OCR 교정) 후 SHA 갱신·재검증, (2) 2012다81609·2011두7526·2024구합76393 판결서 확보(대법원 종합법률정보 접속 필요), (3) 법률 문항 연혁법령·판결문 전문 대조, (4) 학술 원서 확인, (5) 손글씨 실측, (6) 독립 전문가 서면승인.

## 6. ChatGPT 판례 교차확인 게이트 (2026-11-17)

기존 Claude Opus 5.5 V23 실행결과를 그대로 이어받아, OPEN_ISSUES §2에서 국가법령정보센터 검색에 잡히지 않은 **3개 판례를 별도 공개 출처로 교차확인**했다. 같은 328개에 대한 기존 Q-Net·배점·Chromium PASS를 재실행하거나 재개발하지 않았다.

- 추가 증빙: `review/NOMUSA_V23_CASE_3_CORROBORATION_20261117.json` (2026-11-17, URL·증거수준·HOLD 명시).
- 재현 명령: `python3 scripts/nomusa-v23-case-corroboration-gate.py .`.
- 자동검증: [Actions #44093049996](https://github.com/nurioni4188/gongin-nomusa-quiz/actions/runs/44093049996), 2026-11-17 **13:28:22~13:28:33 UTC (전체 약 11초)**, ubuntu-24.04, **success**. 독립 프로그램이 기존 원장 328개/3개 문항/3개 사건번호·5회 인용/원고 SHA/전문가 0건을 모두 대조했다.
- 내용범위: 2012다81609의 대법원 공식 후속판결 인용, 2011두7526의 한국노동연구원 판례평석, 2024구합76393의 서울행정법원 공식 목록 및 비법원 날짜 보조증거.
- **원본 판결문 전문 읽기·2024 판결일 공식문서 확인·개별 사안포섭·법률시점 원전 전수는 HOLD**, 기존 law.go.kr 검색 캐시/328 원장은 수정하지 않음.
- 회귀 영향: 원본 답안·ID·저장키·2022 기준연도·main·Production·Preview 변경 없음. 이메일·배포·전문가 승인 없음.

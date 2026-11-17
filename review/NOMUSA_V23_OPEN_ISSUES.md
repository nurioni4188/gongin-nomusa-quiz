# NOMUSA V23 오류·미해결 보고서 (2026-11-17, Claude Opus 5.5 AI 사전검증)

> 이 문서는 AI 사전검증 결과입니다. **독립 전문가 최종승인 0/328, FINAL_APPROVAL=HOLD.** 앱 원고·문제 ID·저장키는 수정하지 않았고, 아래 수정안은 제안일 뿐입니다.
> 전수 데이터: `review/NOMUSA_V23_VALIDATION_LEDGER.json` (328행), 재현: `python scripts/nomusa-v23-validation-ledger.py .`

## 0. V22 대비 해소된 항목

| V22 HOLD | V23 결과 | 근거 |
|---|---|---|
| 공식 Q-Net 첨부와 바이트 동일성 미확인 (328) | **해소: 328/328 SHA-256 동일** (2013~2026 PDF 55개 + 2007~2012 HWP 6개) | `review/NOMUSA_V23_QNET_OFFICIAL_MANIFEST.json`, CI 재다운로드 63/63 동일 |
| 2007~2012 HWP 원본 바이너리 없음 (94) | **해소: 원본 HWP 6개 확보·저장** (`source_pdf/qnet_official_hwp/`), 기존 매니페스트 해시와 일치, 배포용 문서 복호화로 본문 추출 → 94문항 문항·배점 대조 | `scripts/nomusa_v23_hwp_text.py` |
| 2021년 1·2일차 혼선 (6) | **해소: 인사노무관리론 3문항=1일차(토), 경영조직론 3문항=2일차(일)** (OCR 판독) | `review/NOMUSA_V23_MANUAL_REVIEW.json` |
| 2022년 19개 공식 동일성 | **해소: 7개 PDF가 Q-Net 게시물 artlSeq=5210985 ZIP 구성파일과 바이트 동일** | 위 매니페스트 |

## 1. 수정 필요 (CORRECTION_REQUIRED) — 30건, 우선순위 높음

**문항 본문이 공식 원문이 아니라 자동 생성된 "요지"** (예: `[기출문항 요지 · 원문 전문은 PDF 참조] … 을(를) 논하시오`). 공식 OCR 판독 결과 30건 모두 **주제·배점은 공식 문제와 일치**하나, 수험생 화면 문항이 원문 그대로가 아님.

- 2015: `2015_p3_q1~q3`(인사), `2015_p5_q1~q3`(조직)
- 2016: `2016_p3_q1~q3`, `2016_p5_q1~q3`
- 2017: `2017_p3_q1~q3`, `2017_p5_q1~q3`
- 2018: `2018_p3_q1~q3`, `2018_p5_q1~q3`
- 2021: `2021-인사노무관리론-q1~q3`, `2021-경영조직론-q1~q3`

수정안: 문제 ID·저장키는 그대로 두고 `sourceText`만 공식 원문(이미지 PDF이므로 사람이 OCR 교정한 전사)으로 교체 → `textSHA256` 변경 → 재검증. 판독 요지는 매니페스트별 `officialQuestionAsRead`에 기록. 참고: 2018 경영조직론 문제1 물음1 배점은 OCR상 "(90점)"이나 물음2 30점·총 50점 구조상 **20점**(OCR 오인식) — 원본 이미지로 사람 확인 필요.

## 2. 판례 HOLD (ACADEMIC_OR_CASE_HOLD) — 3개 사건번호/5회 인용

국가법령정보센터 판례검색(사건번호·사건명·본문 3가지 검색)에서 찾지 못함. **비공개 판결일 수 있으므로 허위로 단정하지 않음.**

| 문항 | 사건번호 | 답안 표기 | 조치 |
|---|---|---|---|
| `2014_p2_q1` (P3) | 2011두7526 | 대법원 2011. 5. 26. 선고 (고용안정협약·정리해고) | 대법원 종합법률정보/판결서 열람으로 실재·선고일 확인. 동일 취지 2011두20406(2014.3.27, law.go.kr 확인)은 존재 |
| `2022-labor1-1` (**P0**) | 2012다81609 | 대법원 2014. 12. 24. 선고 (해고사유 서면통지 간략기재) | 2022 기준연도 문항이므로 우선 확인. 같은 문단의 2021두50642·2017다226605는 law.go.kr 확인 |
| `2026-행정쟁송법\|2\|0` (P3) | 2024구합76393 | 서울행정법원 (답안 스스로 "대법원 판단 미확인" 표시) | 하급심. law.go.kr 미수록. 판결서 사본 확보 전 HOLD |

나머지 97개 사건번호는 law.go.kr에서 법원·선고일 확인. 답안에 선고일이 함께 적힌 105회 인용 모두 **공식 선고일과 일치(불일치 0)**. 시험일 이후 선고 판례는 `2007두8881`(2010.3.25, 2009년 문항) 1건이며 답안이 "시험 후 참고"로 이미 표시 → 시간효력 문제 없음.

## 3. 시험 당시 법령 (HOLD_TIME_EFFECT 점검)

- 14개 주요 개정(직장 내 괴롭힘 2019.7.16, 교섭창구단일화 2011.7.1, 근로시간면제 2010.7.1, 행정심판 임시처분 2010.7.26, 중대재해처벌법 2022.1.27, 행정기본법 2021.3.23 등) 키워드 점검에서 **시행 전 연도 문항에 무표시 언급 0건**.
- 단, 시행일 표는 모델 지식이며 국가법령정보센터 연혁법령으로 개별 확인하지 않았음 → 각 문항의 조문 시점 확인은 전문가 HOLD 유지. 판결문 전문과 사안포섭도 미검토.

## 4. 학술 원전 (인사노무관리론·경영조직론)

- 저자/서명-연도 쌍 153회(고유 133) 추출. AI 사전점검에서 연도 오류 의심 0건(초기 "불확실" 11건은 전후 문맥 확인 결과 Goldstein(1978) *Human Factors*, Rahim(1983), Miles & Snow(1978), Katzenbach & Smith(1993), Quinn & Cameron(1983), Weitzel & Jonsson(1989), Lau & Murnighan(1998) 등 표준 인용).
- **원서·원논문을 KCI/출판사에서 실제 열람하지 않았으므로 SOURCE_VERIFIED 아님** → 전원 ACADEMIC_OR_CASE_HOLD.
- 주의: 2021 경영조직론 문제2 공식 지문은 쓰레기통 모형을 "1971년 올슨(J. Olsen) 등"으로 표기. 통상 인용은 Cohen, March & Olsen(1972, ASQ). 답안에서 연도를 언급할 때 공식 지문 표기와 통상 인용의 차이를 주석으로 처리할 것을 권고.

## 5. 노동경제학 계산·그래프

- 순수 숫자 등식 29개 재계산, SymPy 항등식 10개 대수검증 → **불일치 0**. 2022 제1·2문 수동 독립검산 일치(예산선 C=E, 절점 (8,8)·(12,14)·(15,18.5), 지니 0.30/보정 0.60).
- 그래프 자체(곡선 형태·축)와 문장으로 서술된 비교정태는 자동검증 불가 → HOLD. 수식이 문장 속에 있는 대부분의 계산은 기계 추출 범위 밖.

## 6. 분량 우선검토 77개 (P1)

77개 모두 공식 문항·배점 대조 통과. 판례 인용 0, 계산 불일치 0, 요지문항 1건(`2017_p5_q2`, §1에 포함). **500자/쪽 프록시와 실제 손글씨 분량(50점 8~10장, 25점 4장)은 실측 없음 → HOLD_HANDWRITING.**

## 7. CI·환경

- 기존 V22 워크플로(`nomusa-v22-primary-expert-packets.yml`)는 `ubuntu-latest`가 26.04로 바뀌어 Playwright 1.56 브라우저 설치 실패(run 44088696061). V23 워크플로는 `ubuntu-24.04`로 고정하여 V19/V21/V22 단계를 모두 재실행·통과. 기존 V22 파일은 변경하지 않음(필요 시 같은 한 줄 수정 권고).
- 이 세션의 네트워크는 Q-Net·law.go.kr 허용 환경으로 전환해 실행. glaw.scourt.go.kr(대법원 종합법률정보)은 502로 접속 불가 → 판결서 전문 HOLD.

## 8. 전문가 승인 요청 (변경 없음)

과목별 패킷: CI artifact `NOMUSA_V23_SUBJECT_PACKETS/*.md`. 검토자는 실명·자격·검토일·확인 원전·결론·서명을 **같은 `textSHA256`** 원고에 대해 서면 제출해야 하며, 그 전까지 승인 0/328. 이메일은 발송하지 않았음.

## 9. 판례 3건 외부 출처 교차확인 (2026-11-17, 추가 증빙)

기존 국가법령정보센터 `precScListR` 조회의 **NOT_FOUND_ON_LAW_GO_KR_SEARCH 기록과 V23 원장 내 미확인 상태는 역사적 실행 결과로 보존**한다. 다른 공식·공공 연구 자료로 **사건번호 실재·선고일**을 따로 확인한 것으로, 위 §2의 "사건이 확인되지 않는다"를 "국가법령정보센터 해당 검색에서는 미조회, 별도 교차확인 자료 존재"로 해석한다.

| 사건번호 / 문항 | 2026-11-17 추가 자료 | 교차확인 결과 | 남은 HOLD |
|---|---|---|---|
| `2012다81609` / `2022-labor1-1` | 대법원 공식 [주요판결(2017다226605)](https://scourt.go.kr/supreme/news/NewsViewAction2.work?gubun=4&searchOption=&searchWord=&seqnum=7547), [2021두50642 관련 자료](https://www.scourt.go.kr/portal/news/NewsViewAction.work?gubun=4&pageIndex=1&searchOption=&searchWord=&seqnum=8203&type=5) | 대법원 공식 판례가 **2014-12-24 선고 2012다81609**를 명시적으로 인용하고 축약 해고통지 법리 설명 | 해당 **원판결 전문 직접 열람**, 법리의 개별 답안 적용·역사 법령 전문 |
| `2011두7526` / `2014_p2_q1` | 한국노동연구원 [노동판례리뷰](https://www.kli.re.kr/kli/prcdntView.es?currentPage=90&keyField=&keyWord=&keyYear=&mid=a10202000000&prcdnt_no=126968) | 연구기관 게재자료에서 대법원 **2011-05-26 선고 2011두7526** 및 고용안정협약 법리 인용 | **법원 판결문 1차 원전/선고일** 직접 대조·정확한 인용 범위 |
| `2024구합76393` / `2026-행정쟁송법\\|2\\|0` | 서울행정법원 공식 [주요판결 게시물](https://www.scourt.go.kr/portal/dcboard/DcNewsViewAction.work?cbub_code=000220&gubun=44&scode_kname=&searchOption=&searchWord=&seqnum=27433), [선고일을 표기한 판결문 소개](https://weverlabor.com/25/?bmode=view&idx=168365725) | 공식 법원 게시물에서 사건 실재/사고사망만인율 판단 확인. **2025-08-21 선고일은 비법원 자료로 교차확인** | 공식 게시물의 **첨부 판결문 PDF 직접 열람**으로 정확한 선고일 재확인·법리/효력 심사 |

- 기계 재검증: [GitHub Actions run 44093049996](https://github.com/nurioni4188/gongin-nomusa-quiz/actions/runs/44093049996) **success**, 3건·3문항·인용 5회 연결 일치, 원고 SHA·최종승인 HOLD 불변.
- 출처·날짜·확인수준: `review/NOMUSA_V23_CASE_3_CORROBORATION_20261117.json`.
- 재현: `python3 scripts/nomusa-v23-case-corroboration-gate.py .`.
- **법령·판례 전문 원전 검토 및 실제 독립 전문가 승인: HOLD (0/328).** 요지문항 30건, 학술원전·실전 필기분량 등의 기존 HOLD를 변경하지 않는다.

## 10. V24 — 요지문항 30개 원문 전사 교체 자동검증 PASS (2026-11-17, 최신 상태)

- 위 §1의 "30개 원문 교체 필요"는 **V23 당시의 미완료 이력**이다. V24에서 2015~2018/2021년 인사노무관리론·경영조직론 30개를 공식 PDF 원본 이미지 참고 전사문으로 교체했다.
- [V24 Actions #44097717695](https://github.com/nurioni4188/gongin-nomusa-quiz/actions/runs/44097717695) **success**: 30개 대상 SHA 변경/298개 불변, Chromium PC 1440·모바일 390/360 검증 성공, `review/NOMUSA_V23_VALIDATION_LEDGER.json` 재생성 및 검토 브랜치 자동 커밋.
- 최신 원장: `storedQuestionIsSummary=0`, `qnetOfficialByteIdentical=328`, `sourceVerifiedQuestion=328`, HIGH 325/MEDIUM 3.
- **2016_p5_q2**는 새 전사 문항의 자동 유사도 MEDIUM(0.80)이므로 독립 PDF 글자별 교열 우선. 나머지 MEDIUM 두 문항은 2019_p4_q3, 2020_p7_q3이며 이번 30개와 무관.
- 2018 경영조직론 Scott 제1문 물음1의 원본 인쇄 배점 **20점**으로 보정했고, 2021년 쓰레기통모형의 '1971년 올슨'은 시험원문대로 유지했다.
- 결과 및 교열 관문: `review/NOMUSA_V24_30_VERBATIM_SOURCE_EXECUTION_20261117.md`, `.claude/skills/nomusa-v24-verbatim-source/SKILL.md`.
- **원문 30개 자동 교체 해결과 글자별 독립 원본 교열은 별개**. 인간 교열 전에는 `HOLD_SOURCE_PROOFREAD` 유지; 시험 당시 법령/판례/학술원전·수기실측·전문가 독립 내용승인 **0/328 HOLD**.

## 11. V25 원본 전사 MEDIUM 3개 재대조 (2026-11-18)

- 기존 V24의 HIGH 325/MEDIUM 3개는 당시 현황으로 보존. V25 공식 PDF 이미지 재대조 후 **HIGH 327/MEDIUM 1**, 요지문항 잔여 **0**, 기존 Q-Net 파일 SHA 일치 **328/328**(V23 원전매니페스트 재사용).
- `2016_p5_q2` 경영조직론 25점: 공식 인쇄문과 V24 전사문 일치. **‘그리고’를 OCR이 ‘그러고’로 잘못 인식**해 8글자 N그램 일치도 0.80(MEDIUM); 전사원문 **변경하지 않음**, 독립 사람 교열 HOLD.
- `2019_p4_q3` 민사소송법: **"【문제 3】 공동소송참가에 관하여 설명하시오. (25점)"**으로 띄어쓰기·문제번호·인쇄 footer 혼입 교정.
- `2020_p7_q3` 민사소송법: **"【문제 3】 유사필수적 공동소송에 관하여 설명하시오. (25점)"**으로 같은 문제 교정.
- V25 [실제 Actions #44161596035](https://github.com/nurioni4188/gongin-nomusa-quiz/actions/runs/44161596035) **success**, 2개 sourceText SHA만 변경/326개 전체 원고 SHA 불변, 기존 E2E PC1440/모바일390·360 PASS, 공식 원전·점수·ID 불변, `review/NOMUSA_V23_VALIDATION_LEDGER.json` 재생성.
- 검토 로그: `review/NOMUSA_V25_MEDIUM_3_EXECUTION_20261118.md`, 원본 시각 근거 `review/NOMUSA_V25_MEDIUM_3_PRIMARY_PAGE_CROSSCHECK_20261118.json`, 재사용 스킬 `.claude/skills/nomusa-v25-three-medium-pdf-proofread/SKILL.md`.
- **미해결:** 독립 원문 글자별 교열, 역사 법령·판례 전문·학술 원서·수기분량·서면 전문가 승인. 최종 내용승인 **0/328 HOLD**, 기존 판례 3건 등 이전 HOLD 보존.

## 12. V26-2·V26-3 전문가 심사준비 및 96개 사전검증 (2026-11-18)

- 기존 2022 P0 19개·32소문항 + 분량 프록시 P1 77개 = **96개**, V23 원고 SHA와 원전후보 및 법령·판례·학술·수식 미확인 쟁점 일대일 연결. [Actions #44169285275](https://github.com/nurioni4188/gongin-nomusa-quiz/actions/runs/44169285275) **success**.
- 328개 전체 7개 과목별 ZIP 및 **빈 전문가 독립심사 회신 서식 328개**, 발송·회신 대장 생성. 실제 이메일 발송 및 전문가 회신 없음.
- ZIP CRC 및 328개 공란 회신서 검증 PASS. artifact [14366582593](https://github.com/nurioni4188/gongin-nomusa-quiz/actions/runs/44169285275/artifacts/14366582593).
- 이 PASS는 **근거후보 라우팅/검증용 패킷 기술 성공**이다. 모든 판결문 전문·시험 당시 연혁법령·학술 원서/원논문·손글씨 장수의 독립 확인을 의미하지 않는다.
- 우선검토 77건의 500자/쪽 프록시는 글자수 추정이며 필기실측 부족 확정이 아니다.
- 다음 HOLD: 독립 원전 글자별 교열, 역사 법령·판례 전문·학술 원저·수기실측·실제 외부 전문가 서면평가. **FINAL_APPROVAL=HOLD, 승인 0/328**.
- 재현: `scripts/nomusa-v26-substantive-review-packets.py`, 스킬 `.claude/skills/nomusa-v26-2-content-review/SKILL.md`, `.claude/skills/nomusa-v26-3-expert-packets/SKILL.md`, 보고서 `review/NOMUSA_V26_2_3_EXECUTION_20261118.md`.

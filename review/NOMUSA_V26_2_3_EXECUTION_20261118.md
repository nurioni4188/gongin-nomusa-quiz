# NOMUSA V26-2·V26-3 자동검증 및 전문가 심사패킷 생성 결과

실행 확인일: **2026-11-18 KST**. 기존 검토 브랜치 `review/nomusa-auto-v1-20year-gate-20261115`, Draft PR #3.

## 결과 — AI 사전검증과 실제 내용승인 분리

**기술검증 PASS / 근거후보 라우팅 PASS / 원판결·연혁법령·학술원전·실제필기·전문가 최종승인 HOLD (0/328).**

- V26-2: 2022년 19개(32소문항) + 단순 글자수 분량 우선검토 77개 = 중복 없는 **96개**. 실제 Chromium 원문·상세·압축을 V23 328문항의 `textSHA256`과 일대일 연결, 법조문 표기·판례번호 및 선고일 후보·학술 저자/원서연도 후보·계산/수식·분량 부족 검토 플래그 생성.
- V26-3: 전체 20개년 328개 답안에 대하여 **7개 과목별 ZIP**, 문항별 원문·상세·압축 답안 **328개**, 검토자 실명·자격·서명·검토일이 비어 있는 **독립전문가 회신 JSON 328개** 작성. 공식 Q-Net 게시물 URL/첨부 구성원 SHA, 구체적인 확인대상, 현재 SHA 고정.
- 과목별 건수: 노동법Ⅰ **34**, 노동법Ⅱ **32**, 행정쟁송법 **45**, 민사소송법 **36**, 노동경제학 **57**, 인사노무관리론 **58**, 경영조직론 **66**. 합계 **328**.
- 공식 문제 원전 파일 SHA 검증 결과는 기존 V23 증빙을 재사용했다. **이 V26 실행에서 Q-Net 첨부파일을 다시 내려받아 새롭게 원전 동일성을 확인한 것은 아님.**
- V26-2 자동 탐지: 96개 중 77개가 단순 분량 프록시 부족이며 91개 원고에 명시적 미확인/HOLD 표현이 존재. 이 숫자는 **오류 확정 건수나 손글씨 장수 미달 확정 건수가 아님**.
- 남은 원문 자동 MEDIUM 1개 `2016_p5_q2`는 2016년 경영조직론 OCR의 ‘그리고/그러고’ 오인식 이력으로 사람 글자별 교열 HOLD.
- 기존 판례 3건 5회 인용의 원판결 전문·시험 당시 적용 법리, 2022년 4개 공식 판시요지의 사안포섭, 모든 독립 전문가 서면승인은 HOLD.

## 재현 및 실제 실행 증빙

- 구현: `scripts/nomusa-v26-substantive-review-packets.py`.
- CI: `.github/workflows/nomusa-v26-2-3-packets.yml`, `ubuntu-24.04`, `permissions.contents: read`, review branch만 대상으로 실행.
- [GitHub Actions run 44169285275](https://github.com/nurioni4188/gongin-nomusa-quiz/actions/runs/44169285275): **completed/success**, 2026-11-17T20:26:15Z ~ 20:27:53Z (**약 98초**).
- [GitHub Actions artifact 14366582593](https://github.com/nurioni4188/gongin-nomusa-quiz/actions/runs/44169285275/artifacts/14366582593): 676개 구성파일, 외부 추출본 ZIP 테스트 CRC PASS, 내부 과목 ZIP 7개 CRC PASS, 328개 빈 회신 서식 수량 PASS.
- 산출 경로: `review-artifacts/NOMUSA_V26/NOMUSA_V26_2_96_CONTENT_PRECHECK.json`, `NOMUSA_V26_2_96_PRECHECK_REPORT.md`, `NOMUSA_V26_2_PRIORITY_2022_19_PLUS_77.zip`, `NOMUSA_V26_3_328_ROUTING.json`, `NOMUSA_V26_3_328_DISPATCH_TRACKER.csv`, `NOMUSA_V26_3_DISPATCH_INDEX.md`, `NOMUSA_V26_3_SUBJECT_ZIPS/*.zip`.
- CI는 기존 Chromium PC1440/모바일390·360, V19 328문항, V21 19+77, V22 원본 SHA와 출력 검증을 재사용했다.
- SHA·문항 ID·기존 V23 Q-Net 매니페스트 파일 불변식 검사 및 `git diff --exit-code` 통과, 검토 브랜치에만 새 코드/스킬/CI를 추가. 데이터 원고, main, Production, 기존 Preview를 수정·직접 배포하거나 이메일 발송하는 명령은 사용하지 않았다.
- **Vercel 연동의 자동배포 발생 여부는 별도 원격 배포 목록 확인 없이 단정하지 않는다.**

## 생성된 재사용 스킬

- `.claude/skills/nomusa-v26-2-content-review/SKILL.md` — P0 19+P1 77 원전/법령·판례·학술·수식·분량 위험 사전검증.
- `.claude/skills/nomusa-v26-3-expert-packets/SKILL.md` — 328개/7과목 ZIP, 검토자 회신 템플릿, 발송·회신 관리.
- 기존 V23/V24/V25 검증 원장 및 Draft PR #3을 이어받아 반복 실행한다.

## 이어서 필요한 실제 검토

1. **2022년 19개**에 대해 시험 당시 법령·부칙·원판결 전체·학술 원저·소문항별 논증과 사례포섭을 독립 대조.
2. **77개 분량 우선검토**는 실제 필기로 시간·장수와 논증 밀도를 측정; 500자/쪽 프록시를 실제 결과로 혼동하지 않는다.
3. 7과목 자료를 실제 독립 전문가에게 전달하고, 자격·서면 의견·날짜·확인 근거·고정 `textSHA256`을 수령한 문항만 승인 후보로 전환.
4. 학습 웹앱의 main·Production·Preview는 지금 변경할 이유가 없으며 **최종승인 HOLD (0/328)** 유지.

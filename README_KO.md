# 공인노무사 기출학습 RC35 — Warm Light Study

**기준: RC34 소스, 채점 데이터 및 문제 이미지 원본 유지.**

- **기본 화면**: 밝은 아이보리 배경과 흰 카드, 차분한 남색/그린 포인트. 눈 피로를 줄이기 위한 낮은 채도의 학습 화면입니다. 다크모드는 원하는 경우에만 화면 밝기 전환 버튼으로 수동 선택하세요.
- **홈**: 전체 진도, 문항별 학습 현황, 연도·과목·범위 선택 및 이어 풀기.
- **문제풀이**: 원문 이미지 보기와 글자 보기, 선택지 5개, 답안 저장, 결과 재검토.
- **오답노트**: 현재 오답, 한 번 이상 틀린 문제, 별표, 메모를 별도 목록으로 표시.
- **PC/모바일**: 1365, 768, 390, 360px에서 UI 자동검증을 수행한 소스입니다. 실제 모바일 실기기 검증을 대신하지 않습니다.
- **보관 위치**: 학습 기록은 브라우저 로컬 저장소에만 있으므로 RC33을 사용한 브라우저와 동일한 출처/주소일 때만 자동으로 이어집니다. 도메인·브라우저가 변경되면 JSON 백업/복원 기능을 사용하세요.

Windows에서 ZIP 전체 압축을 해제하고 `nomusa-quiz-web/윈도우에서_앱실행.cmd`를 더블클릭하세요. 안전한 출처임을 확인한 후 현재 PowerShell에서 파일 차단을 해제할 수 있습니다.

```powershell
Get-ChildItem .\scripts -Filter *.ps1 -Recurse | Unblock-File
.\scripts\run_all_checks.ps1
```

로컬 전체 자동검증은 Python, Node.js, Playwright Chromium을 필요로 합니다. 브라우저 HTTP 시험이 실패하거나 실행 불가인 경우 `run_all_checks.ps1`는 PASS를 출력하지 않습니다. 실제 Preview 배포와 공식 원문 정답검증, 운영 반영은 미실시/HOLD입니다.

---

# 공인노무사 기출학습 RC34 · Focus Study

**디자인 개편 버전:** 기존 RC33의 채점과 문제 데이터를 유지하고 시각적 배치만 개선했습니다.

- 실행: ZIP 전체 압축 해제 후 `nomusa-quiz-web/index.html`을 Chrome 또는 Edge에서 열거나 `윈도우에서_앱실행.cmd` 실행.
- 기본 테마: 다크. 우측의 달 아이콘을 누르면 라이트 모드로 전환됩니다.
- 데스크톱: 왼쪽 사이드바에서 홈·오답노트·검색·통계·출처 선택.
- 모바일: 상단 2줄 메뉴, 연도·과목별 선택과 문제풀이 이어 풀기 지원.
- 로컬 검증: PowerShell에서 `Get-ChildItem .\scripts\*.ps1 | Unblock-File` 후 `.\scripts\run_all_checks.ps1`를 실행합니다. PC Playwright/Chromium 설치 필요.
- 보호 Preview: 별도 검증 후 `.\scripts\deploy_preview_only.ps1`; 반드시 예상 프로젝트 및 SSO 보호 설정 확인. Production 변경 없음.
- **RC34 보호 Preview는 아직 배포하지 않았습니다.** RC33 기존 Preview와 혼동하지 마세요.
- **공식 Q-Net 기출원문·최종정답 독립 대조는 아직 HOLD**입니다. 로컬 검증 PASS는 공식 정답 검증 PASS를 의미하지 않습니다.

# 공인노무사 1차 기출학습 RC33 — PC·모바일 DOM 검증 개선본

**기준 소스:** 사용자가 제공한 `RC31_nomusa_quiz_web.zip`의 `nomusa-quiz-web` 폴더

## 1. 실행

Windows에서는 `윈도우에서_앱실행.cmd`를 더블클릭하거나, `index.html`을 Chrome/Edge로 여세요. 모든 파일을 **같은 폴더 구조**로 압축 해제해야 합니다. 인터넷·서버·Node 설치 없이 개인용 학습 웹이 작동합니다.

- **2022–2023:** 각 연도 150문항(6과목 × 25문항).
- **2024–2026:** 각 연도 240문항(6과목 × 40문항).
- **합계:** 1,020문항(영어 제외), 원문 PNG 1,020개, 정답표 대조 CSV 1,020행.
- `img/`(이미지), `data.js`(문항/정답), `index.html`(앱) 중 하나라도 빠지면 정상 실행되지 않습니다.
- 모바일에서는 웹 호스팅이 편리하지만, 기출문제 이미지를 **공개 사이트/공개 저장소에 게시하지 않는** 비공개 환경을 권장합니다. 정적 배포 자체가 비공개를 보장하지는 않습니다.

### 홈 화면에서

연도, 과목, 범위(전체/미풀이/오답/재오답/별표), 문제 순서, 문항 수, 연습/실전을 선택하세요. 진행 중인 시험이 있다면 화면 상단의 **이어서 풀기**를 선택할 수 있습니다.

## 2. RC31 → RC32 개선 내용 (그대로 유지)

1. 실전시험 마지막 문항·제출 버튼에서 **미응답 문항 수 확인 후 제출**. 취소도 가능.
2. 실전시험의 의도치 않은 **답 선택 후 자동 다음 문항 이동** 제거.
3. 연습·실전 진행 상태 자동 저장 및 새로고침·화면 이동 후 **이어서 풀기**. 실전시험의 타이머는 화면 이탈/새로고침 중에도 실시간 기준으로 계속 흐름.
4. 결과 목록에서 특정 문항을 열어도 **이전 답안과 기록을 유지하는 재검토 모드**. 중복 채점 방지.
5. 문항 위치 직접 이동/240문항 이하 문항 이동판, 답변 완료·별표 표시.
6. **JSON 백업 실제 다운로드**, 가져오기 전 덮어쓰기 확인, 비정상/미등록 문제 ID 데이터 걸러내기.
7. 360/390px 모바일을 고려한 메뉴·버튼·표·문항 UI CSS 정비(실제 모바일 렌더링 재검증은 필요).
8. PWA 매니페스트/아이콘 및 HTTPS 환경에서의 선택적 오프라인 캐시(처음 열린 문제 이미지부터 캐싱).
9. 기술 무결성 검사 스크립트, Node 회귀시험, 브라우저 자동시험 스크립트 및 검증 기록 추가.

## 3. 검증 범위와 판정

| 게이트 | 결과 | 해석 |
|---|---|---|
| 전체 1,020문항 데이터 구조·CSV 정답 매핑·PNG 존재/크기 | **PASS** | 파일 내부 자료를 기준으로 한 기술적 일치성. 오류 0건 |
| Node 코드 기반 채점·저장·복원·재검토 등 회귀시험 | **PASS 11/11** | DOM/브라우저 표시를 대체하지 않음 |
| 실제 Chrome/Edge 화면, 360·390px 모바일 실측 | **HOLD** | 현재 검증 환경의 Chromium URLBlocklist에 의해 페이지 열기 차단. PC/모바일 실제 재시험 필요 |
| Q-Net 원문 기출 PDF/HWP 및 최종정답과의 **독립 재검증** | **HOLD** | 이번 입력 ZIP에는 원본 PDF/HWP가 없어서 원문과 새로 대조하지 못함 |
| Vercel 보호 Preview/Production 게시 | **미실시** | 비공개 배포 권한/환경을 임의로 변경하지 않음 |

RC31 문서의 기존 확인 기록에 따르면 1,019문항 일치, 2025 노동법(1) 3번 ③→④ 정정, 복수정답 4건입니다. **RC32는 원래 문항·정답을 임의 변경하지 않았습니다.** 원본 Q-Net PDF/HWP가 확보되면 별도 대조하여 정답의 출처 신뢰도를 높여야 합니다.

검증 로그: `uat-evidence/source_integrity_rc32.json`, `uat-evidence/logic_regression_rc32.json`, `uat-evidence/browser_smoke_rc32.json`

## 4. 검증 재실행

Node.js가 설치되어 있으면 아래 명령을 `nomusa-quiz-web` 폴더에서 실행할 수 있습니다.

```powershell
node tests/logic_smoke.js
python scripts/check_integrity.py
```

브라우저 실화면 시험은 Python의 `playwright` 및 Chromium 설치가 필요하며, 인터넷/로컬 페이지 사용을 차단하지 않는 환경에서 아래를 실행하세요.

```powershell
python -m pip install playwright
python -m playwright install chromium
python tests/smoke_ui.py
```

실제 브라우저 시험이 통과하면 360/390px 수평 넘침, 연습 채점, 실전 제출, 결과 재검토, JSON 다운로드가 자동 확인됩니다. **브라우저 테스트 로그가 HOLD인 상태를 PASS로 간주하지 마세요.**

## 5. 주의사항

- 학습 기록은 **브라우저별 로컬 저장소**에 저장됩니다. 정기적으로 `통계 → JSON 백업 다운로드`를 사용하세요. 백업 가져오기는 기존 완료 기록을 덮어쓰며, 진행 중 미제출 시험은 복원하지 않습니다.
- `data.js` 및 `img/`에 기출문제 원문이 포함되어 있습니다. 공개 GitHub 저장소·무인증 공개 배포는 지양하세요. 현재 포함된 `vercel.json` 설정만으로 비공개 배포가 보장되지는 않습니다.
- 법령 개정에 따라 과거 시험의 정답 판단이 현재 법령과 다를 수 있습니다. 실제 최종정답은 Q-Net 공식 공고가 기준입니다.
- `index.html`을 직접 여는 모드는 오프라인으로 실행되며, 설치형 앱(PWA) 기능은 HTTPS로 호스팅할 때만 작동합니다.


## 6. RC33 추가 개선 및 배포 게이트

- **기능 오류 수정:** 검색·오답 목록에서 문항을 클릭했을 때 진행 중 시험이 있으면 교체 확인을 먼저 받고, 승인 이후에 정확한 선택 문항으로 이동합니다. 진행 중 시험은 확인 전에 손대지 않습니다.
- **키보드 접근성 수정:** Enter를 이용한 접기/펼치기(`summary`)와 버튼 조작 중 전역 단축키가 문제를 이동시키지 않습니다.
- **Chromium 브라우저 렌더링 시험:** `python tests/browser_dom_ui.py` 실행 시 실제 Chromium 엔진에 HTML·JS를 주입하고 PC 1365px, 모바일 360·390px, 태블릿 768px 화면·채점·제출·이어풀기·검색·백업·PNG 디코딩을 시험합니다. 전체 15개 검사항목 PASS. 캡처: `uat-evidence/rc33_*_*.png`.
- **중요한 검증 한계:** 관리형 Chromium의 `ERR_BLOCKED_BY_ADMINISTRATOR`로 `http://127.0.0.1`, `file:` 등 주소 탐색은 제한됩니다. HTML DOM 주입 시험 PASS는 실제 URL의 HTTP 서빙, 원격 인증, 모바일 실기기, PWA 설치, 최종 사용자 승인 PASS가 아닙니다. 실제 URL 시험(`python tests/smoke_ui.py`)은 HOLD입니다.
- **원격 배포:** RC33 전체(특히 이미지 1,020개)를 현재 채팅 환경에서 Vercel로 전송하지는 못했습니다. `scripts/deploy_preview_only.ps1`은 사용자의 Windows에서 Vercel CLI 인증 후 실행하는 **Preview 전용** 배포 스크립트입니다. 기존 보호 프로젝트 `gongin-nomusa-rc27-preview`의 인증 설정을 배포 전에 재확인하고, 바뀌었거나 조회되지 않으면 실패 처리합니다.
- **Production:** 명시적으로 금지. 최종 Human UAT/독립 Q-Net 원문 대조는 HOLD.

Windows에서 실제 로컬 브라우저 검증은 `powershell -ExecutionPolicy Bypass -File .\scripts\run_all_checks.ps1` 으로, 보호 Preview 배포는 위 단계가 PASS한 뒤 `powershell -ExecutionPolicy Bypass -File .\scripts\deploy_preview_only.ps1` 로 수행할 수 있습니다. 전제 조건: Vercel CLI 설치 및 연결된 Vercel 계정 로그인. 토큰을 텍스트 파일에 적거나 공유할 필요가 없습니다.

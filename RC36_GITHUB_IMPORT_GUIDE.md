# RC36 전체 소스 1회 업로드 안내

**브랜치:** `rc36/preview-law-ai` (다른 브랜치에서는 중단)

- PC에서 GitHub Desktop으로 `nurioni4188/gongin-nomusa-quiz` 저장소를 복제하고 `rc36/preview-law-ai` 브랜치를 선택합니다.
- 이 대화의 파일 `RC36_GITHUB_DESKTOP_IMPORT_READY.zip`을 별도 폴더에 압축 해제합니다.
- 그 폴더 **내부 파일 전체**를 GitHub Desktop의 저장소 루트로 복사해 기존 파일을 덮어씁니다. 바깥쪽 폴더/ZIP 자체를 복사하지 마세요.
- `index.html`, `data.js`, `api/_data/questions.json`, `api/health.js`, `api/law.js`, `api/explain.js`, `img/` 존재를 확인합니다.
- `vercel.json`은 `git.deploymentEnabled=false`를 **그대로 유지**합니다. 기존 Production은 변경하지 않습니다.
- GitHub Desktop에서 `Commit to rc36/preview-law-ai` → `Push origin`을 실행합니다.
- 완료 후 ChatGPT에게 `RC36 전체소스 업로드 완료, 원격 GitHub 확인 후 다음 단계 진행`이라고 요청합니다.

### 검증 값

- 원본 ZIP SHA256: `584a179be7e1df598d4a964ffc08bcbbbac55bba607abd0acb89b5a6e3ea10cb`
- 원본 파일 1,092개, PNG 1,041개, 1,020문항
- 평탄화 패키지 내 원본 1,092개 파일의 내용 SHA256 비교: **1092/1092 MATCH**
- 오프라인 RC36 Node.js 서버 함수 모의시험 **6/6 PASS**
- 외부 API 실호출, 공식 정답·출제 당시 법령 검증, Vercel Git 연결, Preview 배포: **HOLD**

**Git 자동연결 전 주의:** 기존 Vercel 프로젝트에는 Production 기록이 있으며 GitHub `main`이 RC36/RC35와 다른 구버전입니다. Git 연결 전에 Production 브랜치 격리/자동배포 정책을 반드시 점검해야 합니다.

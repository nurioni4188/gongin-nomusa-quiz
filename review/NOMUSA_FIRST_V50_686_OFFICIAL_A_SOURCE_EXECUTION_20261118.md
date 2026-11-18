# 공인노무사 1차 686 미편입 A형 V50 공식 원본 소스 확장 — 실행결과

**검증일:** 2026-11-18 (KST)  
**작업위치:** `nurioni4188/gongin-nomusa-quiz` / `review/nomusa-auto-v1-20year-gate-20261115` / 기존 Draft PR #3  
**GitHub Actions:** [V50 #44281435756](https://github.com/nurioni4188/gongin-nomusa-quiz/actions/runs/44281435756) — **completed/success**  
**전체 증빙:** [V50 Artifact #14416887431](https://github.com/nurioni4188/gongin-nomusa-quiz/actions/runs/44281435756/artifacts/14416887431) — 686행 JSON/CSV, 공식 A형 원본 3개 PDF 검토자료.

## 실제 근거 확보

| 검증한 A형 공식 원본 | 문항 ID의 공식 문제지 파일 연결 | 확인된 파일 해시 |
|---|---:|---|
| 2016년 경제학원론 A형 PDF, 37쪽 | **25개** | `eb20585599fee9541ea5eae5ad7d56e87cba75a4c6fe1ed674f7280e43a3ac5e` |
| 2018년 경영학개론 A형 PDF, 37쪽 (Q-Net ZIP에서 추출) | **2018년 150문항 중 비경제학 영역** | `5666e3e99d5eba68cff47f41a8c3c957fd88b9398991c6aa3c4238c34476b5de` |
| 2018년 경제학원론 A형 PDF, 38쪽 (Q-Net ZIP에서 추출) | **2018년 150문항 중 경제학 영역** | `8b7ad8b5ca85bd7cfa5d616ccd3fef3e0e2728b26a4d873468958b4da4978ad8` |
| **공식 원본 문제지 추가 연결** | **175개** | **3/3 원본 PDF SHA-256 검증** |

Q-Net 공식 2018년 A/B 원본은 ZIP 2개에 섞여 있었고, 파일 이름에 나타난 A형 원본을 선택해 PDF SHA를 고정했다. 원본 다운로드의 2026-11-18 기록은 `review/NOMUSA_FIRST_V49_ARCHIVE_DISCOVERY_SUMMARY_20261118.json`에 연결돼 있다. **A형임을 개별 인쇄 면·문항번호와 시각 대조한 것은 아직 아니다.**

## 686문항 대상 소스 커버리지

- 기존 V48 2020·2021년 193문항 PDF 링크 및 V42 법률 2개 crop = **195개 공식 원본 문제지 연결**
- 이번 V50 2018년 150 + 2016년 경제학 25 = **175개 추가 공식 원본 문제지 연결**
- 따라서 총 **370/686개는 연도·선택과목 수준의 공식 Q-Net PDF SHA가 연결됨**. 개별 문제의 정확한 페이지와 글자 단위 교열·①~⑤·그래프·공식 최종 정답표 셀까지 검증된 문항 수가 아니다.
- 남은 **316개는 공식 원본 PDF 링크 미확보**. 그중 2013년 150개는 외부 미러 PDF SHA 후보만 확보했고 공식 Q-Net 동일성을 검증하지 못했다. 그 외 166개는 해당 수준의 외부 미러조차 연결되지 않은 상태다.
- 공식 문제지 원본은 직접 확보했으나 문제별 전체 지문·선택지·수식·법령·학술 근거 및 독립 전문가 승인은 **0**.

## 안전·다음 관문

- 기존 V48 **67개 잠정 crop**은 원본 이미지 경계·①~⑤·공통지문·도표·수식을 직접 확인해야 한다. 추가 175개는 V51 페이지 앵커 탐색의 다음 대상이다.
- `review/NOMUSA_FIRST_V50_686_OFFICIAL_SOURCE_SHA_SUMMARY_20261118.json`에 숫자·SHA·출처 상태 기록.
- `review/NOMUSA_FIRST_V44_VERIFIED_APPROVALS.json`의 독립 승인 기록 **0**, 신규 QDATA·자동채점 **0**.
- `main`, 기존 Preview·Production, 기존 1·2차 문제 ID, 저장키, 2차 328답안은 변경하지 않음. 기존 Draft PR #3 미병합.

**정확한 판정: 공식 원본 문제지 추가 연결 175건 PASS / 독립 원문·법령·선택지 해설 최종승인 HOLD / 신규 배포 없음.**

# NOMUSA V22 최종 원전대조·전문가 심사패킷 자동생성 실행보고

**2026-11-17**, 기존 GitHub 검토 브랜치 / Draft PR #3, 변경된 원본 문제지·문항 ID·저장키·main·Production·Vercel Preview 없음.

## 실제 자동실행 PASS 및 소요시간

- [GitHub Actions 실제 완료](https://github.com/nurioni4188/gongin-nomusa-quiz/actions/runs/44061790296) — completed/success, 실행 커밋 `a19e105c42a9354b1392532c130a9e2d7319d10a`.
- 실행 2026-11-17 10:06:56~10:08:16 UTC. 전체 GitHub Actions 경과 **80초**, V22 원전대조 스크립트 자체 소요 **1.002초**. 이 수치는 전문가 검토 시간과 무관.
- [ZIP 증빙 아티팩트](https://github.com/nurioni4188/gongin-nomusa-quiz/actions/runs/44061790296/artifacts/14317919103) — 총 37개 파일(원전 매핑·심사패킷·PDF 페이지 이미지·공식 판례 교차대조 등).
- 검토 브랜치: `review/nomusa-auto-v1-20year-gate-20261115`. GitHub main SHA `9ea46fc9134c55a4312241b55a82b237e86ed4a8` 불변, Draft PR #3 미병합.

## 328개 원전 후보 4개 구간(상호배타)

| 구분 | 수 | 판단 |
|---|---:|---|
| 2022년 문항별 PDF 텍스트 유사도 높은 후보 | 19 | 과목별 7개 PDF 19/19 텍스트 겹침 높음(대부분 1.0), 시각·원본 동일성 확인은 추가 |
| 원전 PDF 후보 경로·바이너리 존재 | 209 | 저장소 파일 SHA 기록. 공식 첨부와 해시 동일성은 미확인 |
| 2021년 1·2일차 PDF 후보 둘 다 가능 | 6 | 날짜·과목과 페이지를 확인해 분리해야 함 |
| 2007~2012년 기출 HWP 원본 바이너리 없음 | 94 | 과거 명세서에 파일 해시 기록만 존재; 원본 복구·대조 전 HOLD |
| **합계** | **328** | **최종 내용승인 0/328** |

## 2022년 독립심사 파일럿

- 원본 PDF 저장소 파일 7개 존재, 2022년 19개 문항 각각 PDF 기계적 텍스트 일치도 높음. 이는 원본 PDF를 **독립적으로 Q-Net 첨부 ZIP과 해시 대조한 결과가 아니다.**
- 2022년 19개 문항별 원문 전사·소문항 배점·상세/압축 답안·SHA256 고정·검토 체크리스트를 포함한 Markdown 전문 심사패킷 생성.
- 모든 2022년 원본 PDF 페이지 미리보기 PNG 생성, 눈으로 그래프·도표·배점·인쇄 원문 대조용.
- 대법원 공식 자료 기준 판례 4건(3문항 연결): 2019다238053, 2019두52386, 2021두46285, 2017도2478의 사건번호·선고일·판시요지 교차 확인. 사건의 사실관계에 대한 최종 포섭과 판결문 전문·법령시점 전수 대조, 전문가 서면검토는 HOLD.
- 공식 Q-Net 2022 문제지 게시물: https://www.q-net.or.kr/cst003.do?artlSeq=5210985&boardId=Q004&gId=05&gSite=L&id=cst00302

## 재사용 스킬 및 원전/검토 자동화

- 스킬: `.agents/skills/nomusa-v22-primary-source-expert-gate/SKILL.md`
- CI: `.github/workflows/nomusa-v22-primary-expert-packets.yml`
- 엔진: `scripts/nomusa-v22-original-expert-packets.py`
- 판례 근거: `review/NOMUSA_V22_2022_OFFICIAL_PRECEDENT_CROSSCHECK.json`
- 기존 승인 양식: `review/NOMUSA_V21_INDEPENDENT_REVIEW_TEMPLATE.json`

## 최종승인을 위한 진짜 남은 일

1. 공식 Q-Net ZIP의 원본 파일 SHA256과 저장소 PDF 동일성/분할 여부 확인.
2. 2021년 6개 문항의 일차별 정확한 PDF와 페이지 매칭.
3. 2007~2012년 원본 HWP 바이너리 6개 연도별 복구 및 94개 문항 대조.
4. 실제 시험 당시 법령·부칙·판례 전문 및 학술 원전·경제학 수식 전수 검증.
5. 필기 답안지 50점 8~10장/25점 4장 실측 및 **외부 독립 전문 검토자의 실명·자격·검토일·근거·서면 승인** 입력.
6. 답안 원문 SHA가 바뀌면 기존 승인 잠금 해제 후 해당 문항 재심사.

**V22 판정: 원전 후보 매핑·PDF 비교·패킷 자동생성 PASS, 공식 문제지 동일성/법리·학술 전수 승인/수기분량/독립 전문가 최종내용승인 HOLD.**

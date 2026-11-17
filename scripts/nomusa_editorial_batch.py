"""Reusable NOMUSA editorial exporter: live Chromium canonical projection → MD/JSON.
No deployment, no content/legal approval, no rewriting source IDs.
Called by the repository's existing Playwright gate for requested years.
"""
from __future__ import annotations
import json
from pathlib import Path


def export_editorial_years(page, root, years=(2023, 2025)):
    years = tuple(int(y) for y in years)
    if len(years) != len(set(years)) or not all(2007 <= y <= 2026 for y in years):
        raise ValueError("Invalid or duplicate exam year")
    document = page.evaluate("""(years) => {
      const catalog=window.N27_CATALOG?.items||[];
      const canonical=window.NOMUSA_CANONICAL_SELECTION_V1?.items||{};
      const gates={2022:window.NOMUSA_V168_2022_GATE,2023:window.NOMUSA_V169_GATE,2025:window.NOMUSA_V169_GATE};
      return years.map(year=>({
        year,gate:gates[year]?.status||'HOLD_UNVERIFIED_EDITORIAL_GATE',
        rows:catalog.filter(q=>q.year===year).map(q=>{
          const a=canonical[q.id]||{};
          return {id:q.id,year:q.year,subject:q.subject,points:q.points,
            title:q.topic||'',sourceText:q.sourceText||'',
            parts:a.examPartRubricV169||a.examPartRubricV168||[],
            detailed:a.detailed||'',compressed:a.compressed||'',
            originalLength:a.detailedBeforeV169?.length||a.detailedBeforeV168?.length||0,
            approval:a.finalAcademicApproval||'HOLD',
            scoringApproved:!!a.scoringApproved};
        })}));
    }""", list(years))
    root=Path(root)
    output=root/"review-artifacts"
    output.mkdir(parents=True,exist_ok=True)
    manifest={"schema":"nomusa-editorial-batch/1","years":[],"contentApproval":"HOLD",
              "handwrittenPagesVerified":False,"productionChanged":False,"previewDeployed":False}
    files=[]
    for record in document:
        year=record["year"]
        rows=record["rows"]
        expected={2022:(19,32),2023:(19,32),2025:(19,37)}.get(year)
        ids=[r["id"] for r in rows]
        if not rows or len(ids)!=len(set(ids)):
            raise AssertionError(("MISSING_OR_DUPLICATE_IDS",year,ids))
        if expected and len(rows)!=expected[0]:
            raise AssertionError(("QUESTION_COUNT",year,len(rows),expected[0]))
        partcount=sum(len(r["parts"]) for r in rows)
        if expected and partcount!=expected[1]:
            raise AssertionError(("SUBQUESTION_COUNT",year,partcount,expected[1]))
        if not all(r["detailed"] and r["compressed"] and r["originalLength"]>0
                   and r["sourceText"] and not r["scoringApproved"]
                   and sum(p["points"] for p in r["parts"])==r["points"] for r in rows):
            raise AssertionError(("BAD_OR_APPROVED_ANSWER",year))
        full=sum(len(r["detailed"]) for r in rows)
        char_goals=[(r["id"],len(r["detailed"]),
                    4000 if r["points"]==50 else 2000) for r in rows]
        deficits=[{"id":name,"chars":length,"studyProxyMinimum":target}
                  for name,length,target in char_goals if length<target]
        lines=[
            "# 공인노무사 2차 "+str(year)+"년 — 통합 편집후보 답안",
            "",
            "> **학습용 편집후보: 법령·판례·학술 최종 내용승인 HOLD**",
            "> 브라우저에 실제 등록된 통합 상세·압축답안 전문을 기록했습니다.",
            "> 기출은 원장 전사이므로 원본 PDF·표·그래프 시각 대조와 시험 당시 법령 전문 확인은 별도입니다.",
            "> 목표 장수는 필기속도·필체·답안지 서식을 실측한 값이 아닙니다.",
            "", "## 전체 소문항 점수·장수 설계",
            "", "| 문항 ID | 과목 | 소문항 | 배점 | 목표 수기 장수 |",
            "|---|---|---|---:|---:|"
        ]
        for r in rows:
            for p in r["parts"]:
                lines.append("| "+r["id"]+" | "+r["subject"]+" | "+p["title"].replace("|","/")+
                             " | "+str(p["points"])+" | "+
                             str(p["minimumPages"])+"–"+str(p["maximumPages"])+" |")
        for index,r in enumerate(rows,1):
            lines.extend(["","---","",
                "## "+str(index)+". "+r["subject"]+" — "+r["id"]+" ("+str(r["points"])+"점)",
                "", "### 기출 원문(원장 전사·PDF 시각대조 HOLD)","",r["sourceText"],
                "", "### 소문항별 실전 목표"])
            for p in r["parts"]:
                lines.append("- **"+p["title"]+"** ("+str(p["points"])+"점): 목표 "+
                             str(p["minimumPages"])+"–"+str(p["maximumPages"])+"장")
            lines.extend(["", "### 상세답안 — 최신 앱 표시 원고","",r["detailed"],
                          "", "### 압축답안 — 최신 앱 표시 원고","",r["compressed"],
                          "", "**내용 독립승인 HOLD / 수기분량 HOLD / 시험 당시 근거 전문대조 HOLD**"])
        prefix="nomusa_"+str(year)+"_"+str(len(rows))+"questions_"+str(partcount)+"parts"
        md=output/(prefix+"_editorial_candidate.md")
        js=output/(prefix+"_rendered_review.json")
        md.write_text("\n".join(lines)+"\n",encoding="utf-8")
        js.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding="utf-8")
        files.extend([str(md.relative_to(root)),str(js.relative_to(root))])
        manifest["years"].append({"year":year,"questions":len(rows),"subquestions":partcount,
            "detailedCharacters":full,"proxyDeficits":deficits,"gate":record["gate"],
            "approval":"HOLD","output":[str(md.relative_to(root)),str(js.relative_to(root))]})
    manifest_path=output/("nomusa_"+("_".join(map(str,years)))+"_editorial_manifest.json")
    manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
    files.append(str(manifest_path.relative_to(root)))
    return {"status":"PASS_EDITORIAL_EXPORT_APPROVAL_HOLD","files":files,"manifest":manifest}

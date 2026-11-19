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


def export_remaining_years(page, root):
    """Export the 17 remaining years from the actual canonical browser model, not base catalog rows.

    Legacy 2013-2018 parent entries are not mistakenly double-counted as independently authored
    children. Independently scored 2024/2026 items are kept as their own source IDs.
    """
    years=[*range(2007,2022),2024,2026]
    expected={2007:13,2008:14,2009:14,2010:17,2011:17,2012:19,
              2013:19,2014:19,2015:6,2016:6,2017:6,2018:6,
              2019:19,2020:19,2021:6,2024:34,2026:37}
    source=page.evaluate("""(years) => {
      const c=window.NOMUSA_CANONICAL_SELECTION_V1?.items||{};
      const original=new Map((window.N27_CATALOG?.items||[]).map(q=>[q.id,q]));
      const audit=window.NOMUSA_V17_REMAINING_GATE;
      const pointGate=window.NOMUSA_V18_POINTS_GATE;
      return {scoreEvidence:{status:pointGate?.status||'HOLD_MISSING_V18_GATE',count:pointGate?.count||0,ids:(pointGate?.rows||[]).map(x=>x.id)},
        gate:{status:audit?.status||'HOLD_MISSING_V17_GATE',
          yearCount:audit?.yearCount||0,questionCount:audit?.questionCount||0,
          years:years.map(year=>({year,status:audit?.years?.[year]?.status||'HOLD',
              issues:audit?.years?.[year]?.issues||[]}))},
        rows:Object.values(c).filter(a=>years.includes(Number(a.year))).map(a=>{
          const q=original.get(a.id);
          return {id:a.id,year:Number(a.year),subject:a.subject,
            topic:q?.topic||'',sourceText:q?.sourceText||'',
            sourceStatus:q?.sourceStatus||'UNVERIFIED',
            points:Number(a.verifiedPointsV18||q?.points||0)>0?Number(a.verifiedPointsV18||q?.points):null,
            originalPoints:q?.points??null,parts:a.examPartRubricV18||a.examPartRubricV17||[],
            scoreEvidence:a.sourceScoringProofV18||null,
            detailed:a.detailed||'',compressed:a.compressed||'',
            preserved:!!a.detailedBeforeV17,
            sourcePath:a.sourcePath||'',
            scoringApproved:!!a.scoringApproved};
        })};
    }""", years)
    records=source["rows"]
    point_evidence_ids=set(source.get("scoreEvidence",{}).get("ids",[]))
    if len(point_evidence_ids)!=26 or source.get("scoreEvidence",{}).get("status")!="26_EXAM_POINT_EVIDENCES_MATCHED_CONTENT_HOLD":
        raise AssertionError("MISSING_26_PDF_SCORE_EVIDENCE")
    root=Path(root);output=root/"review-artifacts";output.mkdir(parents=True,exist_ok=True)
    manifest={"schema":"nomusa-remaining-17-years/1","source":"Chromium canonical model",
              "years":[],"issues":[],"editorialApproval":"HOLD",
              "originalPDFVisualReview":"HOLD","historicLawFullTextReview":"HOLD",
              "handwritingVerified":False,"mainChanged":False,"productionChanged":False,
              "pointCorrections":len(point_evidence_ids),"pointSource":"2019/2020 historical exam-paper PDF mirror visual + catalog text"}
    files=[]
    for year in years:
        rows=[q for q in records if q["year"]==year]
        year_gate=next((x for x in source["gate"]["years"] if x["year"]==year),{"issues":["MISSING_YEAR_GATE"]})
        errors=[e for e in year_gate.get("issues",[]) if not (e.endswith(":POINTS_UNVERIFIED") and e.split(":",1)[0] in point_evidence_ids)]
        if len(rows)!=expected[year]:errors.append("YEAR_COUNT_%d_EXPECT_%d"%(len(rows),expected[year]))
        ids=[q["id"] for q in rows]
        if len(ids)!=len(set(ids)):errors.append("DUPLICATE_IDS")
        for q in rows:
            if not q["sourceText"]:errors.append(q["id"]+":NO_SOURCE_TEXT")
            if not q["detailed"] or not q["compressed"]:errors.append(q["id"]+":ANSWER_MISSING")
            if not q["preserved"]:errors.append(q["id"]+":NOT_PROCESSED")
            if q["points"] is None:
                if q["id"]+":POINTS_UNVERIFIED" not in errors:
                    errors.append(q["id"]+":POINTS_UNVERIFIED")
            elif sum(p["points"] or 0 for p in q["parts"])!=q["points"]:
                errors.append(q["id"]+":SCORE_MISMATCH")
            if q["scoringApproved"]:errors.append(q["id"]+":SCORING_APPROVED_UNEXPECTEDLY")
        split_unverified=sum(1 for q in rows if not all(p.get("splitVerified") for p in q["parts"]))
        part_count=sum(len(q["parts"]) for q in rows)
        lines=[
            "# 공인노무사 2차 "+str(year)+"년 통합 학습답안 편집후보",
            "","> **최종 법률·학술·실전분량 승인 HOLD**",
            "> 현재 학습 웹앱에 실제 투영된 등록 답안 전문입니다.",
            "> 소문항 배점이 분리 확인되지 않은 과거 자료는 원장 전체 배점으로 보존했으며",
            "> 임의 소문항 점수·본문·근거를 만들어 넣지 않았습니다.",
            "", "## 문항·분량 검토 원장","",
            "| ID | 과목 | 배점 | 소문항/배점 단위 | 수기 목표 |",
            "|---|---|---:|---|---|"
        ]
        for q in rows:
            partdesc=", ".join(p["title"]+" ("+(str(p["points"])+"점" if p["points"] is not None else "배점 미확정")+")" for p in q["parts"])
            goaldsc=", ".join((str(p["minimumPages"])+"–"+str(p["maximumPages"])+"장") if p["minimumPages"] is not None else "장수 HOLD" for p in q["parts"])
            lines.append("| "+q["id"].replace("|","/")+" | "+q["subject"]+
                         " | "+(str(q["points"]) if q["points"] is not None else "미확정")+" | "+partdesc.replace("|","/")+
                         " | "+goaldsc+" |")
        for i,q in enumerate(rows,1):
            lines.extend(["","---","",
              "## "+str(i)+". "+q["subject"]+" — "+q["id"].replace("|","/")+" ("+(str(q["points"])+"점" if q["points"] is not None else "배점 미확정")+")",
              "", "### 기출 원장 전사(원본 PDF·HWP 시각 확인 HOLD)", "", q["sourceText"],
              "", "### 배점·실전 장수 목표", ""])
            for p in q["parts"]:
                lines.append("- "+p["title"]+" ("+(str(p["points"])+"점" if p["points"] is not None else "배점 미확정")+"): "+
                    ((str(p["minimumPages"])+"–"+str(p["maximumPages"])+"장") if p["minimumPages"] is not None else "목표 장수 HOLD")+
                    ("" if p.get("splitVerified") else " — 소문항별 분할 검증 HOLD"))
            lines.extend(["", "### 상세답안 — 브라우저 표시 통합본","",q["detailed"],
               "", "### 시험장 압축답안 — 브라우저 표시 통합본","",q["compressed"],
               "", "**내용 최종승인 HOLD / 실제 필기분량 HOLD**"])
        base="nomusa_"+str(year)+"_editorial"
        md=output/(base+"_candidate.md")
        jfile=output/(base+"_rendered.json")
        md.write_text("\n".join(lines)+"\n",encoding="utf-8")
        jfile.write_text(json.dumps({"year":year,"rows":rows,"issues":errors},
            ensure_ascii=False,indent=2),encoding="utf-8")
        files.extend([str(md.relative_to(root)),str(jfile.relative_to(root))])
        info={"year":year,"questions":len(rows),"scoringUnits":part_count,
              "unverifiedSubquestionSplits":split_unverified,"issues":errors,
              "detailChars":sum(len(q["detailed"]) for q in rows),
              "status":"EDITORIAL_EXPORTED_CONTENT_HOLD" if not errors else "EDITORIAL_EXPORTED_WITH_SOURCE_GAPS_HOLD",
              "files":[str(md.relative_to(root)),str(jfile.relative_to(root))]}
        manifest["years"].append(info)
        manifest["issues"].extend(str(year)+":"+e for e in errors)
    if len(records)!=271:manifest["issues"].append("TOTAL_COUNT_%d_EXPECT_271"%len(records))
    manifest["totalQuestions"]=len(records)
    manifest["yearCount"]=len(years)
    manifest["totalScoringUnits"]=sum(x["scoringUnits"] for x in manifest["years"])
    manifest["status"]="EXPORT_PASS_CONTENT_HOLD" if not manifest["issues"] else "EXPORT_PARTIAL_SOURCE_HOLD"
    json_file=output/"nomusa_remaining_17years_editorial_manifest.json"
    json_file.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
    files.append(str(json_file.relative_to(root)))
    return {"status":manifest["status"],"manifest":manifest,"files":files}

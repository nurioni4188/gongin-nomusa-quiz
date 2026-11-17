#!/usr/bin/env python3
"""NOMUSA V23 validation ledger (328 answers, 2007~2026).

Reuses V22 loading (browser-rendered rows + V21 textSHA256 lock) and adds:
  1. Official Q-Net attachment identity (byte SHA-256 vs review/NOMUSA_V23_QNET_OFFICIAL_MANIFEST.json)
  2. Official question text per item (PDF text layer / cached Tesseract OCR / decrypted HWP)
     and Hangul n-gram overlap + points-token check; manual source review overrides
  3. Case citations vs 국가법령정보센터 search cache (existence, court, decision date,
     stated-date match, decision after exam date)
  4. Statute time-effect flags (keyword table; effective dates are AI-supplied, HOLD until law.go.kr check)
  5. Scholar/book-year pairs (AI pre-check only; never SOURCE_VERIFIED)
  6. Arithmetic + SymPy identity-chain re-evaluation; manual economics recalculations
Nothing here is an expert approval. FINAL_APPROVAL stays HOLD for all 328.
"""
from __future__ import annotations
import argparse, csv, hashlib, importlib.util, json, re, sys, time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from nomusa_v23_source_text import source_text  # noqa: E402
from nomusa_v23_arith_check import check as arith_check, check_symbolic  # noqa: E402

REVIEW_DATE = "2026-11-17"
CASE = re.compile(r"((?:19|20)\d{2})\s?(다|두|도|누|마|그|후|재|카|므|스|노|구합|구단|가합|나|헌마|헌바|헌가|헌라|추|모|드|르|무|아)\s?(\d{2,6})")
DATE_BEFORE = re.compile(r"((?:19|20)\d{2})\.\s?(\d{1,2})\.\s?(\d{1,2})\.?\s*(?:선고|자)?\s*$")
AY = re.compile(r"([A-Z][A-Za-z\-\.& ]{1,40}?)\s?[\(（]\s?((?:18|19|20)\d{2})[a-z]?\s?[\)）]")
POINTS = re.compile(r"\(\s*(\d{1,2})\s*점\s*\)")
POST_NOTE = re.compile(r"시험\s?(후|이후|뒤)|사후|현행|개정\s?후|참고|당시에는|당시\s?법|이후\s?(개정|판례|판결)")
HANGUL = re.compile(r"[^가-힣]")

# Known exam dates (day 1) taken from official attachment folder names; others: window Jul–Sep.
# Text layer present but token order scrambled (digits detached from '점'): points are read from OCR.
SCRAMBLED_TEXT_LAYER = {"source_pdf/2013/2013_second_full_original.pdf"}
EXAM_DATES = {2020: "2020-08-15", 2022: "2022-09-03", 2024: "2024-08-31"}

# Statute time-effect keyword table. Effective dates are AI-supplied (model knowledge) and must be
# confirmed on law.go.kr 연혁법령 before any correction is applied.
STATUTE_EVENTS = [
    ("직장 내 괴롭힘", "2019-07-16", "근로기준법 제76조의2·제76조의3 신설 시행"),
    ("중대재해처벌법", "2022-01-27", "중대재해 처벌 등에 관한 법률 시행"),
    ("중대재해 처벌", "2022-01-27", "중대재해 처벌 등에 관한 법률 시행"),
    ("행정기본법", "2021-03-23", "행정기본법 시행(일부 조문 2023-03-24)"),
    ("교섭창구 단일화", "2011-07-01", "노조법 복수노조 교섭창구단일화 시행"),
    ("교섭창구단일화", "2011-07-01", "노조법 복수노조 교섭창구단일화 시행"),
    ("근로시간면제", "2010-07-01", "노조법 근로시간면제제도 시행"),
    ("출산전후휴가", "2012-08-02", "근로기준법 '산전후휴가'→'출산전후휴가' 명칭 변경 시행"),
    ("임시처분", "2010-07-26", "행정심판법 전부개정(임시처분 신설) 시행"),
    ("1주 52시간", "2018-07-01", "근로기준법 1주 최대 52시간(단계적) 시행"),
    ("주 52시간", "2018-07-01", "근로기준법 1주 최대 52시간(단계적) 시행"),
    ("해고자도 조합원", "2021-07-06", "노조법 개정(ILO 핵심협약) 시행"),
    ("사용자 범위 확대", "2026-03-10", "노조법 제2조·제3조 개정 시행"),
    ("일·가정 양립", "2008-06-22", "남녀고용평등과 일·가정 양립 지원에 관한 법률 명칭 시행"),
]

def sha_text(s): return hashlib.sha256(s.encode("utf-8")).hexdigest()
def sha_file(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def hoverlap(q, p, n):
    a = HANGUL.sub("", q); b = HANGUL.sub("", p)
    if len(a) < n: return 1.0 if a and a in b else 0.0
    grams = {a[i:i + n] for i in range(len(a) - n + 1)}
    return round(sum(g in b for g in grams) / len(grams), 4)

def load_v22():
    spec = importlib.util.spec_from_file_location("v22", HERE / "nomusa-v22-original-expert-packets.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

def exam_window(year):
    if year in EXAM_DATES: d = EXAM_DATES[year]; return d, d
    return f"{year}-07-01", f"{year}-09-30"

def official_index(manifest):
    idx = {}
    for y in manifest["years"]:
        for a in y["attachments"]:
            for m in a["members"]:
                idx[m["sha256"]] = {"year": y["year"], "postUrl": y["postUrl"], "attachment": a["fileName"],
                                    "attachmentSha256": a["sha256"], "member": m["member"], "memberSha256": m["sha256"]}
    return idx

def build(root: Path, out_dir: Path):
    t0 = time.monotonic(); started = datetime.now(timezone.utc).isoformat(timespec="seconds")
    v22 = load_v22()
    rows, v21 = v22.load(root)
    manifest = json.loads((root / "review/NOMUSA_V23_QNET_OFFICIAL_MANIFEST.json").read_text(encoding="utf-8"))
    oidx = official_index(manifest)
    ocr = json.loads((root / "review/NOMUSA_V23_OCR_TEXT_CACHE.json").read_text(encoding="utf-8"))
    cases = json.loads((root / "review/NOMUSA_V23_CASE_LOOKUP_CACHE.json").read_text(encoding="utf-8"))
    manual = json.loads((root / "review/NOMUSA_V23_MANUAL_REVIEW.json").read_text(encoding="utf-8"))
    msrc = manual.get("sourceReview", {}); mecon = manual.get("econRecalc", {}); macad = manual.get("academicPrecheck", {})
    v22audit = {}
    p22 = root / "review-artifacts/NOMUSA_V22_328_ORIGINAL_AUDIT.json"
    if p22.is_file():
        for r in json.loads(p22.read_text(encoding="utf-8")).get("rows", []): v22audit[r["id"]] = r

    text_cache = {}
    def pages_of(p):
        if p not in text_cache: text_cache[p] = source_text(root / p, ocr, allow_ocr=False)
        return text_cache[p]

    ledger = []; issues = []
    for id_, q in sorted(rows.items(), key=lambda z: (int(z[1]["year"]), z[0])):
        y = int(q["year"]); src = str(q["sourceText"]); det = str(q["detailed"]); comp = str(q["compressed"])
        body = det + "\n" + comp
        tsha = v21[id_]["textSHA256"]
        assert tsha == sha_text(src + "\0" + det + "\0" + comp)
        cands = v22.paths_for(q) if y > 2012 else [f"source_pdf/qnet_official_hwp/{y}_second_qnet_official.hwp"]
        best = None
        for p in cands:
            if not (root / p).is_file(): continue
            pg = pages_of(p); full = "\n".join(x["text"] for x in pg)
            methods = sorted({x["method"] for x in pg}); is_ocr = any(m.startswith("TESSERACT") for m in methods)
            score = hoverlap(src, full, 4 if is_ocr else 6)
            pts = POINTS.findall(src)
            ptext = "\n".join(x["text"] for x in source_text(root / p, ocr, allow_ocr=False, force_ocr=True)) if p in SCRAMBLED_TEXT_LAYER else full
            if p in SCRAMBLED_TEXT_LAYER: methods = methods + ["TESSERACT_KOR_OCR_FOR_POINTS"]
            flat = re.sub(r"\s+", "", ptext)
            found = [x for x in pts if re.search(rf"\({x}점\)", flat) or re.search(rf"(?<!\d){x}점\)", flat) or re.search(rf"\([^()\d]{{0,3}}{x}[^()\d]{{0,3}}점", flat)]
            c = {"file": p, "methods": methods, "overlap": score, "pointsTokens": pts, "pointsFound": found}
            if best is None or score > best["overlap"]: best = c
        repo_sha = sha_file(root / best["file"]) if best else ""
        off = oidx.get(repo_sha)
        is_summary = bool(re.search(r"요지|원문 전문은|기출 전문은|원본 PDF 참조|PDF를 참조|PDF 참조", src[:120]))
        band = ("HIGH" if best and best["overlap"] >= 0.85 else "MEDIUM" if best and best["overlap"] >= 0.5 else "LOW")
        mr = msrc.get(id_)
        # The historic manual 'topic/points' pass is valid only while the app stores a summary.
        # Once V24 replaces the actual sourceText, independently recompute the official
        # PDF text overlap; do not mask an OCR mismatch behind an old manual summary note.
        if mr and is_summary: band = mr["verdict"]
        pts_ok = bool(best) and set(best["pointsTokens"]) <= set(best["pointsFound"]) and bool(best["pointsTokens"])
        source = {
            "candidateFiles": cands, "repoFile": best["file"] if best else "", "repoSha256": repo_sha,
            "qnetOfficialByteIdentical": bool(off), "qnetPostUrl": off["postUrl"] if off else None,
            "qnetAttachment": off["attachment"] if off else None, "qnetMember": off["member"] if off else None,
            "qnetMemberSha256": off["memberSha256"] if off else None,
            "extraction": best["methods"] if best else [], "questionTextOverlap": best["overlap"] if best else None,
            "matchBand": band, "pointsTokens": best["pointsTokens"] if best else [],
            "pointsFoundInOfficial": best["pointsFound"] if best else [], "pointsCheck": "PASS" if pts_ok else "HOLD_POINTS_NOT_AUTO_CONFIRMED",
            "storedQuestionIsSummary": is_summary, "manualReview": mr,
            "v22Status": v22audit.get(id_, {}).get("autoSourceStatus"),
        }
        if mr and mr.get("pointsConfirmed"): source["pointsCheck"] = "PASS_MANUAL_OCR_READ"
        # ---- cases
        cites = []; seen = set()
        lo, hi = exam_window(y)
        for m in CASE.finditer(body):
            k = "".join(m.groups())
            pre = body[max(0, m.start() - 30): m.start()]; ctx = body[max(0, m.start() - 90): m.end() + 60]
            d = DATE_BEFORE.search(pre)
            stated = "%s-%02d-%02d" % (d.group(1), int(d.group(2)), int(d.group(3))) if d else None
            c = cases.get(k, {"status": "NOT_LOOKED_UP"}); hit = (c.get("hits") or [None])[0]
            post = None
            if hit: post = "AFTER_EXAM" if hit["decisionDate"] > hi else ("DATE_WINDOW_AMBIGUOUS" if hit["decisionDate"] >= lo else "BEFORE_EXAM")
            key = (k, stated)
            if key in seen: continue
            seen.add(key)
            cites.append({"caseNo": k, "statedDate": stated, "lawGoKr": c.get("status"),
                          "court": hit["court"] if hit else None, "officialDecisionDate": hit["decisionDate"] if hit else None,
                          "kind": hit["kind"] if hit else None, "caseName": hit["caseName"] if hit else None,
                          "searchUrl": c.get("publicSearchUrl"), "retrievedUTC": c.get("retrievedUTC"),
                          "statedDateMatches": (stated == hit["decisionDate"]) if (hit and stated) else None,
                          "timing": post, "annotatedAsPostExam": bool(POST_NOTE.search(ctx)) if post == "AFTER_EXAM" else None})
        law_flags = []
        for c in cites:
            if c["lawGoKr"] != "FOUND_ON_LAW_GO_KR": law_flags.append("CASE_NOT_FOUND_ON_LAW_GO_KR:" + c["caseNo"])
            if c["statedDateMatches"] is False: law_flags.append("CASE_DATE_MISMATCH:" + c["caseNo"])
            if c["timing"] == "AFTER_EXAM" and not c["annotatedAsPostExam"]: law_flags.append("CASE_AFTER_EXAM_UNLABELLED:" + c["caseNo"])
            if c["timing"] == "DATE_WINDOW_AMBIGUOUS": law_flags.append("CASE_DECIDED_NEAR_EXAM_DATE:" + c["caseNo"])
        stat = []
        for kw, eff, desc in STATUTE_EVENTS:
            i = body.find(kw)
            if i < 0: continue
            ctx = body[max(0, i - 120): i + 120]
            if eff > hi and not POST_NOTE.search(ctx):
                stat.append({"keyword": kw, "effectiveDateAI": eff, "event": desc, "flag": "MENTIONED_BEFORE_EFFECTIVE_DATE_UNLABELLED"})
            elif eff > hi:
                stat.append({"keyword": kw, "effectiveDateAI": eff, "event": desc, "flag": "MENTIONED_AS_LATER_CHANGE_LABELLED"})
        for s in stat:
            if s["flag"].endswith("UNLABELLED"): law_flags.append("STATUTE_TIME_EFFECT:" + s["keyword"])
        # ---- academic
        pairs = sorted({(m.group(1).strip(), m.group(2)) for m in AY.finditer(body)})
        acad = []
        for nm, yr in pairs:
            v = macad.get(f"{nm}|{yr}", "AI_PRECHECK_NOT_ASSESSED")
            acad.append({"name": nm, "year": yr, "aiPrecheck": v})
        acad_flags = [f"ACADEMIC_YEAR_SUSPECT:{a['name']}({a['year']})" for a in acad if a["aiPrecheck"].startswith("AI_PRECHECK_SUSPECT")]
        # ---- economics / arithmetic
        ar = arith_check(body); sy = check_symbolic(body)
        econ_manual = mecon.get(id_)
        calc_flags = [f"ARITH_MISMATCH:{x['expr']}" for x in ar if not x["ok"]] + [f"SYMBOLIC_MISMATCH:{x['expr']}" for x in sy if not x["ok"]]
        if econ_manual and econ_manual.get("result") == "MISMATCH": calc_flags.append("MANUAL_RECALC_MISMATCH")
        # ---- tags & verdicts
        tags = ["PASS_TECHNICAL"]
        src_ok = bool(off) and band in ("HIGH", "MEDIUM", "MANUAL_TOPIC_POINTS_MATCH") and source["pointsCheck"].startswith("PASS")
        if src_ok: tags.append("SOURCE_VERIFIED")
        else: tags.append("HOLD_MISSING_SOURCE" if not off else "HOLD_SOURCE_TEXT_MATCH")
        if is_summary: tags.append("CORRECTION_REQUIRED")
        domain = v21[id_].get("domain", "")
        if econ_manual and econ_manual.get("result") == "MATCH": tags.append("MODEL_RECALCULATED")
        elif (ar or sy) and not calc_flags: tags.append("MODEL_RECALCULATED")
        if calc_flags: tags.append("CORRECTION_REQUIRED")
        if law_flags:
            tags.append("HOLD_TIME_EFFECT" if any(f.startswith(("STATUTE_TIME", "CASE_AFTER", "CASE_DECIDED_NEAR")) for f in law_flags) else "ACADEMIC_OR_CASE_HOLD")
        tags.append("ACADEMIC_OR_CASE_HOLD")   # full judgments / statute history / original texts not read for every claim
        tags.append("EXPERT_SIGNOFF_PENDING")
        tags = list(dict.fromkeys(tags))
        row = {"id": id_, "year": y, "subject": q["subject"], "points": int(q["points"]),
               "reviewTierV21": v21[id_].get("reviewTier"), "domainV21": domain, "textSHA256": tsha,
               "isLengthProxyPriority77": v21[id_].get("reviewTier") == "P1_LENGTH_PROXY" or str(v21[id_].get("proxyDeficitChars", "0")) not in ("0", "", "None"),
               "source": source, "caseCitations": cites, "statuteTimeEffect": stat, "lawFlags": law_flags,
               "academicPairs": acad, "academicFlags": acad_flags,
               "arithmeticChains": ar, "symbolicChains": sy, "econManualRecalc": econ_manual, "calcFlags": calc_flags,
               "tags": tags,
               "verdicts": {"technical": "PASS_TECHNICAL",
                            "primarySourceQuestion": "VERIFIED_PRIMARY_SOURCE" if src_ok else "HOLD",
                            "legalAcademicContent": "HOLD_FLAGGED" if (law_flags or acad_flags or calc_flags) else "REVIEW_CANDIDATE",
                            "handwriting": "HOLD_HANDWRITING",
                            "expertApproval": "HOLD_EXPERT_APPROVAL", "finalApproval": "HOLD"},
               "reviewDate": REVIEW_DATE}
        ledger.append(row)
        for f in law_flags + acad_flags + calc_flags + (["STORED_QUESTION_IS_SUMMARY_NOT_OFFICIAL_TEXT"] if is_summary else []) + ([] if src_ok else ["SOURCE_NOT_VERIFIED:" + band + "/" + source["pointsCheck"]]):
            issues.append({"id": id_, "year": y, "subject": q["subject"], "tier": row["reviewTierV21"], "issue": f})
    # ---- summary
    cnt = Counter();
    for r in ledger: cnt.update(r["tags"])
    allc = [c for r in ledger for c in r["caseCitations"]]
    summary = {
        "schema": "NOMUSA_V23_VALIDATION_LEDGER/1", "reviewDate": REVIEW_DATE, "startedUTC": started,
        "total": len(ledger), "years": len({r['year'] for r in ledger}),
        "baseline2022": sum(r["year"] == 2022 for r in ledger), "remaining": sum(r["year"] != 2022 for r in ledger),
        "qnetOfficialByteIdentical": sum(r["source"]["qnetOfficialByteIdentical"] for r in ledger),
        "sourceVerifiedQuestion": cnt["SOURCE_VERIFIED"], "storedQuestionIsSummary": sum(r["source"]["storedQuestionIsSummary"] for r in ledger),
        "matchBands": dict(Counter(r["source"]["matchBand"] for r in ledger)),
        "caseCitationsDistinctOccurrences": len(allc), "distinctCaseNumbers": len({c['caseNo'] for c in allc}),
        "caseFoundOnLawGoKr": len({c['caseNo'] for c in allc if c['lawGoKr'] == 'FOUND_ON_LAW_GO_KR'}),
        "caseStatedDateChecked": sum(c["statedDateMatches"] is not None for c in allc),
        "caseStatedDateMismatch": sum(c["statedDateMatches"] is False for c in allc),
        "academicPairs": sum(len(r["academicPairs"]) for r in ledger),
        "arithmeticChainsChecked": sum(len(r["arithmeticChains"]) for r in ledger),
        "symbolicChainsChecked": sum(len(r["symbolicChains"]) for r in ledger),
        "econManualRecalc": len(mecon),
        "tagCounts": dict(cnt), "issueCounts": dict(Counter(i["issue"].split(":")[0] for i in issues)),
        "independentExpertApproved": 0, "finalApproval": "HOLD (0/328)",
        "qnetManifestRetrievedUTC": manifest["retrievedUTC"],
        "scriptSeconds": round(time.monotonic() - t0, 3),
        "finishedUTC": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "noDeploymentNoMutationOfOriginals": True,
    }
    return summary, ledger, issues

def write_outputs(root, summary, ledger, issues, out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    (root / "review/NOMUSA_V23_VALIDATION_LEDGER.json").write_text(
        json.dumps({"summary": summary, "rows": ledger}, ensure_ascii=False, indent=1), encoding="utf-8")
    (out_dir / "NOMUSA_V23_ISSUES.json").write_text(json.dumps(issues, ensure_ascii=False, indent=1), encoding="utf-8")
    with (out_dir / "NOMUSA_V23_LEDGER.csv").open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "year", "subject", "points", "tierV21", "textSHA256", "qnetByteIdentical", "qnetPostUrl", "repoFile",
                    "extraction", "overlap", "band", "pointsCheck", "isSummary", "cases", "casesFound", "lawFlags",
                    "academicPairs", "calcChains", "calcFlags", "tags", "finalApproval"])
        for r in ledger:
            s = r["source"]
            vals = [r["id"], r["year"], r["subject"], r["points"], r["reviewTierV21"], r["textSHA256"], s["qnetOfficialByteIdentical"],
                    s["qnetPostUrl"], s["repoFile"], "|".join(s["extraction"]), s["questionTextOverlap"], s["matchBand"], s["pointsCheck"],
                    s["storedQuestionIsSummary"], len(r["caseCitations"]), sum(c["lawGoKr"] == "FOUND_ON_LAW_GO_KR" for c in r["caseCitations"]),
                    ";".join(r["lawFlags"]), len(r["academicPairs"]), len(r["arithmeticChains"]) + len(r["symbolicChains"]),
                    ";".join(r["calcFlags"]), "|".join(r["tags"]), r["verdicts"]["finalApproval"]]
            w.writerow(["'" + v if isinstance(v, str) and v[:1] in "=+-@" else v for v in vals])
    # subject packets for expert reviewers
    pk = out_dir / "NOMUSA_V23_SUBJECT_PACKETS"; pk.mkdir(exist_ok=True)
    by = defaultdict(list)
    for r in ledger: by[re.sub(r"[ ⅠⅡ12교시/]", "", r["subject"]) or r["subject"]].append(r)
    for subj, rs in by.items():
        L = [f"# V23 독립 전문가 검토 패킷 — {subj} ({len(rs)}개)", "",
             "**AI 사전검증 결과이며 승인서가 아님. 최종승인 HOLD.** 검토자는 `textSHA256`이 같은 원고에만 서명.", "",
             "| ID | 연도 | 배점 | Q-Net 원본 동일 | 문항대조 | 배점 | 판례(확인/전체) | 플래그 | textSHA256 |", "|---|---|---|---|---|---|---|---|---|"]
        for r in sorted(rs, key=lambda z: (z["year"], z["id"])):
            s = r["source"]
            L.append("| `%s` | %d | %d | %s | %s %s | %s | %d/%d | %s | `%s` |" % (
                r["id"], r["year"], r["points"], "예" if s["qnetOfficialByteIdentical"] else "아니오", s["matchBand"],
                s["questionTextOverlap"], s["pointsCheck"], sum(c["lawGoKr"] == "FOUND_ON_LAW_GO_KR" for c in r["caseCitations"]),
                len(r["caseCitations"]), "; ".join(r["lawFlags"] + r["academicFlags"] + r["calcFlags"] + (["요지문항"] if s["storedQuestionIsSummary"] else [])) or "-",
                r["textSHA256"][:16]))
        L += ["", "## 검토자 기입란 (문항별 복제 사용)", "", "- 검토자 실명/자격:", "- 검토일:", "- 확인 원전(URL·조문·판결·문헌):",
              "- 결론(승인/수정요/보류):", "- 서명:", ""]
        (pk / f"V23_{subj}.md").write_text("\n".join(L), encoding="utf-8")

def self_test():
    assert hoverlap("가나다라마바사", "xx가나다라마바사yy", 4) == 1.0
    assert hoverlap("가나다라", "다른문장", 6) == 0.0
    assert arith_check("면적 0.5×0.2/2=0.05 이다")[0]["ok"]
    assert not arith_check("합계 3+4=8 이다")[0]["ok"]
    assert check_symbolic("C=0.8(24−L)=19.2−0.8L 이다")[0]["ok"]
    assert CASE.search("대법원 2020. 2. 20. 선고 2019두52386 판결").group(0) == "2019두52386"
    print("PASS_V23_LEDGER_SELF_TEST")

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("root", nargs="?", default=".")
    ap.add_argument("--self-test", action="store_true"); ap.add_argument("--out", default="review-artifacts")
    a = ap.parse_args()
    if a.self_test: self_test(); sys.exit(0)
    root = Path(a.root).resolve()
    s, l, i = build(root, root / a.out)
    write_outputs(root, s, l, i, root / a.out)
    print(json.dumps(s, ensure_ascii=False))

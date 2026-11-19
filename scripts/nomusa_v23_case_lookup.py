"""Look up Korean case numbers on 국가법령정보센터 (law.go.kr) precedent search and cache results.
Records court, decision date, case name exactly as listed. Not-found != fabricated (law.go.kr is not exhaustive)."""
from __future__ import annotations
import json, re, time, urllib.parse, urllib.request
from datetime import datetime, timezone
from pathlib import Path

PREC = "https://www.law.go.kr/LSW/precScListR.do?menuId=7&subMenuId=47&tabMenuId=213"
DETC = "https://www.law.go.kr/LSW/detcScListR.do?menuId=11&subMenuId=59&tabMenuId=289"
ROW = re.compile(r"([^\[\]<>]{0,80})\[\s*([가-힣]+(?:법원|재판소)[^\]]*?)\s+((?:19|20)\d{2})\.\s*(\d{1,2})\.\s*(\d{1,2})\.\s*(?:자\s*|선고\s*)?([0-9가-힣]+)\s*([가-힣 ]*?)\s*\]")

def _post(url, q, section="evtNo"):
    data = urllib.parse.urlencode({"q": q, "outmax": "20", "pg": "1", "section": section}).encode()
    req = urllib.request.Request(url, data=data, headers={"User-Agent": "Mozilla/5.0 (source-verification)"})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                return r.read().decode("utf-8", "replace")
        except Exception:
            if attempt == 4: raise
            time.sleep(2 * (attempt + 1))

def lookup(case_no: str) -> dict:
    url = DETC if "헌" in case_no else PREC
    hits = []
    for section in ("evtNo", "evtNm", "bdyText"):
        h = _post(url, case_no, section)
        hits = _parse(h, case_no)
        if hits: break
    return _result(case_no, url, hits, section)

def _parse(h, case_no):
    text = re.sub(r"\s+", " ", re.sub("<[^>]+>", " ", re.sub(r"<script.*?</script>", "", h, flags=re.S)))
    hits = []
    for m in ROW.finditer(text):
        if m.group(6).replace(" ", "") == case_no:
            hits.append({"caseName": m.group(1).replace("새창으로 열기", "").strip()[-60:], "court": m.group(2).strip(),
                         "decisionDate": "%s-%02d-%02d" % (m.group(3), int(m.group(4)), int(m.group(5))),
                         "kind": m.group(7)})
    return hits

def _result(case_no, url, hits, section):
    return {"caseNo": case_no, "searchEndpoint": url, "query": case_no, "searchSection": section,
            "publicSearchUrl": "https://www.law.go.kr/LSW/precSc.do?menuId=7&query=" + urllib.parse.quote(case_no) if "헌" not in case_no
                else "https://www.law.go.kr/LSW/detcSc.do?menuId=11&query=" + urllib.parse.quote(case_no),
            "status": "FOUND_ON_LAW_GO_KR" if hits else "NOT_FOUND_ON_LAW_GO_KR_SEARCH",
            "hits": hits, "retrievedUTC": datetime.now(timezone.utc).isoformat(timespec="seconds")}

def lookup_all(case_nos, cache_path: Path, offline=False):
    cache = json.loads(cache_path.read_text(encoding="utf-8")) if cache_path.is_file() else {}
    for c in sorted(set(case_nos)):
        if c in cache or offline: continue
        try: cache[c] = lookup(c)
        except Exception as e: cache[c] = {"caseNo": c, "status": "LOOKUP_ERROR", "error": str(e)[:200]}
        time.sleep(1.0)
    cache_path.write_text(json.dumps(dict(sorted(cache.items())), ensure_ascii=False, indent=1), encoding="utf-8")
    return cache

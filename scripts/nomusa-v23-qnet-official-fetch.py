#!/usr/bin/env python3
"""V23: download the OFFICIAL Q-Net 공인노무사 2차 attachments (2007~2026) and
record URL / attachment name / SHA-256 of the archive and every member.

Only network facts are recorded. Nothing is approved here.
Usage: python scripts/nomusa-v23-qnet-official-fetch.py OUT_DIR [--manifest review/NOMUSA_V23_QNET_OFFICIAL_MANIFEST.json]
"""
from __future__ import annotations
import argparse, hashlib, io, json, re, sys, time, urllib.parse, urllib.request, zipfile
from datetime import datetime, timezone
from pathlib import Path

BASE = "https://www.q-net.or.kr/cst003.do"
# artlSeq of 2차 posts on Q-Net board Q004 (found via board list cst00301s01, 2026-11-17)
POSTS = {2026:5275124,2025:5243325,2024:5213665,2023:5212324,2022:5210985,2021:5209035,
         2020:5207537,2019:5206011,2018:5203698,2017:5201961,2016:5191801,2015:5143603,
         2014:5104410,2013:5075003,2012:5058215,2011:5047980,2010:5028975,2009:5021181,
         2008:5021180,2007:5021179}
UA = {"User-Agent": "Mozilla/5.0 (compatible; source-verification)"}

def get(url, referer=None):
    h = dict(UA)
    if referer: h["Referer"] = referer
    with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=120) as r:
        return r.read(), r.headers

def post_url(seq):
    return f"{BASE}?artlSeq={seq}&boardId=Q004&gId=05&gSite=L&id=cst00302"

def members(name, data):
    out = []
    if name.lower().endswith(".zip"):
        z = zipfile.ZipFile(io.BytesIO(data))
        for i in z.infolist():
            n = i.filename
            if not i.flag_bits & 0x800:
                try: n = i.filename.encode("cp437").decode("cp949", "replace")
                except UnicodeEncodeError: pass
            if i.is_dir(): continue
            d = z.read(i)
            out.append({"member": n, "bytes": len(d), "sha256": hashlib.sha256(d).hexdigest(), "_data": d})
    else:
        out.append({"member": name, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(), "_data": data})
    return out

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("out"); ap.add_argument("--manifest")
    ap.add_argument("--years", default="")
    a = ap.parse_args(); out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    years = [int(y) for y in a.years.split(",") if y] or sorted(POSTS)
    t = time.monotonic(); rows = []
    for y in years:
        seq = POSTS[y]; purl = post_url(seq)
        html, _ = get(purl); h = html.decode("utf-8", "replace")
        title = re.sub(r"\s+", " ", re.sub("<[^>]+>", " ", h[h.find("공인노무사")-80:h.find("공인노무사")+60])).strip()
        row = {"year": y, "artlSeq": seq, "postUrl": purl, "postTitleExcerpt": title, "attachments": []}
        for fp, fn, fs in re.findall(r"fileDown\('([^']+)',\s*'([^']+)',\s*'(\d+)'\)", h):
            q = urllib.parse.urlencode({"id":"cst00302s01","gSite":"L","gId":"05","fileCode":"R001",
                 "filePath":fp,"fileName":fn,"fileSeq":fs,"artlSeq":seq,"href":"0"})
            durl = f"{BASE}?{q}"
            data, hd = get(durl, purl)
            ms = members(fn, data); d = out / str(y); d.mkdir(exist_ok=True)
            (d / fn.replace("/", "_")).write_bytes(data)
            for m in ms:
                tgt = d / "members" / m["member"].replace("/", "__"); tgt.parent.mkdir(exist_ok=True)
                tgt.write_bytes(m.pop("_data"))
            row["attachments"].append({"fileName": fn, "fileSeq": fs, "downloadUrl": durl,
                "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(), "members": ms})
        rows.append(row); print(y, len(row["attachments"]), [m["member"] for x in row["attachments"] for m in x["members"]], flush=True)
    man = {"schema": "NOMUSA_V23_QNET_OFFICIAL_MANIFEST/1",
           "retrievedUTC": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "board": "Q-Net 고객지원 > 자료실 > 공개문제 (boardId=Q004, gId=05 공인노무사)",
           "seconds": round(time.monotonic() - t, 2), "years": rows,
           "note": "Official attachment bytes and SHA-256 only. Not a content approval."}
    if a.manifest:
        Path(a.manifest).write_text(json.dumps(man, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"years": len(rows), "seconds": man["seconds"]}))

if __name__ == "__main__":
    main()

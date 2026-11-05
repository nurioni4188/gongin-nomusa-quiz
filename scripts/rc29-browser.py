#!/usr/bin/env python3
"""Offline Chromium test: PC/tablet/Android-emulated screens. No Vercel, no network."""
import json
from pathlib import Path
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parent.parent
DIR=ROOT/"rc29-evidence"
DIR.mkdir(exist_ok=True)
r={"schema":"rc29-browser-test-v1","status":"HOLD","mode":"OFFLINE_CHROMIUM_VIEWPORT_EMULATION",
   "viewports":[],"errors":[]}
profiles=[("pc-1365",1365,900,False),("tablet-768",768,1024,False),
          ("mobile-390",390,844,True),("mobile-360",360,780,True)]
try:
 from playwright.sync_api import sync_playwright
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True)
  for name,width,height,mobile in profiles:
   item={"name":name,"size":[width,height],"status":"HOLD"}
   ctx=None
   try:
    ctx=browser.new_context(viewport={"width":width,"height":height},
                            is_mobile=mobile,has_touch=mobile,device_scale_factor=1)
    page=ctx.new_page()
    page.goto((ROOT/"index.html").as_uri(),wait_until="load",timeout=30000)
    page.locator("#yearFilter").select_option("2022")
    page.locator("#subjectFilter").select_option("all")
    page.locator("#verificationFilter").select_option("all")
    page.get_by_role("button",name="시작 / 다시풀기").click()
    assert page.locator(".option").count()==5
    assert "HOLD" in page.locator("#validationMessage").inner_text()
    page.locator(".option").first.click()
    page.locator("#showAnswerBtn").click()
    assert "채점하지" in page.locator("#validationMessage").inner_text()
    assert page.locator(".wrong").count()==0 and page.locator(".correct").count()==0
    assert "0 / 0" in page.locator("#score").inner_text()
    page.locator("#nextBtn").click()
    assert "진행: 2 /" in page.locator("#score").inner_text()
    assert not page.evaluate("document.documentElement.scrollWidth > window.innerWidth + 2")
    # Only a synthetic fixture is used here; its answers are NEVER added to the real bank.
    fixture={"verificationStatus":"VERIFIED_OFFICIAL_FINAL","options":["A","B","C","D","E"],
      "answer":2,"provenance":{"questionFile":"synthetic-question.pdf","questionPage":1,
      "answerFile":"synthetic-final.pdf","officialAnswerURL":"https://www.q-net.or.kr/test",
      "booklet":"A","checkedBy":"test-only","checkedAt":"test-only"}}
    assert page.evaluate("(q)=>approvedAnswers(q)",fixture)==[2]
    fixture["acceptedAnswers"]=[0,4]
    assert page.evaluate("(q)=>approvedAnswers(q)",fixture)==[0,4]
    fixture["verificationStatus"]="PENDING"
    assert page.evaluate("(q)=>approvedAnswers(q)",fixture) is None
    fixture["verificationStatus"]="VERIFIED_OFFICIAL_FINAL"
    del fixture["acceptedAnswers"]
    fixture["answer"]="③"
    assert page.evaluate("(q)=>approvedAnswers(q)",fixture) is None
    page.locator("#verificationFilter").select_option("verified")
    page.get_by_role("button",name="시작 / 다시풀기").click()
    assert "검증된 문제 없음" in page.locator("#score").inner_text()
    page.locator("#verificationFilter").select_option("unverified")
    page.get_by_role("button",name="시작 / 다시풀기").click()
    assert page.locator(".option").count()==5
    page.screenshot(path=str(DIR/(name+".png")),full_page=True)
    item["status"]="PASS"
   except Exception as e:
    item["error"]=str(e)[:1000]
    r["errors"].append(name+": "+str(e)[:450])
   finally:
    if ctx:ctx.close()
   r["viewports"].append(item)
  browser.close()
 r["status"]="PASS" if all(x["status"]=="PASS" for x in r["viewports"]) else "HOLD"
except Exception as e:
 r["errors"].append("Chromium setup/runtime error: "+str(e)[:1000])
r["completedAtUTC"]=datetime.now(timezone.utc).isoformat()
(DIR/"browser-test.json").write_text(json.dumps(r,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
print(json.dumps({"status":r["status"],"viewports":r["viewports"],"errors":r["errors"]},ensure_ascii=False))
raise SystemExit(0 if r["status"]=="PASS" else 2)

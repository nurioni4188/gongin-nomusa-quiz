#!/usr/bin/env python3
"""Offline Chromium viewport smoke tests: NO Vercel or external calls."""
import json
import sys
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent
EVIDENCE = ROOT / "rc28-evidence"
EVIDENCE.mkdir(exist_ok=True)
RESULT = {"schema": "rc28-browser-v1", "status": "HOLD", "mode": "local-file-only",
          "viewports": [], "errors": []}
PROFILES = [
    ("desktop", 1365, 900, False),
    ("tablet", 768, 1024, False),
    ("android-390", 390, 844, True),
    ("android-360", 360, 780, True),
]
try:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        for name, width, height, mobile in PROFILES:
            record = {"name": name, "width": width, "height": height, "mobileEmulation": mobile, "status": "HOLD"}
            context = None
            try:
                context = browser.new_context(viewport={"width": width,"height": height},
                                              is_mobile=mobile, has_touch=mobile, device_scale_factor=1)
                page = context.new_page()
                page.goto((ROOT / "index.html").as_uri(), wait_until="load", timeout=30000)
                assert "공인노무사" in page.locator("h1").inner_text()
                page.locator("#yearFilter").select_option("2022")
                page.locator("#subjectFilter").select_option("all")
                page.get_by_role("button", name="시작 / 다시풀기").click()
                assert page.locator(".option").count() == 5, "five options missing"
                assert page.locator(".meta").count() == 1, "question meta missing"
                page.locator(".option").first.click()
                assert "selected" in page.locator(".option").first.get_attribute("class")
                page.locator("#showAnswerBtn").click()
                assert not page.locator("#nextBtn").is_hidden(), "next button missing"
                page.locator("#nextBtn").click()
                assert "진행: 2 /" in page.locator("#score").inner_text()
                overflow = page.evaluate("document.documentElement.scrollWidth > window.innerWidth + 2")
                assert not overflow, "horizontal overflow"
                page.screenshot(path=str(EVIDENCE / (name + ".png")), full_page=True)
                record["status"] = "PASS"
            except Exception as exc:
                record["error"] = str(exc)[:1200]
                RESULT["errors"].append(name + ": " + str(exc)[:500])
            finally:
                if context:
                    context.close()
            RESULT["viewports"].append(record)
        browser.close()
    RESULT["status"] = "PASS" if all(v["status"] == "PASS" for v in RESULT["viewports"]) else "HOLD"
except Exception as exc:
    RESULT["errors"].append("Browser execution failure: " + str(exc)[:1200])
RESULT["completedAtUtc"] = datetime.now(timezone.utc).isoformat()
(EVIDENCE / "browser-smoke.json").write_text(json.dumps(RESULT, ensure_ascii=False, indent=2) + "\n", encoding="utf8")
print(json.dumps({"status": RESULT["status"], "viewports": RESULT["viewports"], "errors": RESULT["errors"]}, ensure_ascii=False))
sys.exit(0 if RESULT["status"] == "PASS" else 2)

#!/usr/bin/env python3
"""V7.1 review-only browser regression: Q-Net PDF page annotations, never scoring approval."""
import json
import sys
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
CASES = [
    (2020, "A", "민법", 72, 24),
    (2020, "A", "민법", 75, 25),
    (2020, "A", "사회보험법", 78, 26),
    (2020, "A", "경제학원론", 114, 36),
    (2020, "B", "노동법Ⅰ", 4, 3),
    (2020, "B", "노동법Ⅰ", 5, 3),
    (2020, "B", "노동법Ⅰ", 6, 3),
    (2020, "B", "노동법Ⅰ", 10, 4),
    (2020, "B", "노동법Ⅱ", 36, 12),
    (2020, "B", "민법", 75, 25),
    (2020, "B", "사회보험법", 78, 26),
    (2020, "B", "경영학개론", 112, 34),
    (2020, "B", "경영학개론", 117, 35),
    (2021, "A", "경영학개론", 102, 34),
]

class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

def main():
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(Quiet, directory=str(ROOT)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    out = []
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True, args=["--no-sandbox"])
            for width in (1440, 390, 360):
                errors = []
                context = browser.new_context(viewport={"width": width, "height": 860})
                page = context.new_page()
                page.on("pageerror", lambda error: errors.append(str(error)))
                for year, form, subject, number, pdf_page in CASES:
                    key = f"{year}-{form}-{subject}-{number}"
                    try:
                        page.goto(
                            f"http://127.0.0.1:{server.server_port}/study-hub/first-legacy-answers.html",
                            wait_until="domcontentloaded",
                        )
                        page.locator("#year").select_option(str(year))
                        page.locator("#type").select_option(form)
                        page.locator("#subject").select_option(subject)
                        page.locator("#number").fill(str(number))
                        row = page.locator("#rows tr")
                        assert row.count() == 1, f"{key}: row count {row.count()}"
                        body = row.inner_text()
                        assert f"PDF {pdf_page}쪽" in body, f"{key}: wrong page"
                        assert "인쇄 쪽수·전체 지문 검증 HOLD" in body, f"{key}: missing HOLD"
                        assert "최종정답 PDF" in body, f"{key}: missing official link"
                        overflow = page.evaluate(
                            "document.documentElement.scrollWidth-document.documentElement.clientWidth"
                        )
                        assert overflow <= 1, f"{key}: horizontal overflow {overflow}"
                        out.append({"viewport": width, "case": key, "status": "PASS"})
                    except Exception as exc:
                        out.append({
                            "viewport": width, "case": key, "status": "HOLD",
                            "reason": str(exc)[:350],
                        })
                if errors:
                    out.append({"viewport": width, "status": "HOLD", "pageErrors": errors})
                context.close()
            browser.close()
    finally:
        server.shutdown()
    passed = sum(r["status"] == "PASS" for r in out)
    status = "PASS" if len(out) == 42 and passed == 42 else "HOLD"
    print(json.dumps({
        "schema": "nomusa-first-v71-visual-page-browser-qa/1",
        "status": status,
        "expected": 42,
        "passed": passed,
        "issues": [r for r in out if r["status"] != "PASS"],
        "scoringApproval": "HOLD",
        "newPreview": "NOT_DEPLOYED",
    }, ensure_ascii=False, indent=2))
    return 0 if status == "PASS" else 1

if __name__ == "__main__":
    sys.exit(main())

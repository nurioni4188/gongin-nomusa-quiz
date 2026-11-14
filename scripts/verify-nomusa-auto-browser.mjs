import assert from "node:assert/strict";
import { createServer } from "node:http";
import { spawn } from "node:child_process";
import { once } from "node:events";
import { access, mkdtemp, readFile, rm } from "node:fs/promises";
import os from "node:os";
import path from "node:path";

const executable = process.env.CHROME_PATH ?? (process.platform === "win32"
  ? "C:/Program Files/Google/Chrome/Application/chrome.exe" : "/usr/bin/chromium");
await access(executable);
const types = { ".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8", ".css": "text/css", ".pdf": "application/pdf" };
const root = process.cwd();
const server = createServer(async (request, response) => {
  try {
    const pathname = new URL(request.url, "http://localhost").pathname;
    const file = path.resolve(root, "." + pathname);
    assert.ok(file.startsWith(root + path.sep));
    const payload = await readFile(file);
    response.writeHead(200, { "Content-Type": types[path.extname(file)] ?? "application/octet-stream" });
    response.end(payload);
  } catch {
    response.writeHead(404).end();
  }
});
server.listen(0, "127.0.0.1");
await once(server, "listening");
const profile = await mkdtemp(path.join(os.tmpdir(), "nomusa-auto-"));
const chrome = spawn(executable, ["--headless=new", "--disable-gpu", "--no-first-run", "--no-default-browser-check", "--remote-debugging-port=0", "--user-data-dir=" + profile, "about:blank"], { windowsHide: true, stdio: "ignore" });

const pause = ms => new Promise(resolve => setTimeout(resolve, ms));
async function poll(action) {
  for (let attempt = 0; attempt < 100; attempt++) {
    try { const value = await action(); if (value) return value; } catch {}
    await pause(100);
  }
  throw new Error("Timed out waiting for Chrome or page");
}

let socket;
try {
  const port = await poll(async () => (await readFile(path.join(profile, "DevToolsActivePort"), "utf8")).split("\n")[0]);
  const targets = await (await fetch("http://127.0.0.1:" + port + "/json/list")).json();
  socket = new WebSocket(targets.find(target => target.type === "page").webSocketDebuggerUrl);
  await once(socket, "open");
  let id = 0;
  const pending = new Map();
  const errors = [];
  socket.addEventListener("message", ({ data }) => {
    const result = JSON.parse(data);
    if (result.id) {
      const callback = pending.get(result.id);
      pending.delete(result.id);
      callback?.(result);
    }
    if (result.method === "Runtime.exceptionThrown") errors.push(result.params.exceptionDetails.text);
  });
  function send(method, params = {}) {
    const requestId = ++id;
    return new Promise((resolve, reject) => {
      const timeout = setTimeout(() => { pending.delete(requestId); reject(new Error(method + " timed out")); }, 12000);
      pending.set(requestId, message => {
        clearTimeout(timeout);
        if (message.error) reject(new Error(message.error.message));
        else resolve(message.result);
      });
      socket.send(JSON.stringify({ id: requestId, method, params }));
    });
  }
  async function evaluate(expression) {
    const result = await send("Runtime.evaluate", { expression, returnByValue: true });
    if (result.exceptionDetails) throw new Error(result.exceptionDetails.exception?.description ?? result.exceptionDetails.text);
    return result.result.value;
  }
  await send("Runtime.enable");
  const key = "nomusa_rc27_v103_essay_records_v1";
  const url = "http://127.0.0.1:" + server.address().port + "/second/index.html";
  const ready = () => poll(() => evaluate("document.readyState === 'complete' && !!document.querySelector('#n27-year')"));
  for (const width of [1440, 390, 360]) {
    await send("Emulation.setDeviceMetricsOverride", { width, height: 900, deviceScaleFactor: 1, mobile: width < 500 });
    await send("Page.navigate", { url });
    await ready();
    const result = await evaluate(`(() => {
      const find = s => document.querySelector(s);
      const click = s => find(s).click();
      const select = y => {
        const filter = find('#n27-year');
        filter.value = y;
        filter.dispatchEvent(new Event('change'));
      };
      const layout = () => document.documentElement.scrollWidth <= innerWidth;
      if (find('#n27-year').options.length !== 21) throw Error('Year filter');
      click('[data-answer="2022-org-1"]');
      click('[data-pane="detail"]');
      if (!find('[data-pane="detail"][aria-pressed="true"]')) throw Error('Detailed answer');
      click('[data-pane="compact"]');
      if (!find('[aria-label="학습용 압축답안"]')) throw Error('Compact answer');
      click('[data-pane="write"]');
      const existing = find('#n27-draft');
      existing.value = '기존 ' + ${width};
      existing.dispatchEvent(new Event('input'));
      select('2013');
      click('[data-answer="2013_p1"]');
      if (!find('a[href*="2013_second_full_original.pdf#page=1"]')) throw Error('2013 PDF link');
      select('2007');
      click('[data-answer="nomusa-auto-2007-labor1-q1"]');
      click('[data-pane="detail"]');
      if (!find('.n1079-empty')?.textContent.includes('HOLD')) throw Error('Answer HOLD');
      click('#n1079-advanced summary');
      click('[aria-label="문항별 원본 위치"] summary');
      if (!find('[aria-label="문항별 원본 위치"]').textContent.includes('HWP 페이지 HOLD') || !layout()) throw Error('Source panel layout');
      click('[data-pane="write"]');
      const input = find('#n27-draft');
      input.value = '과거 ' + ${width};
      input.dispatchEvent(new Event('input'));
      if (!find('#n27-save-state').textContent.includes('임시저장 완료')) throw Error('Autosave');
      click('[data-pane="compare"]');
      if (find('#n27-flag').textContent.includes('취소')) click('#n27-flag');
      click('#n27-flag');
      if (!find('#n27-flag').textContent.includes('취소') || !find('.n27-metrics').textContent.includes('%')) throw Error('Review progress');
      const state = JSON.parse(localStorage.getItem('${key}'));
      return layout() && state.drafts['nomusa-auto-2007-labor1-q1'] === '과거 ' + ${width}
        && state.drafts['2022-org-1'] === '기존 ' + ${width};
    })()`);
    assert.equal(result, true, "Local storage or viewport");
    await send("Page.reload", { ignoreCache: true });
    await ready();
    assert.equal(await evaluate(`(() => {
      document.querySelector('[data-answer="nomusa-auto-2007-labor1-q1"]').click();
      document.querySelector('[data-pane="write"]').click();
      return document.querySelector('#n27-draft').value === '과거 ' + ${width}
        && document.querySelector('#n27-flag').textContent.includes('취소')
        && document.documentElement.scrollWidth <= innerWidth;
    })()`), true, "Reload restores draft and review");
    assert.deepEqual(errors, []);
    console.log(JSON.stringify({ status: "PASS", width, checks: ["years", "detail", "compact", "HOLD", "source index", "autosave", "restore", "review", "layout"] }));
  }
} finally {
  socket?.close();
  chrome.kill();
  server.close();
  await rm(profile, { recursive: true, force: true, maxRetries: 5, retryDelay: 200 }).catch(() => {});
}

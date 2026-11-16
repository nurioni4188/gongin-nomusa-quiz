(() => {
  'use strict';

  const config = window.HUB_QA;
  const frame = document.getElementById('frame');
  const run = document.getElementById('run-qa');
  const status = document.getElementById('qa-status');
  const results = document.getElementById('qa-results');
  const manual = globalThis.crypto?.randomUUID?.() || Date.now().toString(36);
  const essayKey = 'nomusa_rc27_v103_essay_records_v1';
  const mainId = '2025-org-1';
  const widths = config.widths;
  const cases = config.checks;
  const timeout = 6000;
  const tick = delay => new Promise(resolve => setTimeout(resolve, delay));

  async function waitFor(condition, message) {
    const end = Date.now() + timeout;
    while (Date.now() < end) {
      const result = condition();
      if (result) return result;
      await tick(40);
    }
    throw Error(message);
  }

  function assert(condition, message) {
    if (!condition) throw Error(message);
  }

  function find(selector) {
    const found = frame.contentDocument?.querySelector(selector);
    if (!found) throw Error('화면 요소 확인 실패 · ' + selector);
    return found;
  }

  function click(selector) {
    const button = find(selector);
    assert(!button.disabled, '사용 가능한 버튼이 필요합니다 · ' + selector);
    button.click();
  }

  function input(selector, value, type = 'input') {
    const field = find(selector);
    field.value = value;
    field.dispatchEvent(new frame.contentWindow.Event(type, {bubbles: true}));
  }

  function text(selector) {
    return find(selector).textContent;
  }

  function open(width, namespace, route = 'home') {
    frame.style.width = width + 'px';
    const url = new URL('index.html', location.href);
    url.searchParams.set('qa', namespace);
    url.hash = route;
    if (frame.src === url.href) return Promise.resolve();
    return load(() => { frame.src = url.href; });
  }

  function load(navigate) {
    return new Promise((resolve, reject) => {
      const onLoad = () => {
        clearTimeout(timer);
        if (frame.contentWindow?.HubState?.qa) resolve();
        else reject(Error('검증용 화면을 열 수 없습니다.'));
      };
      const timer = setTimeout(() => {
        frame.removeEventListener('load', onLoad);
        reject(Error('검증용 화면 응답 시간 초과'));
      }, timeout);
      frame.addEventListener('load', onLoad, {once: true});
      navigate();
    });
  }

  function reload() {
    return load(() => frame.contentWindow.location.reload());
  }

  function recordKey(namespace, key) {
    return `nomusa_qa_${namespace}:${key}`;
  }

  function clean(namespace) {
    for (const key of [essayKey, 'nomu1-progress-v2', 'nomusa_preview_hub_v1']) {
      localStorage.removeItem(recordKey(namespace, key));
    }
  }

  function checkWidth(width) {
    const document = frame.contentDocument;
    assert(frame.contentWindow.innerWidth === width, '뷰포트 폭 불일치');
    assert(document.documentElement.scrollWidth <= width, '가로 넘침 ' + (document.documentElement.scrollWidth - width) + 'px');
  }

  async function exportJson() {
    const document = frame.contentDocument;
    let payload;
    const onDownload = event => {
      const anchor = event.target.closest('a[download]');
      if (!anchor) return;
      event.preventDefault();
      payload = frame.contentWindow.fetch(anchor.href).then(response => response.text());
    };
    document.addEventListener('click', onDownload, true);
    try {
      click('[data-action="export"]');
      assert(payload, 'JSON 다운로드가 시작되지 않았습니다.');
      return await payload;
    } finally {
      document.removeEventListener('click', onDownload, true);
    }
  }

  function importJson(payload) {
    const view = frame.contentWindow;
    const transfer = new view.DataTransfer();
    transfer.items.add(new view.File([payload], 'study-qa.json', {type: 'application/json'}));
    const file = find('#import-file');
    file.files = transfer.files;
    file.dispatchEvent(new view.Event('change', {bubbles: true}));
  }

  function display(checks) {
    const table = document.createElement('table');
    table.className = 'verify-matrix';
    const heading = table.createTHead().insertRow();
    for (const label of ['검증 항목', ...widths.map(width => width + 'px')]) {
      const th = document.createElement('th');
      th.scope = 'col';
      th.textContent = label;
      heading.append(th);
    }
    const body = table.createTBody();
    for (const [id, label] of cases) {
      const row = body.insertRow();
      const th = document.createElement('th');
      th.scope = 'row';
      th.textContent = label;
      row.append(th);
      for (const width of widths) {
        const result = checks.find(check => check.width === width && check.id === id);
        const td = row.insertCell();
        const badge = document.createElement('span');
        badge.className = 'status ' + (result?.status === 'PASS' ? 'pass' : 'hold');
        badge.textContent = result?.status || '대기';
        td.append(badge);
        if (result?.reason) {
          const reason = document.createElement('small');
          reason.textContent = result.reason;
          td.append(reason);
        }
      }
    }
    results.replaceChildren(table);
  }

  async function runWidth(width, allChecks, token) {
    const namespace = 'run-' + width + '-' + token;
    const restoreNamespace = namespace + '-restore';
    const answer = '검증용 답안 ' + width + 'px · 문제의 소재와 결론';
    const baseline = new Map([essayKey, 'nomu1-progress-v2', 'nomusa_preview_hub_v1']
      .map(key => [key, localStorage.getItem(key)]));
    const casesById = {
      detail: async () => {
        await open(width, namespace);
        checkWidth(width);
        click('[data-action="start-essay"]');
        assert(find('[data-selected-id]').dataset.selectedId === mainId, '기존 문항 ID 불일치');
        assert(text('#trace-content').includes('학습용 초안') && text('#trace-content').includes('상세 학습답안'), '상세답안·초안 상태 누락');
        click('[data-action="compressed"]');
        assert(text('#trace-content').includes('시험장 압축답안'), '시험장 압축답안 누락');
        click('[data-action="write"]');
        find('#draft');
        checkWidth(width);
      },
      source: async () => {
        click('[data-trace="0"]');
        assert(text('.source-text').includes('퀸'), '기출 원문 미표시');
        click('[data-trace="1"]');
        const pdf = find('#trace-content a').href;
        assert(new URL(pdf).hash === '#page=1', '원본 쪽수 링크 오류');
        const response = await frame.contentWindow.fetch(pdf, {headers: {Range: 'bytes=0-7'}, signal: AbortSignal.timeout(timeout)});
        assert(response.ok && (await response.text()).startsWith('%PDF-'), '원본 PDF 응답 오류');
        click('[data-trace="2"]');
        assert(text('#trace-content').includes('선택지·수식'), '수식 대조 누락');
        click('[data-trace="3"]');
        assert(text('#trace-content').includes('공식 모범답안 미확보'), '공식 근거 HOLD 표시 누락');
        click('[data-trace="5"]');
        input('#memo', 'PDF 1쪽 대조');
        assert(text('#memo-save').includes('자동저장 완료'), '검토 메모 저장 실패');
      },
      save: async () => {
        click('[data-pane="write"]');
        input('#draft', answer);
        assert(text('#save-state') === '임시저장 완료', '임시저장 표시 실패');
        assert(JSON.parse(localStorage.getItem(recordKey(namespace, essayKey))).drafts[mainId] === answer, '저장 데이터 불일치');
        await reload();
        assert(find('#draft').value === answer, '새로고침 후 답안 불일치');
        assert(find('[data-selected-id]').dataset.selectedId === mainId, '새로고침 후 문항 불일치');
        checkWidth(width);
      },
      exam: async () => {
        click('[data-action="exam"]');
        click('[data-action="exam-start"]');
        assert(find('[data-trace="3"]').disabled && find('[data-trace="4"]').disabled && find('[data-trace="5"]').disabled, '실전 중 정답·해설·메모 잠금 실패');
        input('#draft', answer + ' · 실전');
        await reload();
        find('#exam-clock');
        assert(find('#draft').value === answer + ' · 실전' && find('[data-trace="3"]').disabled, '실전 답안·잠금 복원 실패');
        click('[data-action="exam-stop"]');
        click('[data-action="exam-end"]');
        assert(!find('[data-trace="3"]').disabled && text('#trace-content').includes(answer), '실전 종료 후 비교 화면 오류');
        checkWidth(width);
      },
      backup: async () => {
        click('[data-nav="backup"]');
        checkWidth(width);
        const payload = await exportJson();
        const snapshot = JSON.parse(payload);
        assert(snapshot.essay.drafts[mainId] === answer + ' · 실전', '내보내기 답안 불일치');
        assert(snapshot.hub.notes[mainId] === 'PDF 1쪽 대조', '내보내기 메모 누락');
        await open(width, restoreNamespace, 'backup');
        importJson(payload);
        await waitFor(() => frame.contentDocument.querySelector('[data-action="import"]'), '가져오기 확인 대화상자 누락');
        click('[data-action="import"]');
        assert(text('#toast').includes('병합 완료'), '가져오기 병합 실패');
        click('[data-nav="study"]');
        click('[data-pane="write"]');
        assert(find('#draft').value === answer + ' · 실전', '가져오기 답안 불일치');
        click('[data-nav="backup"]');
        importJson('{"schema":"unrelated"}');
        await waitFor(() => text('#toast').includes('가져오기 HOLD'), '잘못된 JSON을 차단하지 못했습니다.');
        assert([...baseline].every(([key, value]) => localStorage.getItem(key) === value), '실제 학습 기록이 변경되었습니다.');
      },
      review: async () => {
        click('[data-nav="study"]');
        click('[data-pane="compare"]');
        assert(text('#trace-content').includes(answer), '비교 화면에서 작성 답안 누락');
        click('[data-selfcheck]');
        click('[data-action="done"]');
        click('[data-action="wrong"]');
        click('[data-nav="review"]');
        assert(text('main').includes('복습 대상 · 1개'), '복습 목록 누락');
        click('[data-action="retest"]');
        assert(find('#draft').value === '', '재시험 첫 답안에 기존 답안이 입력되었습니다.');
        input('#draft', '재시험 새 답안');
        await reload();
        assert(find('#draft').value === '재시험 새 답안', '재시험 답안 복원 실패');
        click('[data-action="retest-stop"]');
        assert(text('.round-record').includes('재시험 새 답안'), '재시험 이력 누락');
        click('[data-question="' + mainId + '"]');
        click('[data-pane="write"]');
        assert(find('#draft').value === answer + ' · 실전', '기존 답안 보존 실패');
      },
      first: async () => {
        click('[data-stage="first"]');
        const details = find('#study-filters');
        details.open = true;
        input('#filter-year', '2026', 'change');
        input('#filter-subject', '노동법(1)', 'change');
        input('#filter-round', '35', 'change');
        assert(find('[data-selected-id]').dataset.selectedId === '2026-노동법(1)-001', '1차 연도·과목·회차 필터 오류');
        click('[data-choice="1"]');
        await reload();
        assert(text('#save-state').includes('저장된 선택 1번'), '1차 답안 복원 실패');
        click('[data-trace="1"]');
        const image = find('.source-image');
        await waitFor(() => image.naturalWidth, '1차 원본 이미지 로딩 실패');
        click('[data-trace="3"]');
        assert(text('#trace-content').includes('HOLD'), '1차 정답 근거 HOLD 표시 누락');
        click('[data-trace="4"]');
        assert(text('#trace-content').includes('학습용 해설 초안'), '1차 해설 초안 누락');
        checkWidth(width);
        click('[data-nav="verify"]');
        checkWidth(width);
      },
    };

    try {
      for (const [id, label] of cases) {
        status.textContent = width + 'px · ' + label + ' 검사 중';
        try {
          await casesById[id]();
          allChecks.push({width, id, status: 'PASS'});
        } catch (error) {
          allChecks.push({width, id, status: 'HOLD', reason: error.message});
        }
        display(allChecks);
      }
    } finally {
      clean(namespace);
      clean(restoreNamespace);
    }
  }

  document.querySelectorAll('[data-width]').forEach(button => button.onclick = async () => {
    try {
      await open(Number(button.dataset.width), 'manual-' + manual);
      status.textContent = button.textContent + ' 수동 점검 화면';
    } catch (error) {
      status.textContent = 'HOLD · ' + error.message;
    }
  });

  run.onclick = async () => {
    const buttons = [run, ...document.querySelectorAll('[data-width]')];
    buttons.forEach(button => { button.disabled = true; });
    const checks = [];
    try {
      const token = Date.now().toString(36);
      for (const width of widths) await runWidth(width, checks, token);
      const pass = checks.filter(check => check.status === 'PASS').length;
      const result = {
        revision: config.revision, origin: location.origin, checkedAt: new Date().toISOString(),
        scope: '같은 출처 브라우저 · 실제 HTTP · 화면 폭별 기능 시험', checks,
      };
      localStorage.setItem(config.resultKey, JSON.stringify(result));
      status.textContent = `검증 완료 · PASS ${pass}/${checks.length} · HOLD ${checks.length - pass}`;
      status.dataset.checkedAt = result.checkedAt;
    } catch (error) {
      status.textContent = '검증 HOLD · ' + error.message;
    } finally {
      buttons.forEach(button => { button.disabled = false; });
    }
  };
})();

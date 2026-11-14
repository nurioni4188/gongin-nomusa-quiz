(() => {
  'use strict';

  const icons={home:'M3 10 12 3l9 7v10a1 1 0 0 1-1 1h-5v-7H9v7H4a1 1 0 0 1-1-1Z',book:'M3 4c4-1 6 0 9 2 3-2 5-3 9-2v15c-4-1-6 0-9 2-3-2-5-3-9-2ZM12 6v15',check:'m5 12 4 4L19 6',shield:'M12 3 4 6v6c0 5 8 9 8 9s8-4 8-9V6ZM8 12l3 3 5-6',note:'M6 3h12v18l-6-4-6 4ZM9 7h6M9 10h6',chart:'M4 3v17h17M8 15v-4M13 15V7M18 15V4',arrow:'M4 12h16m-5-5 5 5-5 5',external:'M13 3h8v8m0-8L10 14M10 5H4v15h15v-6',clock:'M12 8v5l3 2M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0',download:'M12 3v12m-4-4 4 4 4-4M4 16v5h16v-5',upload:'M12 16V4m-4 4 4-4 4 4M4 16v5h16v-5',search:'M20 20l-5-5M17 10a7 7 0 1 1-14 0 7 7 0 0 1 14 0',warn:'m12 3 10 18H2ZM12 9v5m0 3v.1',folder:'M2 6h8l2 3h10v11H2Z',refresh:'M20 9a8 8 0 1 0 0 6M20 3v6h-6',lock:'M7 10V7a5 5 0 0 1 10 0v3M5 10h14v11H5ZM12 14v3',layers:'m12 3 10 5-10 5L2 8Zm-10 9 10 5 10-5M2 17l10 5 10-5',list:'M9 5h12M9 12h12M9 19h12M3 5h1M3 12h1M3 19h1',close:'m6 6 12 12M6 18 18 6'};

  const D = window.REVIEW_DATA;
  const S = window.HubState;
  const Q = window.QDATA;
  const E = window.N27_CATALOG?.items;
  const app = document.getElementById('app');
  const modal = document.getElementById('modal');
  if (!S || !Q?.length || !E?.length) {
    app.textContent = '학습 자료를 불러오지 못했습니다. 새로고침 후 다시 확인해 주세요.';
    return;
  }

  const firstRows = Q.map(row => ({
    ...row, stage: 'first', key: row.k, year: row.y, subject: row.s,
    topic: row.n + '번 문제', sourceText: row.q,
  }));
  const essayRows = E.map(row => ({...row, stage: 'essay', key: row.id, r: row.year - 1991}));
  const all = new Map([...essayRows, ...firstRows].map(row => [row.key, row]));
  const defaultId = essayRows.find(row => row.origin === 'V103_57' && row.year === 2025).key;
  const explanations = window.NOMUSA_V108_EXPLANATIONS?.entries || {};
  const dataCounts = {
    explanations: Object.keys(explanations).length,
    incomplete: firstRows.filter(row => row.o?.length !== 5).length,
    scanned: firstRows.filter(row => row.tx !== 'pdf').length,
  };
  const sourceRoot = document.body.dataset.sourceRoot;
  const sourcePath = relative => sourceRoot + relative.split('/').map(encodeURIComponent).join('/');
  const isVercelPreview = /^gongin-nomusa-rc27-preview-[a-z0-9]+\.vercel\.app$/.test(location.hostname);
  const nav = [
    ['home', 'home', '학습 대시보드', '홈'],
    ['study', 'book', '기출 학습', '기출 학습'],
    ['review', 'note', '오답·복습노트', '복습노트'],
    ['verify', 'shield', 'Preview 검증', '검증'],
    ['backup', 'folder', '기록 백업', '백업'],
  ];
  const title = Object.fromEntries(nav.map(([page, , label]) => [page, label]));
  const steps = [
    ['detail', '상세답안'], ['compressed', '시험장 압축답안'],
    ['write', '직접 작성'], ['compare', '비교·복습'],
  ];
  const traceLabels = ['문제 원문', '원본 페이지', '선택지·수식', '공식 정답 근거', '상세·압축답안', '검토 메모'];
  const escapeMap = {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'};
  const esc = value => String(value ?? '').replace(/[&<>"']/g, char => escapeMap[char]);
  const icon = name => `<svg viewBox="0 0 24 24" aria-hidden="true"><path d="${icons[name] || icons.book}"/></svg>`;
  const badge = status => `<span class="status ${status === 'PASS' ? 'pass' : 'hold'}">${esc(status)}</span>`;
  const button = (label, action, style = '', attr = '') =>
    `<button type="button" class="button ${style}" data-action="${action}" ${attr}>${label}</button>`;
  const link = (url, label, style = 'text-link') =>
    `<a class="${style}" href="${esc(url)}" target="_blank" rel="noopener noreferrer">${esc(label)} ${icon('external')}</a>`;
  const outsideLink = (url, label) => /^https:\/\//.test(url || '') ? link(url, label) : esc(label);
  const notice = (message, style = 'gray') => `<div class="notice ${style}">${icon(style ? 'shield' : 'warn')}<div>${message}</div></div>`;
  const pageTitle = (heading, description, action = '') =>
    `<div class="page-title"><div><h1>${heading}</h1><p>${description}</p></div>${action}</div>`;
  const groups = [['all', '모든 학습 단위'], ['new', '신규 57개 대문제'], ['old', '기존 71개 답안'], ['source', '원문 연습 87개']];
  const filtersFor = stage => ({stage, year: 'all', subject: 'all', round: 'all', group: 'all', query: ''});
  const examEnd = () => Math.max(Number(S.essay.examEnd) || 0, Number(S.hub.exam?.end) || 0);
  const locked = () => examEnd() > Date.now();
  const activeRetest = () => S.hub.rounds.find(row => row.id === S.hub.activeRetest && !row.finishedAt);
  const retestFor = row => {
    const round = activeRetest();
    return round?.ids.includes(row.key) ? round : null;
  };

  let selected = all.has(S.hub.lastId) ? S.hub.lastId : defaultId;
  if (locked() && all.has(S.hub.exam?.id)) selected = S.hub.exam.id;
  let view = Object.hasOwn(title, location.hash.slice(1)) ? location.hash.slice(1) : 'home';
  let pane = steps.some(([id]) => id === S.hub.lastPane) ? S.hub.lastPane : 'detail';
  let trace = view === 'study' && S.hub.lastId && all.get(selected).stage === 'essay' ? 4 : 0;
  let filters = filtersFor(all.get(selected).stage);
  let listOpen = false;
  let listPage = 0;
  let filterOpen = matchMedia('(min-width: 701px)').matches;
  let importPending;
  let toastTimer;
  let localReport;
  let reviewStage = 'all';

  function showToast(message) {
    const el = document.getElementById('toast');
    el.textContent = message;
    el.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => el.classList.remove('show'), 4200);
  }

  function save(name) {
    const ok = S.save(name);
    if (!ok) showToast(S.storageError || '저장 실패 · JSON으로 기록을 내보내세요.');
    return ok;
  }

  function complete(row) {
    if (row.stage === 'essay') return Boolean(S.essay.flags[row.key]);
    return Boolean(S.hub.completed[row.key] || S.hub.choices[row.key] || S.first.att[row.key]);
  }

  function needsReview(row) {
    if (Object.hasOwn(S.hub.wrong, row.key)) return Boolean(S.hub.wrong[row.key]);
    if (row.stage !== 'first') return false;
    const chosen = S.hub.choices[row.key];
    if (chosen) return !locked() && Array.isArray(row.a) && row.a.length > 0 && !row.a.includes(chosen);
    return S.first.att[row.key]?.ok === false;
  }

  function choiceFor(row) {
    const round = retestFor(row);
    return round ? round.choices?.[row.key] : S.hub.choices[row.key] ?? S.first.att[row.key]?.last;
  }

  function draftFor(row) {
    const round = retestFor(row);
    return round ? round.drafts?.[row.key] ?? '' : S.essay.drafts[row.key] ?? '';
  }

  function remember(id, nextPane = 'detail') {
    if (!all.has(id)) return;
    S.hub.lastId = id;
    S.hub.lastPane = nextPane;
    if (S.hub.exam) S.hub.exam.id = id;
    save('hub');
  }

  function route(page, updateUrl = true) {
    view = page;
    if (updateUrl && location.hash !== '#' + page) history.pushState(null, '', '#' + page);
    renderShell();
    window.scrollTo(0, 0);
    document.getElementById('main').focus({preventScroll: true});
  }

  function renderShell() {
    const navigation = className => nav.map(([id, symbol, label, short]) =>
      `<a href="#${id}" data-nav="${id}" class="${view === id ? 'active' : ''}" ${view === id ? 'aria-current="page"' : ''}>
        ${icon(symbol)}<span>${className === 'mobile-nav' ? short : label}</span>
      </a>`).join('');
    app.innerHTML = `
      <aside class="sidebar">
        <a class="brand" href="#home" data-nav="home"><img src="brand.svg" alt=""><div><b>누리온</b><small>공인노무사 학습실</small></div></a>
        <nav class="nav" aria-label="주 메뉴">${navigation('nav')}</nav>
        <div class="sidebar-bottom">
          <div class="protect">${icon('shield')}<div><b>Preview 전용</b><br>이 브라우저에 학습 기록 저장</div></div>
          ${locked() || S.qa ? '' : link(sourcePath('index.html'), '기존 1차 RC35 열기')}
        </div>
      </aside>
      <div class="page">
        <header class="topbar"><div class="breadcrumb"><b>${title[view]}</b></div>
          <div class="top-right"><span class="preview-pill"><i class="dot"></i>${S.qa ? '검증 기록 격리' : 'Preview'}</span></div>
        </header>
        <main class="main" id="main" tabindex="-1"></main>
      </div>
      <nav class="mobile-nav" aria-label="모바일 메뉴">${navigation('mobile-nav')}</nav>`;
    renderMain();
  }

  function renderMain() {
    const pages = {home: renderHome, study: renderStudy, review: renderReview, verify: renderVerify, backup: renderBackup};
    document.getElementById('main').innerHTML =
      (S.storageError ? notice(esc(S.storageError), 'red') : '') +
      (locked() ? renderExam() : '') + renderRetestBanner() + pages[view]() +
      `<footer class="footer"><span>누리온 · 공인노무사 학습·검증 허브</span><span>${esc(D.sourceVersion)}</span></footer>`;
    bindFields();
  }

  function renderHome() {
    const row = all.get(selected) || all.get(defaultId);
    const doneEssay = essayRows.filter(complete).length;
    const doneFirst = firstRows.filter(complete).length;
    return pageTitle('공인노무사 기출 학습', '2차 논술 답안 작성과 1차 기출 문제풀이를 이어가세요.') +
      `<section class="hero">
        <div><p class="hero-kicker">2013–2026 · 2차 답안학습</p>
          <h2>기출문제 풀이부터<br>답안 작성과 복습까지</h2>
          <p>상세답안 → 시험장 압축답안 → 직접 작성 → 비교·복습</p>
          <div class="hero-actions">
            ${button('2차 답안학습 시작 ' + icon('arrow'), 'start-essay', 'white')}
            ${button('최근 문항 이어풀기', 'continue', 'ghost')}
          </div>
        </div>
      </section>
      <section class="stats" aria-label="학습 자료 범위">
        <div class="stat"><div class="stat-top">2차 · 2013–2026 ${icon('book')}</div><strong>215</strong><span class="unit">개 연습 단위</span><p>학습 초안 128개 · 원문 연습 87개</p></div>
        <div class="stat"><div class="stat-top">1차 · 2022–2026 ${icon('layers')}</div><strong>1,020</strong><span class="unit">문항</span><p>${button('1차 문제풀이', 'start-first', 'mini')}</p></div>
        <div class="stat"><div class="stat-top">2차 · 신규 대문제 ${icon('note')}</div><strong>57</strong><span class="unit">개 대문제</span><p>${button('신규 대문제 보기', 'new57', 'mini')}</p></div>
      </section>
      <div class="grid-main"><div>
        <section class="card"><div class="section-head"><div><h2>2차 연도별 기출</h2><p>연도를 선택하면 해당 기출문제를 볼 수 있습니다.</p></div></div>
          <div class="year-grid">${Array.from({length: 14}, (_, i) => 2026 - i).map(year => {
            const rows = essayRows.filter(item => item.year === year);
            return `<button class="year-card ${year === 2026 ? 'current' : ''}" data-year="${year}"><b>${year}</b><small>${rows.length}개</small><div class="tinybar"><span style="width:${rows.filter(complete).length / rows.length * 100}%"></span></div></button>`;
          }).join('')}</div>
        </section>
        <section class="card"><div class="section-head"><h2>내 학습 진도</h2></div>
          ${progressLine('2차 복습 완료', doneEssay, essayRows.length)}
          ${progressLine('1차 풀이 기록', doneFirst, firstRows.length)}
          <p class="muted small">최근 문항 · ${row.year}년 ${esc(row.subject)} · ${esc(row.topic)}</p>
        </section></div>
        <div><section class="card"><div class="section-head"><h2>Preview 검증</h2></div>
          <p class="muted">PC 1440px와 모바일 360·390px에서 답안 저장, 복원, 실전 모드와 JSON 백업을 확인합니다.</p>
          ${button('검증 대시보드', 'verify', 'primary')}
          ${!locked() && !S.qa ? `<p class="original-link">${link(sourcePath('index.html'), '기존 1차 RC35')}</p>` : ''}
        </section></div>
      </div>`;
  }

  function progressLine(label, count, total) {
    const pct = total ? Math.round(100 * count / total) : 0;
    return `<div class="progress-section"><div class="progress-heading"><span>${label} <b>${count.toLocaleString('ko-KR')} / ${total.toLocaleString('ko-KR')}</b></span><span>${pct}%</span></div>
      <progress class="learning-progress" max="${total || 1}" value="${count}" aria-label="${label}">${pct}%</progress></div>`;
  }

  function questionRows() {
    const round = activeRetest();
    const groupMatch = row => filters.group === 'all' ||
      (filters.group === 'new' && row.origin === 'V103_57') ||
      (filters.group === 'old' && row.origin === 'EX_MA_2024_2026') ||
      (filters.group === 'source' && row.sourceOnly);
    const query = filters.query.trim().toLowerCase();
    return (filters.stage === 'essay' ? essayRows : firstRows).filter(row =>
      (!round || round.ids.includes(row.key)) &&
      (filters.year === 'all' || String(row.year) === filters.year) &&
      (filters.subject === 'all' || row.subject === filters.subject) &&
      (filters.round === 'all' || String(row.r) === filters.round) &&
      groupMatch(row) &&
      (!query || [row.key, row.topic, row.subject, row.sourceText].join(' ').toLowerCase().includes(query)));
  }

  function selectOptions(values, value) {
    return values.map(([id, label]) =>
      `<option value="${esc(id)}" ${String(id) === String(value) ? 'selected' : ''}>${esc(label)}</option>`).join('');
  }

  function renderStudy() {
    const rows = questionRows();
    if (rows.length && !rows.some(row => row.key === selected)) {
      selected = rows[0].key;
      trace = 0;
      pane = rows[0].sourceOnly || activeRetest() ? 'write' : 'detail';
      remember(selected, pane);
    }
    const row = rows.find(item => item.key === selected);
    const essay = filters.stage === 'essay';
    const pool = essay ? essayRows : firstRows;
    const years = [...new Set(pool.map(item => item.year))].sort((a, b) => b - a);
    const subjects = [...new Set(pool.map(item => item.subject))].sort((a, b) => a.localeCompare(b, 'ko'));
    const rounds = [...new Set(pool.map(item => item.r))].sort((a, b) => b - a);
    const pages = Math.max(1, Math.ceil(rows.length / 30));
    listPage = Math.min(Math.max(0, listPage), pages - 1);
    return pageTitle(essay ? '2차 답안학습' : '1차 기출 문제풀이',
      essay ? '2013–2026년 · 215개 연습 단위' : '2022–2026년 · 1,020문항',
      button(icon('clock') + ' 실전 모드', 'exam', '', row && !locked() ? '' : 'disabled')) +
      `<div class="study-toolbar">
        <div class="segmented" aria-label="시험 단계">
          <button data-stage="essay" aria-pressed="${essay}" class="${essay ? 'active' : ''}">2차 논술</button>
          <button data-stage="first" aria-pressed="${!essay}" class="${essay ? '' : 'active'}">1차 객관식</button>
        </div>
        ${!essay && !locked() && !S.qa ? link(sourcePath('index.html'), '기존 RC35') : ''}
      </div>
      <details class="study-filters" id="study-filters" ${filterOpen ? 'open' : ''}>
        <summary>연도·과목·회차 필터 <span>${rows.length.toLocaleString('ko-KR')}개</span></summary>
        <label class="search-field">${icon('search')}<input id="search" type="search" aria-label="문항 검색" placeholder="문제 · 논점 · ID 검색" value="${esc(filters.query)}"></label>
        <div class="filters">
          <label class="field">연도<select id="filter-year">${selectOptions([['all', '전체 연도'], ...years.map(year => [year, year + '년'])], filters.year)}</select></label>
          <label class="field">과목<select id="filter-subject">${selectOptions([['all', '전체 과목'], ...subjects.map(subject => [subject, subject])], filters.subject)}</select></label>
          <label class="field">시험 회차<select id="filter-round">${selectOptions([['all', '전체 회차'], ...rounds.map(round => [round, '제' + round + '회'])], filters.round)}</select></label>
          ${essay ? `<label class="field">학습 자료<select id="filter-group">${selectOptions(groups, filters.group)}</select></label>` : ''}
        </div>
      </details>
      <div class="study-list-control">
        ${button(listOpen ? '문제 목록 닫기' : '문제 목록 열기', 'list-toggle', 'mini mobile-list-toggle', `aria-expanded="${listOpen}" aria-controls="question-list"`)}
        <span class="muted small">${rows.length.toLocaleString('ko-KR')}개 ${essay ? '연습 단위' : '문항'}</span>
      </div>
      <div class="study-grid">
        <aside id="question-list" class="question-list ${listOpen ? 'open' : ''}" aria-label="문제 목록">
          <div class="list-head">${listPage + 1} / ${pages} 페이지</div>
          ${rows.slice(listPage * 30, (listPage + 1) * 30).map(renderQuestion).join('') || '<div class="empty">조건에 맞는 문항이 없습니다.</div>'}
          <div class="list-pagination">${button('이전', 'list-prev', 'mini', listPage ? '' : 'disabled')}
            ${button('다음', 'list-next', 'mini', listPage + 1 < pages ? '' : 'disabled')}</div>
        </aside>
        <section class="card study-detail" aria-label="문항 상세">
          ${row ? renderDetail(row, rows) : '<div class="empty">필터를 변경해 문항을 선택하세요.</div>'}
        </section>
      </div>`;
  }

  function renderQuestion(row) {
    const kind = row.stage === 'first' ? '1차 기출' : row.sourceOnly ? '원문 연습' :
      row.origin === 'V103_57' ? '신규 대문제 · 학습 초안' : '기존 학습 초안';
    return `<button class="question-item ${selected === row.key ? 'active' : ''}" data-question="${esc(row.key)}" aria-pressed="${selected === row.key}">
      <small>${row.year}년 · ${esc(row.subject)}</small><b>${esc(row.topic)}</b>
      ${row.stage === 'first' && row.q ? `<span class="q-title">${esc(row.q)}</span>` : ''}
      <small>${kind}${complete(row) ? ' · 학습 기록 있음' : ''}</small>
    </button>`;
  }

  function renderDetail(row, rows) {
    const essay = row.stage === 'essay';
    const round = retestFor(row);
    const isExam = locked();
    const index = rows.indexOf(row);
    const status = essay ? (row.sourceOnly ? '원문 중심 직접 작성' : '학습용 답안 초안 · 독립 승인 HOLD') : '수록 정답 근거 확인 HOLD';
    if (isExam && trace > 2) trace = 0;
    const points = typeof row.points === 'number' ? row.points + '점' : row.points;
    return `
      <div class="tags" data-selected-id="${esc(row.key)}">
        <span class="tag">${row.year}년 · 제${row.r}회</span><span class="tag">${esc(row.subject)}</span>
        ${essay && points ? `<span class="tag">${esc(points)}</span>` : ''}${badge('HOLD')}
      </div>
      <h2 class="detail-title">${esc(row.topic)}</h2>
      <p class="detail-id">${esc(row.key)} · ${status}</p>
      <div class="trace" role="group" aria-label="문항 근거 추적">
        ${traceLabels.map((label, index) =>
          `<button type="button" data-trace="${index}" class="${trace === index ? 'active' : ''}" aria-pressed="${trace === index}" ${isExam && index > 2 ? 'disabled' : ''}>${label}</button>`).join('')}
      </div>
      ${essay && !isExam ? `<div class="learning-flow" role="group" aria-label="2차 답안학습 단계">
        ${steps.map(([id, label]) => `<button type="button" data-pane="${id}" class="${trace === 4 && pane === id ? 'active' : ''}" aria-pressed="${trace === 4 && pane === id}" ${row.sourceOnly && ['detail', 'compressed'].includes(id) ? 'disabled' : ''}>${label}</button>`).join('')}
      </div>` : ''}
      <div id="trace-content">${traceContent(row)}</div>
      ${essay ? (isExam ? renderWriter(row) : '') : renderChoices(row)}
      <div class="row detail-actions">
        ${button('← 이전 문항', 'q-prev', 'mini', index > 0 ? '' : 'disabled')}
        ${button('다음 문항 →', 'q-next', 'mini', index + 1 < rows.length ? '' : 'disabled')}
        <div class="spacer"></div>
        ${isExam ? '' : button(needsReview(row) ? '복습 필요 해제' : '복습 필요 표시', 'wrong', 'mini')}
        ${isExam || (!essay && !round) ? '' : button((round ? round.completed?.[row.key] : complete(row)) ? '복습 완료 취소' : '복습 완료', 'done', 'mini')}
      </div>`;
  }

  function traceContent(row) {
    switch (trace) {
      case 1: return originalPage(row);
      case 2: return optionsPanel(row);
      case 3: return evidencePanel(row);
      case 4: return row.stage === 'essay' ? essayPanel(row) : explanationPanel(row);
      case 5: return notePanel(row);
      default: {
        const transcribed = row.sourceImageTextRestored ? '스캔 수기 전사 · 재대조 HOLD' :
          row.stage === 'first' && row.tx !== 'pdf' ? '스캔·이미지형 · 원본 문항 이미지와 대조하세요.' : '';
        return `<h3 class="panel-title">기출문제 원문</h3>
          ${transcribed ? notice(transcribed, '') : ''}
          <div class="source-text">${esc(row.sourceText || '추출 텍스트 미확보 · 원본 페이지를 열어 보세요.')}</div>
          <div class="row source-actions">${button('원본 페이지 확인', 'source', 'mini')}</div>`;
      }
    }
  }

  function originalPage(row) {
    if (row.stage === 'first') {
      const url = sourcePath('img/' + row.img);
      return `<h3 class="panel-title">원본 문항 이미지</h3>
        <p class="muted small">${esc(row.src)} · 원본 ${esc((row.pg || []).join(', ') || '미확인')}쪽</p>
        <img class="source-image" src="${esc(url)}" alt="${esc(row.key)} 원본 문항 이미지">
        ${link(url, '이미지 확대')}<p class="footer-note">시험지에서 잘라낸 문항 이미지입니다. 전체 시험지 PDF 경로는 미확인입니다.</p>`;
    }
    if (!row.pdfPath) return `<h3 class="panel-title">원본 페이지</h3>${notice('원본 PDF 연결 HOLD', '')}`;
    const page = Number(row.pdfPage) || 1;
    const pageHint = row.pdfPageVerification === 'FIRST_PAGE_ONLY_REVIEW_REQUIRED'
      ? '해당 과목 PDF 첫 페이지입니다. 정확한 문항 위치는 대조가 필요합니다.'
      : '원본에서 문항 번호와 배점을 확인하세요.';
    return `<h3 class="panel-title">기출 원본 PDF</h3>
      <p class="muted small">${esc(row.basis || '기출 시험지')}</p>
      ${link(sourcePath(row.pdfPath) + '#page=' + page, row.year + '년 PDF · ' + page + '쪽 열기', 'button primary')}
      <p class="footer-note">${pageHint}</p>`;
  }

  function optionsPanel(row) {
    const options = row.o || [];
    const content = row.stage === 'essay' ?
      `<p class="answer">${row.mathEvidence ? '수식 근거 메타데이터가 연결되어 있습니다.' : '논술형 문항입니다.'} 원본에서 수식·기호·수치와 배점을 대조하세요.</p>` :
      (options.length ? options.map((text, index) => `<button type="button" class="option ${choiceFor(row) === index + 1 ? 'active' : ''}" data-choice="${index + 1}" ${index >= 5 ? 'disabled' : ''} aria-pressed="${choiceFor(row) === index + 1}"><span class="num">${index + 1}</span><span>${esc(text)}</span></button>`).join('') :
        '<div class="empty">선택지 텍스트 미확보 · 원본 문항 이미지에서 확인하세요.</div>');
    return `<h3 class="panel-title">선택지·수식 대조</h3>
      ${row.stage === 'first' ? notice(esc(row.sourceImageTextRestored ? '스캔 수기 전사 · 재대조 HOLD' :
        options.length === 5 ? '선택지 5개 수록 · 수식과 기호는 원본을 기준으로 확인하세요.' : '선택지 구조 확인 HOLD · 추출 ' + options.length + '개'), options.length === 5 ? 'gray' : '') : ''}
      ${content}<div class="row source-actions">${button('원본과 대조하기', 'source', 'mini')}</div>`;
  }

  function evidencePanel(row) {
    if (locked()) return '';
    const heading = '<h3 class="panel-title">공식 정답 근거</h3>';
    if (row.stage === 'first') {
      const picked = choiceFor(row);
      const comparison = picked ? `<p class="muted small">선택 ${picked}번 · 수록 후보와 ${row.a?.includes(picked) ? '일치' : '불일치'} · 연습용 대조</p>` : '';
      return heading + notice('문항별 공식 정답 원본 및 페이지 대조 HOLD', '') +
        `<div class="source-text">수록 정답 후보 ${esc(row.a?.join(', ') || '미확보')}번
원장 대조 표기 ${esc(row.chk || '미확인')}
출처 기록 ${esc(window.QMETA.answerSources[row.year] || '미확인')}</div>
        ${comparison}<div class="row source-actions">${link(D.qnetAnswers, 'Q-Net 최종정답 목록')}</div>`;
    }
    const audit = window.N1075_AUDIT;
    const record = audit?.items?.[row.key];
    const legal = window.N1076_EVIDENCE?.legal?.[row.key];
    const official = legal?.officialLinks?.map(([label, url]) => [label, url]) || [];
    const refs = [
      ...(record?.academicRefs || []).map(id => audit.academic[id]).filter(Boolean),
      ...(record?.lawRefs || []).map(id => audit.laws[id]).filter(Boolean),
      ...(record?.caseRefs || []).map(id => audit.cases[id]).filter(Boolean),
    ].map(ref => [ref.title, ref.url, ref.warning]);
    const links = [...official, ...refs];
    return heading + notice('공식 모범답안 미확보 · 독립 승인 HOLD', '') +
      `<p class="muted">${esc(row.basis || '학습자료 출처 미확인')}</p>
        ${links.length ? `<h4>문항별 학습 참고 근거</h4><ul class="evidence-links">
          ${links.map(([label, url, warning]) => `<li>${outsideLink(url, label)}${warning ? `<small>${esc(warning)}</small>` : ''}</li>`).join('')}
        </ul><p class="footer-note">시험 당시 적용 법령·판례와 문항 적용 관계는 확인이 필요합니다.</p>` : ''}`;
  }

  function explanationPanel(row) {
    if (locked()) return '';
    const entry = explanations[row.key];
    if (!entry) return '<div class="empty">이 문항의 선택지 해설은 작성 대기 중입니다.</div>';
    return `<h3 class="panel-title">선택지별 해설</h3>${notice('학습용 해설 초안 · 승인 HOLD', '')}
      <p class="answer">${esc(entry.summary)}</p>
      <ol class="explanation-list">${(entry.options || []).map(value => `<li>${esc(value)}</li>`).join('')}</ol>
      ${entry.mnemonic ? `<p class="answer">${esc(entry.mnemonic)}</p>` : ''}
      <ul class="evidence-links">${(entry.sources || []).map(ref =>
        `<li>${outsideLink(ref.url, ref.title)}${ref.basis ? `<small>${esc(ref.basis)}</small>` : ''}</li>`).join('')}</ul>`;
  }

  // Use the same original paragraph excerpts as the RC35 essay module when no
  // authored compact answer is present.
  function compactExcerpt(section) {
    const raw = String(section.detailed || '').trim();
    const headings = raw.split(/(?=^\s*[ⅠⅡⅢⅣⅤⅥⅦ]\.\s)/m).map(text => text.trim()).filter(Boolean);
    const blocks = headings.length > 1 ? headings : raw.split(/\n\s*\n/).filter(Boolean);
    return blocks.slice(0, 5).map(block => {
      const [head, ...lines] = block.split(/\n+/).map(line => line.trim()).filter(Boolean);
      return [head, lines.find(line => line.length >= 30) || lines[0]].filter(Boolean).join('\n');
    }).filter(Boolean).join('\n\n');
  }

  function compactAnswers(row) {
    return row.sections.map(section => `<article class="answer">
      <h4>${esc(section.title)}</h4>${section.compressed ? '' : '<small class="answer-label">상세답안 발췌 · 학습용</small>'}
      ${esc(section.compressed || compactExcerpt(section) || '압축답안 미수록')}
    </article>`).join('');
  }

  function detailedAnswers(row) {
    const expanded = window.N1078_ESSAYS?.items?.[row.key];
    const improved = window.N1074_QUALITY?.items?.[row.key]?.improvedDraft;
    const original = row.sections.map(section =>
      `<article class="answer"><h4>${esc(section.title)}</h4>${esc(section.detailed)}</article>`).join('');
    if (!expanded && !improved) return original;
    const learningDraft = expanded ? expanded.parts.map(part =>
      `<article class="answer"><h4>${esc(part.heading)}</h4>${esc(part.text)}</article>`).join('') :
      `<article class="answer">${esc(improved)}</article>`;
    return learningDraft + `<details class="original-answer"><summary>기존 상세답안 초안 열기</summary>${original}</details>`;
  }

  function essayPanel(row) {
    if (locked()) return '';
    if (pane === 'write') return renderWriter(row);
    if (pane === 'compare') {
      return `<h3 class="panel-title">내 답안과 비교·복습</h3>
        <div class="split">
          <div><h4>내가 작성한 답안</h4><div class="answer">${esc(draftFor(row) || '작성 기록이 없습니다.')}</div></div>
          <div><h4>${row.sourceOnly ? '비교 자료' : '학습용 압축답안'}</h4>
            ${row.sourceOnly ? '<p class="answer">원본 시험지와 작성한 답안을 직접 대조하세요.</p>' : compactAnswers(row)}</div>
        </div>${checklist(row)}`;
    }
    if (row.sourceOnly) return `<h3 class="panel-title">원문 연습</h3><p>원본 PDF를 확인하고 답안을 직접 작성하세요.</p>
      ${button('직접 작성하기', 'write', 'primary')}`;
    const detail = pane === 'detail';
    return `<h3 class="panel-title">${detail ? '상세 학습답안' : '시험장 압축답안'}</h3>
      ${notice('학습용 초안 · 독립 승인 HOLD', '')}
      <div class="answer-pane">${detail ? detailedAnswers(row) : compactAnswers(row)}</div>
      <div class="row source-actions">${button(detail ? '시험장 압축답안 보기 →' : '직접 작성하기 →',
        detail ? 'compressed' : 'write', 'primary')}</div>`;
  }

  function checklist(row) {
    const entries = row.sections.flatMap((section, index) => (section.reviewChecklist || [])
      .map((text, part) => [index + '-' + part, text])).slice(0, 48);
    const items = entries.length ? entries : [
      ['0-0', '문제의 요구사항과 배점을 대조했다'],
      ['0-1', '핵심 법리·이론 또는 수식 근거를 대조했다'],
      ['0-2', '사안 적용과 결론을 다시 읽었다'],
    ];
    return `<div class="checklist"><h4>내 답안 점검</h4>${items.map(([key, text]) =>
      `<label class="check-item"><input type="checkbox" data-selfcheck="${key}" ${S.essay.checks[row.key]?.[key] ? 'checked' : ''}><span>${esc(text)}</span></label>`).join('')}</div>`;
  }

  function notePanel(row) {
    if (locked()) return '';
    const note = S.hub.notes[row.key] ?? (row.stage === 'first' ? S.first.memo[row.key] : '');
    return `<h3 class="panel-title">검토 메모</h3>
      <label class="field">원문 대조 결과 · 보완할 논점<textarea id="memo" rows="6" maxlength="5000" placeholder="근거 파일명·쪽수와 확인이 필요한 부분을 기록하세요.">${esc(note)}</textarea></label>
      <span id="memo-save" class="save-state">입력 즉시 자동저장</span>`;
  }

  function renderWriter(row) {
    const draft = draftFor(row);
    return `<div class="writer">
      <div class="section-head"><h3>${retestFor(row) ? '재시험 답안 작성' : '내 답안 작성'}</h3>
        <span class="save-state" id="save-state" aria-live="polite">${draft ? '저장된 답안 복원됨' : '입력 즉시 자동저장'}</span></div>
      <textarea id="draft" aria-label="내 답안" maxlength="299999" placeholder="쟁점 → 관련 법리·이론 → 사안 적용 → 결론">${esc(draft)}</textarea>
      <div class="row">${button('답안 구성 틀 넣기', 'outline', 'mini')}
        <span class="muted small" id="char-count">${Array.from(draft).length.toLocaleString('ko-KR')}자</span>
        ${locked() ? '' : button('비교·복습 →', 'compare', 'mini primary')}</div>
    </div>`;
  }

  function renderChoices(row) {
    const picked = choiceFor(row);
    return `<div class="writer"><div class="section-head"><h3>선택 답안 기록</h3>
      <span class="save-state" id="save-state">${picked ? '저장된 선택 ' + picked + '번' : '선택 즉시 자동저장'}</span></div>
      <div class="row">${[1, 2, 3, 4, 5].map(number =>
        `<button type="button" class="button ${picked === number ? 'primary' : ''}" data-choice="${number}" aria-pressed="${picked === number}">${number}번</button>`).join('')}</div>
    </div>`;
  }

  function renderExam() {
    const seconds = Math.max(0, Math.ceil((examEnd() - Date.now()) / 1000));
    const timer = String(Math.floor(seconds / 60)).padStart(2, '0') + ':' + String(seconds % 60).padStart(2, '0');
    return `<div class="exam-bar"><div><b>20분 실전 연습</b><small>정답·학습답안 잠금</small></div>
      <strong id="exam-clock" role="timer">${timer}</strong>${button('실전 종료', 'exam-stop', 'white mini')}</div>`;
  }

  function renderRetestBanner() {
    const round = activeRetest();
    if (!round) return '';
    const count = round.ids.filter(id => round.completed?.[id] || round.drafts?.[id]?.trim() || round.choices?.[id]).length;
    return `<div class="notice gray retest-banner"><div><b>재시험 진행 중 · ${count}/${round.ids.length}개 기록</b>
      <small>회차의 답안은 기존 풀이와 별도로 저장됩니다.</small></div>${button('회차 종료', 'retest-stop', 'mini', locked() ? 'disabled' : '')}</div>`;
  }

  function reviewRows() {
    return [...all.values()].filter(row => needsReview(row) && (reviewStage === 'all' || reviewStage === row.stage));
  }

  function renderReview() {
    const rows = reviewRows();
    const rounds = S.hub.rounds.slice().reverse();
    const labels = [['all', '전체'], ['essay', '2차 복습'], ['first', '1차 오답·복습']];
    const reason = row => {
      if (row.stage !== 'first' || Object.hasOwn(S.hub.wrong, row.key)) return '';
      return S.hub.choices[row.key] ? ' · 수록 후보와 불일치' : ' · RC35 오답 이력';
    };
    return pageTitle('오답·복습노트', '복습이 필요한 문항을 모아 다시 풀고 회차별 답안을 확인하세요.',
      button(icon('refresh') + ' 재시험 시작', 'retest', 'primary', rows.length && !locked() && !activeRetest() ? '' : 'disabled')) +
      `<section class="card">
        <div class="section-head"><h2>복습 대상 · ${rows.length}개</h2></div>
        <label class="field review-filter">복습 범위<select id="review-stage">${selectOptions(labels, reviewStage)}</select></label>
        ${rows.map(row => `<div class="mini-row review-row"><div><b>${esc(row.topic)}</b>
          <p>${row.year}년 · ${esc(row.subject)}${reason(row)}</p></div>
          <button class="button mini" data-question="${esc(row.key)}">문항 열기</button></div>`).join('') ||
        '<div class="empty">기출 학습에서 복습이 필요한 문항을 표시하세요.</div>'}
      </section>
      <section class="card"><div class="section-head"><h2>재시험 이력</h2></div>
        ${locked() ? '<p>실전 종료 후 회차별 답안을 확인할 수 있습니다.</p>' : rounds.map(renderRound).join('') ||
        '<div class="empty">저장된 재시험 회차가 없습니다.</div>'}
      </section>`;
  }

  function renderRound(round) {
    const date = new Date(round.startedAt).toLocaleString('ko-KR', {timeZone: 'Asia/Seoul'});
    return `<details class="round-record"><summary>${esc(date)} · ${round.ids.length}개 문항 · ${round.finishedAt ? '종료' : '미완료'}</summary>
      ${round.ids.map(id => {
        const row = all.get(id);
        if (!row) return '';
        const value = row.stage === 'essay' ? round.drafts?.[id] : round.choices?.[id] ? round.choices[id] + '번 선택' : '';
        return `<div class="answer"><h4>${row.year}년 ${esc(row.subject)} · ${esc(row.topic)}</h4>
          ${esc(value || '작성 기록 없음')}${round.completed?.[id] ? '<small class="answer-label">복습 완료</small>' : ''}</div>`;
      }).join('')}</details>`;
  }

  function currentVerification() {
    try {
      const raw = localStorage.getItem(window.HUB_QA.resultKey);
      const result = JSON.parse(raw || 'null');
      return result?.revision === D.version && result?.origin === location.origin && Array.isArray(result.checks) ? result : null;
    } catch {
      return null;
    }
  }

  function renderVerify() {
    const matrix = window.HUB_QA;
    const remote = isVercelPreview ? currentVerification() : D.deployment?.browser;
    const verified = remote?.checks.filter(check => check.status === 'PASS').length || 0;
    const local = localReport?.checks || [];
    const prior = local.filter(check => check.status === 'PASS').length;
    const cell = (data, width, id) => {
      const check = data?.find(entry => entry.width === width && entry.id === id);
      return `<td>${badge(check?.status === 'PASS' ? 'PASS' : 'HOLD')}${check?.reason ? `<small>${esc(check.reason)}</small>` : ''}</td>`;
    };
    const table = checks => `<table class="verify-matrix"><thead><tr><th scope="col">검증 항목</th>
      ${matrix.widths.map(width => `<th scope="col">${width === 1440 ? 'PC' : '모바일'}<small>${width}px</small></th>`).join('')}
      </tr></thead><tbody>${matrix.checks.map(([id, label]) => `<tr><th scope="row">${label}</th>
      ${matrix.widths.map(width => cell(checks, width, id)).join('')}</tr>`).join('')}</tbody></table>`;
    return pageTitle('Preview 검증 대시보드', '답안 작성·저장·복원·실전 모드·JSON 백업을 화면 폭별로 확인합니다.',
      `<a class="button primary" href="qa.html">${icon('check')} 검증 실행</a>`) +
      `<section class="card">
        <div class="section-head"><div><h2>Vercel Preview 브라우저</h2><p>${esc(D.project)}</p></div>${badge(verified === matrix.widths.length * matrix.checks.length ? 'PASS' : 'HOLD')}</div>
        <p class="muted">${isVercelPreview ? '현재 Preview에서 검증을 실행하면 이 브라우저의 결과를 아래 표에 기록합니다.' :
          'Vercel의 Preview 전용 경로에서 기능을 확인할 수 있습니다.'}</p>
        ${D.deployment?.url && !isVercelPreview ? `<p>${link(D.deployment.url, '기존 Vercel 프로젝트의 학습 Preview 열기')}</p>` : ''}
        ${remote ? `<p class="muted small">실행 ${esc(new Date(remote.checkedAt).toLocaleString('ko-KR', {timeZone: 'Asia/Seoul'}))} · PASS ${verified}/${remote.checks.length}</p>` : ''}
        ${table(remote?.checks)}
      </section>
      <section class="card">
        <div class="section-head"><div><h2>Sites 검토본 브라우저</h2><p>같은 학습 소스를 실행한 브라우저 화면 폭 시험</p></div>${badge(local.length && prior === local.length ? 'PASS' : 'HOLD')}</div>
        ${local.length ? `<p class="muted small">PASS ${prior}/${local.length} · 실기기 시험 HOLD</p>${table(local)}` : '<p class="muted">시험 결과를 불러오는 중입니다.</p>'}
      </section>
      <section class="card">
        <div class="section-head"><h2>자료 검토</h2></div>
        <div class="mini-row"><span>2차 시험지 PDF ${D.sourcePdfs}개 연결</span>${badge('PASS')}</div>
        <div class="mini-row"><span>2차 학습용 초안 128개 · 독립 승인 0개</span>${badge('HOLD')}</div>
        <div class="mini-row"><span>1차 학습용 해설 ${dataCounts.explanations}개 · 미작성 ${firstRows.length - dataCounts.explanations}개</span>${badge('HOLD')}</div>
        <div class="mini-row"><span>1차 스캔·이미지형 ${dataCounts.scanned}개 · 선택지 5개 미충족 ${dataCounts.incomplete}개</span>${badge('HOLD')}</div>
        <div class="mini-row"><span>Android·iOS 실기기</span>${badge('HOLD')}</div>
        <p class="footer-note">${esc(D.sourceVersion)} 원본 ${D.baselineFiles.toLocaleString('ko-KR')}개 대조 · 해설 자료 ${esc(D.explanationVersion)}</p>
      </section>${verificationNotes()}`;
  }

  function verificationNotes() {
    const records = S.hub.logs || [];
    return `<section class="card"><div class="section-head"><h2>수동 점검 메모</h2>${button('메모 남기기', 'manual-note', 'mini')}</div>
      ${records.length ? records.slice().reverse().map(record => `<div class="log"><b>${esc(record.name || '수동 점검')}</b>
        <p>${esc(record.env || '')} · ${esc(record.date || '')}</p><p>${esc(record.note)}</p></div>`).join('') :
        '<p class="muted">실기기에서 확인한 환경과 결과를 기록할 수 있습니다.</p>'}
    </section>`;
  }

  function renderBackup() {
    return pageTitle('학습 기록 백업', '기기나 Preview 주소를 바꿀 때 JSON으로 학습 기록을 옮기세요.') +
      `<section class="card">
        <div class="section-head"><h2>내보내기</h2></div>
        <div class="backup-actions">
          ${button(icon('download') + ' 전체 학습 JSON', 'export', 'primary')}
          ${button('기존 1차 형식', 'export-first')}${button('기존 2차 형식', 'export-essay')}
        </div>
        <p class="footer-note">전체 학습 JSON에는 복습 메모와 재시험 기록이 포함됩니다.</p>
      </section>
      <section class="card">
        <div class="section-head"><h2>가져오기</h2></div>
        <label class="upload-box">${icon('upload')}<b>JSON 파일 선택</b>
          <span>전체 학습 또는 기존 RC35 1차·2차 백업</span><input id="import-file" type="file" accept=".json,application/json" aria-label="JSON 파일 선택"></label>
        <p class="footer-note">문항 ID와 형식을 검사한 뒤 가져올 기록을 확인할 수 있습니다.</p>
      </section>`;
  }

  function download(value, filename) {
    const url = URL.createObjectURL(new Blob([JSON.stringify(value, null, 2)], {type: 'application/json'}));
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = filename;
    document.body.append(anchor);
    anchor.click();
    anchor.remove();
    setTimeout(() => URL.revokeObjectURL(url), 2000);
    showToast('JSON 백업을 준비했습니다.');
  }

  function showDialog(html) {
    modal.innerHTML = `<button class="close-dialog" data-action="close" aria-label="닫기">×</button>${html}`;
    modal.showModal();
  }

  function bindFields() {
    const fieldset = document.getElementById('study-filters');
    if (fieldset) fieldset.ontoggle = () => { filterOpen = fieldset.open; };
    for (const key of ['year', 'subject', 'round', 'group']) {
      const field = document.getElementById('filter-' + key);
      if (field) field.onchange = () => {
        filters[key] = field.value;
        if (key === 'year' && filters.round !== 'all' && Number(field.value) - 1991 !== Number(filters.round)) filters.round = 'all';
        if (key === 'round' && filters.year !== 'all' && Number(field.value) + 1991 !== Number(filters.year)) filters.year = 'all';
        listPage = 0;
        renderMain();
        document.getElementById(field.id)?.focus({preventScroll: true});
      };
    }
    const search = document.getElementById('search');
    if (search) search.oninput = event => {
      if (event.isComposing) return;
      const at = search.selectionStart;
      filters.query = search.value;
      listPage = 0;
      renderMain();
      const replacement = document.getElementById('search');
      replacement.focus({preventScroll: true});
      if (at !== null) replacement.setSelectionRange(at, at);
    };
    const stage = document.getElementById('review-stage');
    if (stage) stage.onchange = () => { reviewStage = stage.value; renderMain(); };
    const draft = document.getElementById('draft');
    if (draft) draft.oninput = () => {
      const round = retestFor(all.get(selected));
      if (round) {
        round.drafts ||= {};
        round.drafts[selected] = draft.value;
      } else {
        S.essay.drafts[selected] = draft.value;
      }
      const saved = save(round ? 'hub' : 'essay');
      document.getElementById('save-state').textContent = saved ? '임시저장 완료' : '저장 실패 · JSON 백업 가능';
      document.getElementById('char-count').textContent = Array.from(draft.value).length.toLocaleString('ko-KR') + '자';
    };
    const note = document.getElementById('memo');
    if (note) note.oninput = () => {
      S.hub.notes[selected] = note.value;
      document.getElementById('memo-save').textContent = save('hub') ? '메모 자동저장 완료' : '메모 저장 실패';
    };
    const file = document.getElementById('import-file');
    if (file) file.onchange = async () => {
      const input = file.files[0];
      if (!input) return;
      try {
        if (input.size > 10 * 1024 * 1024) throw Error('10MB 이하의 JSON 파일을 선택해 주세요.');
        importPending = S.validateImport(JSON.parse(await input.text()));
        showDialog(`<h2>가져올 기록 확인</h2><p>${esc(importPending.kind)} · 기본 답안 기록 ${importPending.count}개</p>
          ${notice('같은 문항의 답안은 가져온 기록으로 바뀝니다. 현재 기록을 먼저 백업할 수 있습니다.', '')}
          <div class="dialog-actions">${button('현재 기록 백업', 'export')}${button('취소', 'close')}
          ${button('기록 병합', 'import', 'primary')}</div>`);
      } catch (error) {
        showToast('가져오기 HOLD · ' + error.message);
      } finally {
        file.value = '';
      }
    };
  }

  function openQuestion(id, targetPane = 'detail', preserveFilter = false) {
    const row = all.get(id);
    if (!row) return;
    if (!preserveFilter) {
      filters = filtersFor(row.stage);
      listPage = 0;
    }
    selected = id;
    pane = row.sourceOnly && targetPane === 'detail' ? 'write' : targetPane;
    trace = row.stage === 'first' || locked() ? 0 : 4;
    listOpen = false;
    remember(id, pane);
    if (view === 'study') {
      renderMain();
      document.querySelector('.study-detail')?.scrollIntoView({block: 'start'});
    } else {
      route('study');
    }
  }

  function switchPane(nextPane) {
    if (locked() || all.get(selected)?.stage !== 'essay') return;
    pane = nextPane;
    trace = 4;
    remember(selected, pane);
    renderMain();
    document.querySelector(`[data-pane="${nextPane}"]`)?.focus({preventScroll: true});
  }

  function startExam() {
    if (locked() || !all.has(selected)) return;
    const end = Date.now() + 20 * 60 * 1000;
    S.hub.exam = {end, id: selected};
    S.essay.examEnd = end;
    S.hub.lastId = selected;
    S.hub.lastPane = 'write';
    save('essay');
    save('hub');
    trace = 0;
    pane = 'write';
    modal.close();
    if (view === 'study') renderShell();
    else route('study');
  }

  function endExam() {
    S.essay.examEnd = 0;
    S.hub.exam = null;
    save('essay');
    save('hub');
    if (view === 'study' && all.get(selected)?.stage === 'essay') {
      pane = 'compare';
      trace = 4;
      remember(selected, pane);
    }
    renderShell();
  }

  function startRetest() {
    const ids = reviewRows().map(row => row.key);
    if (!ids.length || activeRetest() || locked()) return;
    const round = {
      id: globalThis.crypto?.randomUUID?.() || String(Date.now()), ids, startedAt: new Date().toISOString(),
      drafts: {}, choices: {}, completed: {},
    };
    S.hub.rounds.push(round);
    S.hub.activeRetest = round.id;
    save('hub');
    openQuestion(ids[0], 'write');
  }

  function stopRetest() {
    const round = activeRetest();
    if (!round || locked()) return;
    round.finishedAt = new Date().toISOString();
    S.hub.activeRetest = null;
    save('hub');
    route('review');
  }

  function action(name) {
    const row = all.get(selected);
    switch (name) {
      case 'continue':
        openQuestion(all.has(S.hub.lastId) ? S.hub.lastId : defaultId, S.hub.lastPane);
        break;
      case 'start-essay':
        openQuestion(defaultId);
        break;
      case 'start-first':
        openQuestion(firstRows[0].key);
        break;
      case 'new57':
        filters = {...filtersFor('essay'), group: 'new'};
        openQuestion(defaultId, 'detail', true);
        break;
      case 'verify':
        route('verify');
        break;
      case 'list-toggle':
        listOpen = !listOpen;
        renderMain();
        break;
      case 'list-prev':
      case 'list-next':
        listPage += name === 'list-prev' ? -1 : 1;
        renderMain();
        break;
      case 'q-prev':
      case 'q-next': {
        const rows = questionRows();
        const index = rows.findIndex(item => item.key === selected) + (name === 'q-prev' ? -1 : 1);
        if (rows[index]) {
          listPage = Math.floor(index / 30);
          openQuestion(rows[index].key, activeRetest() ? 'write' : 'detail', true);
        }
        break;
      }
      case 'source':
        trace = 1;
        renderMain();
        break;
      case 'compressed':
      case 'write':
      case 'compare':
        switchPane(name);
        break;
      case 'outline': {
        const draft = document.getElementById('draft');
        if (!draft) break;
        const outline = /노동법|행정쟁송|민사소송/.test(row.subject)
          ? 'Ⅰ. 문제의 소재\n\nⅡ. 관련 법리·판례\n\nⅢ. 사안의 검토\n\nⅣ. 결론\n'
          : 'Ⅰ. 문제 요구사항\n\nⅡ. 관련 개념·이론\n\nⅢ. 분석 및 적용\n\nⅣ. 결론\n';
        draft.value = (draft.value + (draft.value.trim() ? '\n\n' : '') + outline).slice(0, draft.maxLength);
        draft.dispatchEvent(new Event('input'));
        draft.focus();
        break;
      }
      case 'wrong':
        S.hub.wrong[row.key] = !needsReview(row);
        save('hub');
        renderMain();
        break;
      case 'done': {
        const round = retestFor(row);
        if (round) {
          round.completed ||= {};
          round.completed[row.key] = !round.completed[row.key];
          save('hub');
        } else {
          S.essay.flags[row.key] = !complete(row);
          save('essay');
        }
        renderMain();
        break;
      }
      case 'retest':
        startRetest();
        break;
      case 'retest-stop':
        stopRetest();
        break;
      case 'exam':
        showDialog(`<h2>20분 실전 연습</h2><p>기출 원문을 보며 답안을 작성할 수 있습니다. 정답·학습용 답안·검토 메모는 종료 후 열립니다.</p>
          <div class="dialog-actions">${button('취소', 'close')}${button('20분 시작', 'exam-start', 'primary')}</div>`);
        break;
      case 'exam-start':
        startExam();
        break;
      case 'exam-stop':
        showDialog(`<h2>실전 연습을 종료할까요?</h2><p>저장한 답안을 비교·복습할 수 있습니다.</p>
          <div class="dialog-actions">${button('계속 작성', 'close')}${button('종료하고 복습', 'exam-end', 'primary')}</div>`);
        break;
      case 'exam-end':
        modal.close();
        endExam();
        break;
      case 'export':
        download(S.exportData(), 'nomusa_learning_backup.json');
        break;
      case 'export-essay':
        download({schema: 'nomusa-rc27-essay-records/1', saved: {...S.essay, examEnd: 0}}, 'nomusa_2cha_backup.json');
        break;
      case 'export-first': {
        const {session, ...progress} = S.first;
        download({schema: 'nomusa-quiz-progress-rc32', exportedAt: new Date().toISOString(), sourceQuestions: Q.length, progress}, 'nomusa_1cha_backup.json');
        break;
      }
      case 'manual-note': {
        showDialog(`<h2>수동 점검 메모</h2>
          <form id="manual-note-form"><label class="field">기기·브라우저<input name="env" required maxlength="100" placeholder="예 Android Chrome 390px"></label>
            <label class="field">확인 결과<textarea name="note" required maxlength="1000" rows="4"></textarea></label>
            <div class="dialog-actions">${button('취소', 'close')}<button class="button primary" type="submit">저장</button></div></form>`);
        document.getElementById('manual-note-form').onsubmit = event => {
          event.preventDefault();
          const fields = new FormData(event.currentTarget);
          const note = fields.get('note').trim();
          const env = fields.get('env').trim();
          if (!note || !env) return;
          S.hub.logs.push({name: '수동 점검', note, env, date: new Date().toLocaleDateString('ko-KR', {timeZone: 'Asia/Seoul'})});
          save('hub');
          modal.close();
          renderMain();
        };
        break;
      }
      case 'import':
        try {
          if (!importPending) break;
          S.applyImport(importPending);
          if (all.has(S.hub.lastId)) selected = S.hub.lastId;
          pane = S.hub.lastPane;
          importPending = null;
          modal.close();
          renderMain();
          showToast('학습 기록 병합 완료');
        } catch (error) {
          showToast(error.message);
        }
        break;
      case 'close':
        importPending = null;
        modal.close();
        break;
    }
  }

  function onClick(event) {
    const control = event.target.closest('button, [data-nav]');
    if (!control || control.disabled) return;
    const {nav: page, action: name, year, stage, question, trace: source, pane: step, choice: choiceNumber} = control.dataset;
    if (page) { event.preventDefault(); route(page); }
    if (name) action(name);
    if (year) {
      filters = {...filtersFor('essay'), year};
      listPage = 0;
      filterOpen = true;
      route('study');
    }
    if (stage) {
      filters = filtersFor(stage);
      trace = 0;
      listPage = 0;
      renderMain();
    }
    if (question) openQuestion(question, activeRetest() ? 'write' : 'detail', view === 'study');
    if (source !== undefined && (!locked() || Number(source) <= 2)) {
      trace = Number(source);
      renderMain();
      document.querySelector(`[data-trace="${source}"]`)?.focus({preventScroll: true});
    }
    if (step) switchPane(step);
    if (choiceNumber) {
      const round = retestFor(all.get(selected));
      if (round) {
        round.choices ||= {};
        round.choices[selected] = Number(choiceNumber);
      } else {
        if (S.hub.choices[selected] !== Number(choiceNumber) && S.hub.wrong[selected] === false) delete S.hub.wrong[selected];
        S.hub.choices[selected] = Number(choiceNumber);
      }
      remember(selected, pane);
      renderMain();
    }
  }

  app.addEventListener('click', onClick);
  modal.addEventListener('click', onClick);
  app.addEventListener('change', event => {
    const key = event.target.dataset.selfcheck;
    if (key !== undefined && !locked()) {
      S.essay.checks[selected] ||= {};
      S.essay.checks[selected][key] = event.target.checked;
      save('essay');
    }
  });
  window.addEventListener('hashchange', () => {
    const page = location.hash.slice(1);
    if (Object.hasOwn(title, page) && page !== view) route(page, false);
  });
  window.addEventListener('pageshow', () => {
    if (view === 'verify') renderMain();
  });
  window.addEventListener('storage', event => {
    if (event.key === window.HUB_QA.resultKey && view === 'verify') renderMain();
  });
  setInterval(() => {
    const end = examEnd();
    if (!end) return;
    if (end <= Date.now()) {
      endExam();
      showToast('20분 실전 연습 종료');
      return;
    }
    const clock = document.getElementById('exam-clock');
    const seconds = Math.ceil((end - Date.now()) / 1000);
    if (clock) clock.textContent = String(Math.floor(seconds / 60)).padStart(2, '0') + ':' + String(seconds % 60).padStart(2, '0');
  }, 1000);

  renderShell();
  fetch('evidence/hub-browser-v2.json', {cache: 'no-store'}).then(async response => {
    if (response.ok) localReport = await response.json();
    if (view === 'verify') renderMain();
  }).catch(() => {});
})();

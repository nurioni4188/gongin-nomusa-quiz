(() => {
  'use strict';

  const mode = new URLSearchParams(location.search || '').get('qa');
  const prefix = /^[a-zA-Z0-9-]{1,64}$/.test(mode || '') ? `nomusa_qa_${mode}:` : '';
  const keys = {
    essay: prefix + 'nomusa_rc27_v103_essay_records_v1',
    first: prefix + 'nomu1-progress-v2',
    hub: prefix + 'nomusa_preview_hub_v1',
  };
  const essayIds = new Set(window.N27_CATALOG.items.map(row => row.id));
  const firstIds = new Set(window.QDATA.map(row => row.k));
  const allIds = new Set([...essayIds, ...firstIds]);
  const validCardFields = ['author', 'title', 'year', 'locator', 'note'];
  const essayMaps = ['drafts', 'flags', 'bookmarks', 'checks', 'memoryCards',
    'sourceChecks', 'researchCards', 'writingPlans'];
  const hubMaps = ['notes', 'wrong', 'completed', 'choices'];
  const emptyEssay = () => ({...Object.fromEntries(essayMaps.map(field => [field, {}])), examEnd: 0});
  const emptyFirst = () => ({att: {}, star: {}, memo: {}, prefs: {}, session: null});
  const emptyHub = () => ({
    notes: {}, wrong: {}, completed: {}, choices: {}, lastId: null, lastPane: 'detail',
    rounds: [], activeRetest: null, logs: [], human: {}, exam: null,
  });
  const defaults = {essay: emptyEssay, first: emptyFirst, hub: emptyHub};
  const data = {};
  const snapshots = {};
  const corrupt = new Set();
  const object = value => value !== null && typeof value === 'object' && !Array.isArray(value);
  const validKey = key => !['__proto__', 'constructor', 'prototype'].includes(key);
  const equal = (left, right) => JSON.stringify(left) === JSON.stringify(right);
  const clone = value => JSON.parse(JSON.stringify(value));
  let storageError = '';

  function read(name, raw = localStorage.getItem(keys[name])) {
    const fallback = defaults[name]();
    if (raw === null) return fallback;
    const value = JSON.parse(raw);
    if (!object(value)) throw Error('저장 기록의 형식을 확인해 주세요.');
    for (const [key, sample] of Object.entries(fallback)) {
      if (!Object.hasOwn(value, key)) continue;
      if ((object(sample) && !object(value[key])) || (Array.isArray(sample) && !Array.isArray(value[key]))) {
        throw Error('저장 기록의 형식을 확인해 주세요.');
      }
    }
    return {...fallback, ...value};
  }

  for (const name of Object.keys(keys)) {
    try {
      data[name] = read(name);
    } catch {
      corrupt.add(name);
      data[name] = defaults[name]();
      storageError = '저장된 기록을 읽지 못했습니다. 기존 값을 보호하고 있습니다.';
    }
    snapshots[name] = clone(data[name]);
  }

  // Merge edits onto the latest record so other tabs' unrelated edits survive.
  function rebase(before, edited, latest) {
    if (equal(before, edited)) return latest;
    if (Array.isArray(edited) && Array.isArray(latest) && edited.every(row => object(row) && row.id)) {
      const base = new Map((Array.isArray(before) ? before : []).map(row => [row.id, row]));
      const result = new Map(latest.map(row => [row.id, row]));
      for (const row of edited) result.set(row.id, rebase(base.get(row.id), row, result.get(row.id)));
      return [...result.values()].filter(Boolean);
    }
    if (!object(edited) || !object(latest) || (before !== undefined && !object(before))) return edited;
    const base = object(before) ? before : {};
    const result = {...latest};
    for (const key of new Set([...Object.keys(base), ...Object.keys(edited)])) {
      if (!validKey(key)) continue;
      if (!Object.hasOwn(edited, key)) {
        delete result[key];
      } else {
        const next = rebase(base[key], edited[key], latest[key]);
        if (next !== undefined) result[key] = next;
      }
    }
    return result;
  }

  function save(name) {
    if (corrupt.has(name)) return false;
    try {
      const merged = rebase(snapshots[name], data[name], read(name));
      localStorage.setItem(keys[name], JSON.stringify(merged));
      data[name] = merged;
      snapshots[name] = clone(merged);
      if (!corrupt.size) storageError = '';
      return true;
    } catch {
      storageError = '기록을 저장하지 못했습니다. 현재 입력을 JSON으로 내보낼 수 있습니다.';
      return false;
    }
  }

  function cleanMap(raw, ids, cleanValue) {
    if (!object(raw)) throw Error('기록 항목의 구조를 확인해 주세요.');
    const entries = Object.entries(raw).map(([id, value]) => {
      if (!validKey(id) || !ids.has(id)) throw Error(`알 수 없는 문항 ID ${id.slice(0, 80)}`);
      return [id, cleanValue(value)];
    });
    return Object.fromEntries(entries);
  }

  function textLimit(value, max = 299999) {
    if (typeof value !== 'string' || value.length > max) throw Error('기록의 텍스트 길이 또는 형식을 확인해 주세요.');
    return value;
  }
  function boolean(value) {
    if (typeof value !== 'boolean' && value !== 0 && value !== 1) throw Error('체크 기록의 형식을 확인해 주세요.');
    return Boolean(value);
  }
  function choice(value) {
    if (!Number.isInteger(value) || value < 1 || value > 5) throw Error('선택 번호를 확인해 주세요.');
    return value;
  }
  function checks(value) {
    if (!object(value)) throw Error('체크리스트 형식을 확인해 주세요.');
    const entries = Object.entries(value).map(([key, checked]) => {
      if (!validKey(key) || !/^[\w가-힣-]{1,60}$/.test(key) || typeof checked !== 'boolean') {
        throw Error('체크리스트 항목을 확인해 주세요.');
      }
      return [key, checked];
    });
    return Object.fromEntries(entries);
  }

  function memoryCards(raw) {
    if (!object(raw)) throw Error('암기 카드 구조를 확인해 주세요.');
    return Object.fromEntries(Object.entries(raw).map(([key, card]) => {
      const divider = key.lastIndexOf('::');
      const id = key.slice(0, divider);
      const part = key.slice(divider + 2);
      if (divider < 0 || !essayIds.has(id) || !/^(\d|1\d|2[0-5])$/.test(part) || !object(card)) {
        throw Error('암기 카드의 문항 ID를 확인해 주세요.');
      }
      const out = {
        words: textLimit(card.words ?? '', 1200),
        story: textLimit(card.story ?? '', 900),
        review: ['known', 'retry'].includes(card.review) ? card.review : '',
      };
      for (const field of ['recallAttempts', 'recallHits', 'lastAccuracy']) {
        const value = card[field];
        if (Number.isInteger(value) && value >= 0 && value <= (field === 'lastAccuracy' ? 100 : 100000)) out[field] = value;
      }
      if (typeof card.lastRecallAt === 'string' && Number.isFinite(Date.parse(card.lastRecallAt))) out.lastRecallAt = card.lastRecallAt;
      return [key, out];
    }));
  }

  function researchCard(value) {
    if (!object(value)) throw Error('문헌 검토 기록을 확인해 주세요.');
    return Object.fromEntries(validCardFields
      .filter(field => Object.hasOwn(value, field))
      .map(field => [field, textLimit(value[field], field === 'note' ? 700 : 220)]));
  }

  function writingPlan(value) {
    if (!object(value)) throw Error('답안 분량 설정을 확인해 주세요.');
    const out = {};
    if (Number.isInteger(value.pages) && value.pages >= 1 && value.pages <= 12) out.pages = value.pages;
    if ([300, 400, 500, 600, 700, 800].includes(value.perPage)) out.perPage = value.perPage;
    return out;
  }

  function cleanEssay(value) {
    if (!object(value)) throw Error('2차 기록 구조를 확인해 주세요.');
    const out = emptyEssay();
    const validators = {drafts: textLimit, flags: boolean, bookmarks: boolean, checks,
      sourceChecks: boolean, researchCards: researchCard, writingPlans: writingPlan};
    for (const [field, validate] of Object.entries(validators)) {
      out[field] = cleanMap(value[field] ?? {}, essayIds, validate);
    }
    out.memoryCards = memoryCards(value.memoryCards ?? {});
    return out;
  }

  function firstAttempt(value) {
    if (!object(value) || !Number.isSafeInteger(value.n) || value.n < 1 || value.n > 1000000 ||
        !Number.isSafeInteger(value.w) || value.w < 0 || value.w > value.n || typeof value.ok !== 'boolean') {
      throw Error('1차 풀이 이력을 확인해 주세요.');
    }
    return {n: value.n, w: value.w, last: choice(value.last), ok: value.ok, t: Number.isFinite(value.t) ? value.t : 0};
  }

  function firstPreferences(value) {
    if (!object(value)) return {};
    const out = {};
    if (['light', 'dark'].includes(value.theme)) out.theme = value.theme;
    if (typeof value.invert === 'boolean') out.invert = value.invert;
    if (['img', 'text'].includes(value.view)) out.view = value.view;
    if (object(value.setup)) {
      const setup = value.setup;
      const years = [...new Set(window.QDATA.map(row => row.y))];
      const subjects = [...new Set(window.QDATA.map(row => row.s))];
      out.setup = {
        years: Array.isArray(setup.years) ? setup.years.filter(year => years.includes(year)) : [],
        subs: Array.isArray(setup.subs) ? setup.subs.filter(subject => subjects.includes(subject)) : [],
        scope: ['all', 'new', 'wrong', 'everwrong', 'star'].includes(setup.scope) ? setup.scope : 'all',
        order: setup.order === 'rand' ? 'rand' : 'seq',
        count: [0, 10, 20, 40].includes(setup.count) ? setup.count : 0,
        mode: setup.mode === 'exam' ? 'exam' : 'practice',
      };
      if (!out.setup.years.length) out.setup.years = [Math.max(...years)];
      if (!out.setup.subs.length) out.setup.subs = [subjects[0]];
    }
    return out;
  }

  function cleanFirst(value) {
    if (!object(value)) throw Error('1차 기록 구조를 확인해 주세요.');
    return {
      ...emptyFirst(),
      att: cleanMap(value.att, firstIds, firstAttempt),
      star: cleanMap(value.star ?? {}, firstIds, starred => boolean(starred) ? 1 : 0),
      memo: cleanMap(value.memo ?? {}, firstIds, value => textLimit(value, 5000)),
      prefs: firstPreferences(value.prefs),
    };
  }

  function cleanRounds(value) {
    if (!Array.isArray(value) || value.length > 1000) throw Error('재시험 회차 구조를 확인해 주세요.');
    return value.map(round => {
      if (!object(round) || !Array.isArray(round.ids) || !round.ids.length ||
          round.ids.some(id => !allIds.has(id)) || !Number.isFinite(Date.parse(round.startedAt))) {
        throw Error('재시험 회차의 문항 ID 또는 날짜를 확인해 주세요.');
      }
      const ids = [...new Set(round.ids)];
      const allowed = new Set(ids);
      const clean = {
        id: typeof round.id === 'string' && round.id.length <= 100 ? round.id : round.startedAt,
        startedAt: round.startedAt,
        ids,
        drafts: cleanMap(round.drafts ?? {}, new Set(ids.filter(id => essayIds.has(id))), textLimit),
        choices: cleanMap(round.choices ?? {}, new Set(ids.filter(id => firstIds.has(id))), choice),
        completed: cleanMap(round.completed ?? {}, allowed, boolean),
      };
      if (round.finishedAt && Number.isFinite(Date.parse(round.finishedAt))) clean.finishedAt = round.finishedAt;
      return clean;
    });
  }

  function validateImport(value) {
    if (!object(value)) throw Error('JSON 객체를 선택해 주세요.');
    if (value.schema === 'nomusa-rc27-essay-records/1') {
      const essay = cleanEssay(value.saved);
      return {essay, kind: '기존 2차 백업', count: Object.keys(essay.drafts).length};
    }
    if (value.schema === 'nomusa-quiz-progress-rc32') {
      const first = cleanFirst(value.progress);
      return {first, kind: '기존 1차 백업', count: Object.keys(first.att).length};
    }
    if (value.schema !== 'nomusa-preview-hub/1' || !object(value.hub)) {
      throw Error('기존 1차·2차 또는 학습 허브 JSON을 선택해 주세요.');
    }
    const essay = cleanEssay(value.essay);
    const first = cleanFirst(value.first);
    const hub = emptyHub();
    const validators = {notes: textLimit, wrong: boolean, completed: boolean, choices: choice};
    for (const field of hubMaps) {
      hub[field] = cleanMap(value.hub[field] ?? {}, field === 'choices' ? firstIds : allIds, validators[field]);
    }
    if (value.hub.lastId != null && !allIds.has(value.hub.lastId)) throw Error('최근 학습 문항 ID를 확인해 주세요.');
    hub.lastId = value.hub.lastId || null;
    if (['detail', 'compressed', 'write', 'compare'].includes(value.hub.lastPane)) hub.lastPane = value.hub.lastPane;
    hub.rounds = cleanRounds(value.hub.rounds ?? []);
    return {essay, first, hub, kind: '학습 허브 백업',
      count: Object.keys(essay.drafts).length + Object.keys(first.att).length + Object.keys(hub.choices).length};
  }

  function applyImport(input) {
    const names = Object.keys(keys).filter(name => input[name]);
    const stored = {};
    const merged = {};
    const written = [];
    try {
      for (const name of names) {
        if (corrupt.has(name)) throw Error('손상된 기존 기록');
        stored[name] = localStorage.getItem(keys[name]);
        merged[name] = rebase(snapshots[name], data[name], read(name, stored[name]));
      }
      if (merged.essay) {
        for (const field of essayMaps.filter(field => field !== 'checks')) {
          merged.essay[field] = {...merged.essay[field], ...input.essay[field]};
        }
        for (const [id, checked] of Object.entries(input.essay.checks)) {
          merged.essay.checks[id] = {...merged.essay.checks[id], ...checked};
        }
      }
      if (merged.first) {
        for (const field of ['att', 'star', 'memo', 'prefs']) merged.first[field] = {...merged.first[field], ...input.first[field]};
      }
      if (merged.hub) {
        for (const field of hubMaps) merged.hub[field] = {...merged.hub[field], ...input.hub[field]};
        if (input.hub.lastId) {
          merged.hub.lastId = input.hub.lastId;
          merged.hub.lastPane = input.hub.lastPane;
        }
        const rounds = new Map(merged.hub.rounds.map(round => [round.id || round.startedAt, round]));
        for (const round of input.hub.rounds) {
          if (round.id !== merged.hub.activeRetest) rounds.set(round.id, round);
        }
        merged.hub.rounds = [...rounds.values()];
      }
      for (const name of names) {
        localStorage.setItem(keys[name], JSON.stringify(merged[name]));
        written.push(name);
      }
    } catch {
      try {
        for (const name of written.reverse()) {
          if (stored[name] === null) localStorage.removeItem(keys[name]);
          else localStorage.setItem(keys[name], stored[name]);
        }
      } catch {
        throw Error('가져오기 중 저장과 복원에 실패했습니다. 현재 기록을 백업해 주세요.');
      }
      throw Error('기존 기록을 보호하기 위해 가져오기를 취소했습니다.');
    }
    for (const name of names) {
      data[name] = merged[name];
      snapshots[name] = clone(merged[name]);
    }
  }

  function exportData() {
    return {
      schema: 'nomusa-preview-hub/1', exportedAt: new Date().toISOString(), origin: location.origin,
      essay: {...data.essay, examEnd: 0}, first: {...data.first, session: null},
      hub: {...data.hub, exam: null, activeRetest: null},
    };
  }

  window.HubState = {
    keys, qa: Boolean(prefix), save, validateImport, applyImport, exportData,
    get essay() { return data.essay; },
    get first() { return data.first; },
    get hub() { return data.hub; },
    get storageError() { return storageError; },
  };
})();

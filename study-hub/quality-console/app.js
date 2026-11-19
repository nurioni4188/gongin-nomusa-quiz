(() => {
  'use strict';
  const REPO = 'nurioni4188/gongin-nomusa-quiz';
  const BRANCH = 'review/nomusa-auto-v1-20year-gate-20261115';
  const STORAGE_KEY = 'nomusa_quality_console_review_v1';
  const SCHEMA = 'NOMUSA_QUALITY_CONSOLE_LOCAL_REVIEW/1';
  const STATES = ['원문 대조 필요','작성 중','검토 중','내용확정','독립심사 대기','승인 완료'];
  const SOURCES = {
    first103: '/review/NOMUSA_FIRST_V43_103_SECOND_PASS_515_CHOICES_AND_LAW_QA_20261118.json',
    remaining686: '/review/NOMUSA_FIRST_V54_686_UNIFIED_PRIMARY_SOURCE_LEDGER_20261118.json',
    essay328: '/review/NOMUSA_V23_VALIDATION_LEDGER.json',
    coverage: '/review/NOMUSA_FIRST_V77_2008_2026_3070_RECONCILIATION_SUMMARY_20261119.json',
    audit: '/review/NOMUSA_FIRST_V76_19_YEAR_AUDIT_SUMMARY_20261119.json',
    risk: '/review/NOMUSA_FIRST_V71_686_WORKSPACE_SUMMARY_20261119.json'
  };
  const E = id => document.getElementById(id);
  const esc = v => String(v == null ? '' : v).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const clean = v => String(v == null ? '' : v).trim();
  const cap = (v, n=1800) => clean(v).slice(0,n);
  const jsonObj = x => x && typeof x === 'object' && !Array.isArray(x);
  const isSafeKey = x => !['__proto__','prototype','constructor'].includes(x);
  const link = (url,label) => {
    const u = clean(url);
    if (!/^https:\/\/[a-z0-9.-]+\//i.test(u) && !/^\/[a-z0-9/_?=&#%.-]+$/i.test(u)) return '';
    return '<a href="' + esc(u) + '" target="_blank" rel="noopener noreferrer">' + esc(label) + '</a>';
  };
  const gh = path => 'https://github.com/' + REPO + '/blob/' + BRANCH + '/' + path.split('/').map(encodeURIComponent).join('/');
  const fmt = v => Number(v || 0).toLocaleString('ko-KR');
  const bucket = new Map();
  const reports = {};
  const failures = [];
  let all = [], filtered = [], view = 'all', page = 0, current = null, detailTab = 'source', sourceRecord = null;
  const pageSize = 35;
  let record = {schema: SCHEMA, version: 1, updatedAt: null, items: {}, log: []};
  let blockedStorage = false;
  function toast(message) {
    E('toast').textContent = String(message);
    window.clearTimeout(toast.t);
    toast.t = window.setTimeout(() => E('toast').textContent = '', 4000);
  }
  function readLocal() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw == null) return;
      const obj = JSON.parse(raw);
      if (!jsonObj(obj) || obj.schema !== SCHEMA || !jsonObj(obj.items)) throw Error('구조 불일치');
      if (Object.keys(obj.items).some(k => !isSafeKey(k))) throw Error('금지된 키');
      record = {schema:SCHEMA, version:1, updatedAt:obj.updatedAt || null, items:obj.items, log:Array.isArray(obj.log)?obj.log.slice(-250):[]};
    } catch (err) {
      blockedStorage = true;
      toast('저장 데이터 형식 오류: 원본 보호를 위해 자동저장을 중지했습니다.');
    }
  }
  function persist() {
    if (blockedStorage) return false;
    try {
      record.updatedAt = new Date().toISOString();
      localStorage.setItem(STORAGE_KEY, JSON.stringify(record));
      return true;
    } catch {
      toast('브라우저 저장 실패. JSON 내보내기로 내용을 보관해 주세요.');
      return false;
    }
  }
  function itemData(id) {
    if (!jsonObj(record.items[id])) record.items[id] = {};
    return record.items[id];
  }
  function auditLog(id, action) {
    record.log.push({id, action, at:new Date().toISOString()});
    record.log = record.log.slice(-250);
    persist();
  }
  function kindSubject(id) {
    const parts = id.split('-');
    const code = parts[3] || '';
    const m = {
      management:'경영학개론', economics:'경제학원론', labor1:'노동법(1)',labor2:'노동법(2)',
      social:'사회보험법', civil:'민법', hrm:'인사노무관리론', organization:'경영조직론',
      administrative:'행정쟁송법','labor-economics':'노동경제학'
    };
    if (m[code]) return m[code];
    return /(social|insurance)/.test(id)?'사회보험법':/(econom)/.test(id)?'경제학원론':/(labor)/.test(id)?'노동법':'원본 과목 확인 필요';
  }
  function asFirst(r, label) {
    return {
      id:String(r.k || r.id || r.key || ''), stage:'first', kind:label,
      year:Number(r.y || r.year || 0), subject:clean(r.s || r.subject || kindSubject(String(r.k || r.id || ''))),
      number:r.n || r.questionNumber || null, form:r.form || 'A',
      points:null, page:r.pg || r.pdfPage || r.originalPage || null,
      q:clean(r.q || r.question || r.sourceText || ''), options:Array.isArray(r.o)?r.o:[],
      answer:Array.isArray(r.a)?r.a:(r.officialAFormAnswer != null?[r.officialAFormAnswer]:[]),
      evidence:r.sourceUrl || r.answerSourceUrl || r.originalRecord || '',
      source:r, title:clean(r.topic || r.q || r.question || '1차 기출문항')
    };
  }
  function add(r, force) {
    if (!r || !r.id) return;
    if (bucket.has(r.id) && !force) return;
    if (bucket.has(r.id)) {
      const old=bucket.get(r.id);
      r.q=r.q || old.q;
      r.options=r.options.length ? r.options : old.options;
      r.answer=r.answer.length ? r.answer : old.answer;
      r.page=r.page || old.page;
      r.evidence=r.evidence || old.evidence;
    }
    bucket.set(r.id,r);
  }
  function prepareBaseline() {
    for (const row of (window.QDATA || [])) add(asFirst(row,'existing'));
    for (const key of ['NOMUSA_FIRST_2008','NOMUSA_FIRST_2009','NOMUSA_FIRST_2010']) {
      const val=window[key];
      for (const row of (Array.isArray(val)?val:Array.isArray(val?.items)?val.items:[])) add(asFirst(row,'existing'));
    }
  }
  async function addPacked() {
    const raw = window.NOMUSA_FIRST_BATCH_PACK;
    if (!raw || !('DecompressionStream' in window)) {failures.push('과거 압축 문제은행 로드 미지원');return;}
    try {
      const buf = Uint8Array.from(atob(raw),c => c.charCodeAt(0));
      const stream = new Blob([buf]).stream().pipeThrough(new DecompressionStream('gzip'));
      const parsed = JSON.parse(await new Response(stream).text());
      const items = Array.isArray(parsed)?parsed:(parsed.items || parsed.rows || []);
      for (const row of items) add(asFirst(row,'existing'));
    } catch {failures.push('2011~2019 과거 압축 문제은행 로드 실패');}
  }
  async function loadFile(name,url) {
    try {
      const res=await fetch(url,{cache:'no-store'});
      if (!res.ok) throw Error('HTTP '+res.status);
      const parsed=await res.json();
      reports[name]=parsed;
      return parsed;
    } catch(err) {
      failures.push(name+' 근거 파일 접근 미확인 ('+err.message+')');
      return null;
    }
  }
  function addFrom103(data) {
    if (!Array.isArray(data?.rows)) return;
    for (const src of data.rows) {
      const obj=asFirst({...src,k:src.id,y:src.year,a:[src.officialAFormAnswer]},'first103');
      obj.number=Number(String(obj.id).match(/-(\d+)$/)?.[1] || 0);
      obj.evidence=src.originalRecord;
      obj.title='원본·5선택지·상세해설 검토';
      obj.source=src;
      add(obj,true);
    }
  }
  function addFrom686(data) {
    const items = Array.isArray(data)?data:[data?.rows,data?.items,data?.questions,data?.records,data?.ledger]
      .find(Array.isArray);
    if (!items) {failures.push('686개 원장 세부 ID 해석 미확인: 연도별 검토묶음만 표시');return;}
    for (const src of items) {
      const id=src.id || src.questionId || src.key || src.k;
      if (!id) continue;
      const row=asFirst({...src,k:id,y:src.year || src.y,s:src.subject || src.s},'first686');
      row.title=cap(src.title || src.question || src.sourceText || '원본 대조·정답·해설 검증',90);
      row.evidence=src.originalRecord || src.sourceFile || src.evidenceFile || src.qnetSourceUrl || row.evidence;
      row.source=src;
      add(row,true);
    }
  }
  function addEssay(data) {
    const catalog=new Map((window.N27_CATALOG?.items || []).map(r=>[r.id,r]));
    for (const src of (data?.rows || [])) {
      const c=catalog.get(src.id) || {};
      const obj={
        id:src.id,stage:'second',kind:'second',year:src.year,subject:src.subject || c.subject || '과목 확인 필요',
        number:src.questionNumber || null,points:src.points ?? c.points ?? null,page:c.pdfPage || c.sourcePage || null,
        form:String(src.year-1991)+'회',q:clean(c.sourceText || ''),options:[],answer:[],
        title:clean(c.topic || c.title || '2차 기출 모범답안 검토'),
        evidence:src.source?.qnetPostUrl || '', source:src,catalog:c
      };
      add(obj,true);
    }
  }
  function addCoverageGroups() {
    const gaps=(reports.coverage?.yearly || []).filter(y => Number(y.V74OriginalSourceReviewDraft) > 0);
    if ((reports.remaining686?.rows || []).length >= 680) return;
    for (const r of gaps) {
      const count=Number(r.V74OriginalSourceReviewDraft);
      const id='review-group-'+r.year;
      add({id,stage:'first',kind:'first686',year:r.year,subject:'원본 미편입 '+count+'문항',
        number:null,form:'A',points:null,page:null,q:'연도별 원본 근거 장부를 확인하고 문항 ID와 원문·선택지를 1대1 연결해야 합니다.',
        options:[],answer:[],title:r.year+'년 미편입 '+count+'문항 검토묶음',
        evidence:'review/NOMUSA_FIRST_V54_686_UNIFIED_PRIMARY_SOURCE_LEDGER_20261118.json',source:r,group:true,count},false);
    }
  }
  function addSocial() {
    for (const r of bucket.values()) {
      if (r.stage==='first' && r.year===2026 && /사회보험법/.test(r.subject)) r.social2026=true;
    }
  }
  function getStatus(r) {
    const explicit=record.items[r.id]?.status;
    return STATES.includes(explicit)?explicit:(r.kind==='first103'||r.kind==='second'?'검토 중':'원문 대조 필요');
  }
  function holdReason(r) {
    const manual=clean(record.items[r.id]?.blocking);
    if (manual) return manual;
    if (r.kind==='first103') return /사회보험|민법|노동법/.test(r.subject)?'당시 법령·판례·독립교열':'독립 원문·학술 교열';
    if (r.kind==='second') return '독립 전문가 서명·원전 확인';
    if (r.social2026) return '해설·시험 당시 법령 검토';
    return '원문·정답·선택지 확인';
  }
  const sheet = r => r.points===50?'8~10장':r.points===25?'4장':r.points===15?'3장':r.points>0&&r.points<=10?'2장':r.points?'소문항 배점 비례':'배점 확인 필요';
  const related = r => {
    if (/경제|노동경제/.test(r.subject)) return ['수식','함수','그래프','계산','검산','수치 원본'];
    if (/경영|인사노무/.test(r.subject)) return ['학자','저서','논문','연도','비교표','학술원전'];
    return ['시험 당시 조문','부칙','판례','사안포섭','효력발생일','원문'];
  };
  const asPage = p => Array.isArray(p)?p.join(', '):(p==null?'미확인':String(p));
  function metrics() {
    const cards=[
      ['3,070','1차 19개년 A형 ID','V77 전체 ID 일치 · 내용승인 별도'],
      ['103','집중검토 문항','515개 선택지 설명 초안'],
      ['25','시험일 법률문항','조문·부칙·판례 최종 HOLD'],
      ['686','추가 원문 대조 문항','정답·해설 승인 0'],
      ['328','2차 내용 고도화','독립 전문가 승인 0']
    ];
    E('metrics').innerHTML=cards.map(c=>'<div class="metric"><div class="num">'+c[0]+'</div><div class="lab">'+c[1]+'</div><div class="sub">'+c[2]+'</div></div>').join('');
  }
  const titles = {
    all:'전체 문항·작업 대장', first103:'1차 집중검토 103문항', first686:'1차 추가 원문대조 686문항',
    social2026:'2026년 사회보험법 해설 점검', second:'2차 모범답안 328문항',
    coverage:'2008~2026년 누락·원전 연결 현황', evidence:'검증 증거·Preview 관문'
  };
  function matchesView(r) {
    if(view==='first103')return r.kind==='first103';
    if(view==='first686')return r.kind==='first686';
    if(view==='social2026')return Boolean(r.social2026);
    if(view==='second')return r.kind==='second';
    return true;
  }
  function filter() {
    if(view==='coverage'){renderCoverage();return;}
    if(view==='evidence'){renderEvidence();return;}
    const q=clean(E('q').value).toLowerCase();
    const y=E('year').value, s=E('subject').value, st=E('status').value, round=clean(E('round').value).toLowerCase();
    filtered=all.filter(r=>matchesView(r)&&(!y||String(r.year)===y)&&(!s||r.subject===s)&&(!st||getStatus(r)===st)
      &&(!round||[r.form,String(r.year),String(r.year-1991),'제'+(r.year-1991)+'회'].some(v=>String(v||'').toLowerCase().includes(round)))
      &&(!q||[r.id,r.title,r.subject,r.q,holdReason(r),record.items[r.id]?.reviewNote].some(v=>String(v||'').toLowerCase().includes(q))));
    const pages=Math.max(1,Math.ceil(filtered.length/pageSize));page=Math.max(0,Math.min(page,pages-1));
    E('tableCount').textContent=fmt(filtered.length)+'개 문항·작업 조회 (실제 로드 '+fmt(all.length)+'개)';
    E('pageText').textContent=(page+1)+' / '+pages+'페이지';
    E('prevBtn').disabled=page===0;E('nextBtn').disabled=page>=pages-1;
    const rows=filtered.slice(page*pageSize,(page+1)*pageSize);
    E('rows').innerHTML=rows.length?rows.map(r=>{
      const status=getStatus(r);
      const tags=r.group?'<span class="tag gray">연도 묶음</span>':r.kind==='first103'?'<span class="tag blue">103 내용초안</span>':'';
      return '<tr><td><button type="button" class="item-link" data-open="'+esc(r.id)+'">'+esc(cap(r.title,48) || r.id)+'</button><span class="micro">'+esc(r.id)+'</span>'+tags+'</td>'
        +'<td>'+esc(r.year)+'년<br>'+esc(r.subject)+'</td><td>'+esc(r.points? r.points+'점':(r.form||'A형'))+'<br><span class="micro">'+esc(asPage(r.page))+'쪽</span></td>'
        +'<td><span class="tag '+(status==='승인 완료'?'green':status==='검토 중'?'blue':'hold')+'">'+esc(status)+'</span></td>'
        +'<td class="muted">'+esc(cap(holdReason(r),65))+'</td></tr>';
    }).join(''):'<tr><td class="empty" colspan="5">조건에 맞는 작업이 없습니다. 필터를 변경해 주세요.</td></tr>';
  }
  function fillSelect() {
    const years=[...new Set(all.map(r=>r.year).filter(Boolean))].sort((a,b)=>b-a);
    const subjects=[...new Set(all.map(r=>r.subject).filter(Boolean))].sort((a,b)=>a.localeCompare(b,'ko'));
    E('year').innerHTML='<option value="">전체 연도</option>'+years.map(y=>'<option value="'+y+'">'+y+'년</option>').join('');
    E('subject').innerHTML='<option value="">전체 과목</option>'+subjects.map(s=>'<option value="'+esc(s)+'">'+esc(s)+'</option>').join('');
    E('status').innerHTML='<option value="">전체 상태</option>'+STATES.map(s=>'<option value="'+esc(s)+'">'+esc(s)+'</option>').join('');
  }
  function switchView(next) {
    view=next;page=0;E('detail').hidden=true;
    for(const b of E('views').querySelectorAll('button'))b.classList.toggle('active',b.dataset.view===next);
    E('viewTitle').textContent=titles[next];
    E('viewSubtitle').textContent=next==='evidence'?'실행 여부가 확인되는 기술검증과 내용승인을 분리':next==='coverage'?'연도별 현황은 ID 정리 상태이며 최종 내용승인 통계가 아닙니다.':'모든 입력은 검토 전용이며 기존 채점·정답 데이터에 적용되지 않습니다.';
    E('filters').hidden=['coverage','evidence'].includes(next);
    E('nextBtn').hidden=E('prevBtn').hidden=['coverage','evidence'].includes(next);
    filter();
  }
  function renderCoverage() {
    const rows=reports.coverage?.yearly || [];
    E('tableCount').textContent=rows.length+'개 연도 확인 · 연도별 미편입 원본 관리';
    E('pageText').textContent='';
    E('rows').innerHTML=rows.length?rows.map(r=>'<tr><td><strong>'+r.year+'년</strong><span class="micro">A형 목표 '+fmt(r.expectedAFormItemIDs)+'</span></td>'
      +'<td>원전 ID '+fmt(r.registeredUniqueIDs)+'</td><td>문제은행 '+fmt(r.existingQDATAAndLegacyBank)+'</td>'
      +'<td><span class="tag hold">내용승인 HOLD</span></td><td>103 초안 '+fmt(r.V43OriginalFirstPassDraft)+' · 686 원문검토 '+fmt(r.V74OriginalSourceReviewDraft)+'</td></tr>').join('')
      :'<tr><td colspan="5">V77 연도별 근거자료 접근 미확인</td></tr>';
  }
  function renderEvidence() {
    E('tableCount').textContent='기존 통과 시험과 신규 미실행 관문';
    E('pageText').textContent='';
    const rows=[
      ['V43 · 103문항 구조 대조','PASS (기존 증거)','515 선택지/원전 SHA/정답표 일치','review/NOMUSA_FIRST_V43_103_SECOND_PASS_515_CHOICES_AND_LAW_QA_20261118.json'],
      ['V48 · 686문항 근거 복구','PASS (기존 실행)','GitHub Actions #44279151283 · 내용승인 아님','review/NOMUSA_FIRST_V48_686_AUTOMATION_EXECUTION_20261118.md'],
      ['V77 · 3,070문항 ID 전수','자료 확인','ID 연결만 완료 · 해설·승인 아님','review/NOMUSA_FIRST_V77_2008_2026_3070_RECONCILIATION_SUMMARY_20261119.json'],
      ['103문항 독립 2차 교열','HOLD','독립 원문·학술·법리 내용심사 0/103','review/NOMUSA_FIRST_V43_103_SECOND_PASS_515_CHOICES_AND_LAW_QA_20261118.json'],
      ['2차 328문항 최종 승인','HOLD','검토자 서명과 원고 SHA별 승인 없음','review/NOMUSA_V23_VALIDATION_LEDGER.json'],
      ['신규 콘솔 PC1440/M390/M360 E2E','PASS (로컬 검증)','Chromium 직접 실행 · 저장/복원/JSON/가로 넘침 검증','review/NOMUSA_QUALITY_CONSOLE_E2E_20261119.json'],
      ['보호 Preview 실사용 점검','HOLD','SSO 인증·실제 저장복원·문항 이동 검증 필요','']
    ];
    E('rows').innerHTML=rows.map(r=>'<tr><td><strong>'+esc(r[0])+'</strong></td><td colspan="2"><span class="tag '+(r[1].startsWith('PASS')?'green':'hold')+'">'+esc(r[1])+'</span></td>'
      +'<td>'+esc(r[2])+'</td><td>'+ (r[3]?link(gh(r[3]),'근거 열기'):'실행 전')+'</td></tr>').join('');
    E('rows').insertAdjacentHTML('beforeend','<tr><td colspan="5"><strong>기존 Vercel 프로젝트:</strong> gongin-nomusa-rc27-preview<br><strong>현재 접속 주소:</strong> '+esc(location.origin+location.pathname)+'<br><strong>GitHub 검토 브랜치:</strong> '+esc(BRANCH)+'<br><strong>차단:</strong> 신규 화면 E2E 결과 없으면 보호 Preview 검증 HOLD · main/Production 배포 불가</td></tr>');
  }
  function textField(key,label,val,hint,long=false) {
    const v=val == null?'':String(val);
    return '<label class="field">'+esc(label)+(hint?'<small class="muted">'+esc(hint)+'</small>':'')
      +'<textarea data-field="'+esc(key)+'" '+(long?'class="long"':'')+' maxlength="100000">'+esc(v)+'</textarea></label>';
  }
  function inputField(key,label,val,placeholder='') {
    return '<label class="field">'+esc(label)+'<input data-field="'+esc(key)+'" type="text" value="'+esc(val||'')+'" placeholder="'+esc(placeholder)+'" maxlength="1000"></label>';
  }
  function displayStr(v) {return '<pre>'+esc(v || '현재 원장에는 문항별 텍스트가 확인되지 않습니다. 공식 원본과 대조 후 입력하세요.')+'</pre>';}
  function htmlSource(r,d) {
    let parts='<div class="two"><div class="content-card"><h3>문항 원문·배점</h3>'+displayStr(r.q)+'<p class="muted">원본 페이지: '+esc(asPage(r.page))+'쪽 · '+esc(r.form||'')+'</p>';
    if(r.options.length)parts+='<h3>선택지 (검토용 원본 기록)</h3>'+r.options.map((v,i)=>'<p>'+(i+1)+'. '+esc(v)+'</p>').join('');
    else parts+='<div class="notice">선택지 텍스트가 현재 불러온 원장에 없습니다. 미대조 원문을 임의로 채우지 않습니다.</div>';
    parts+='</div><div class="content-card"><h3>공식 정답 근거·원전 링크</h3>';
    parts+='<p>원장에 기록된 정답: <strong>'+(r.answer.length?esc(r.answer.join(', ')):'미확인')+'</strong></p>';
    parts+='<p class="muted">정답번호 일치와 선택지 해설 내용승인은 서로 다릅니다.</p>';
    const refs=[];
    if(r.evidence && /^https:\/\//.test(r.evidence))refs.push(link(r.evidence,'원본 게시물'));
    if(r.evidence && /^(review|source_pdf|second|study-hub)\//.test(r.evidence))refs.push(link(gh(r.evidence),'검토 원장'));
    if(r.source?.originalRecord)refs.push(link(gh(r.source.originalRecord),'문항 초안'));
    if(r.source?.explanationEvidence)refs.push(link(gh(r.source.explanationEvidence),'선택지별 이유'));
    if(r.source?.source?.qnetPostUrl)refs.push(link(r.source.source.qnetPostUrl,'Q-Net'));
    parts+='<div class="link-list">'+refs.filter(Boolean).join('')+'</div>';
    parts+='<div class="notice">'+esc(holdReason(r))+' · 원문/선택지/수식/그래프 미검증 항목은 HOLD입니다.</div>';
    parts+=inputField('originalPage','원본 인쇄 쪽수 검토 메모',d.originalPage || asPage(r.page),'예 원본 12쪽 · 재대조 필요');
    parts+=textField('sourceDifference','공식 원문·선택지·수식·그래프 대조 메모',d.sourceDifference,'기존 문제·답안 데이터는 변경되지 않습니다.');
    parts+='</div></div>';
    return parts;
  }
  function htmlAnswer(r,d) {
    if(r.stage==='first') {
      const oldAnswer = r.source?.explanation || '';
      return '<div class="two"><div class="content-card"><h3>상세 해설·선택지별 이유</h3><p class="muted">기존 원본의 해설 초안은 근거 링크에서 확인합니다.</p>'
        +displayStr(oldAnswer)+'<div class="notice">51문항 선택지별 보강은 V43 초안에 반영되었습니다. 이 필드는 추가 독립 교열 기록입니다.</div>'
        +textField('choiceExplanations','①~⑤ 선택지별 검증·수정 제안',d.choiceExplanations,'검증 전 작성 메모 · 공식 정답 변경 없음',true)
        +'</div><div class="content-card"><h3>시험 대비 학습 메모</h3>'
        +textField('detailedDraft','검증용 상세해설 보강',d.detailedDraft,'승인 전 학습용 확정으로 표시되지 않습니다.',true)
        +textField('memoryKeywords','핵심 키워드·두음자',d.memoryKeywords)
        +'</div></div>';
    }
    return '<div class="two"><div class="content-card"><h3>2차 상세 모범답안 검토</h3><p class="muted">요구 분량 '+esc(sheet(r))+' · 이론과 사례형 구조 및 소문항 배점 비율 확인</p>'
      +'<p>원문 주제: '+esc(cap(r.title,200))+'</p><p>정확한 기존 완성형 답안은 원래 2차 학습화면에서 확인합니다.</p>'
      +'<div class="link-list">'+link('/second/','기존 2차 상세답안 열기')+'</div>'
      +textField('detailedDraft','상세답안 검토·보강 초안',d.detailedDraft,'기존 답안을 덮어쓰지 않습니다.',true)
      +'</div><div class="content-card"><h3>시험장 압축답안과 암기</h3><div class="notice">50점 8~10장 · 25점 4장 · 15점 3장 · 10점 이하 2장. 손글씨 실측 검증 전 분량 최종승인 HOLD.</div>'
      +textField('shortDraft','시험장 압축답안 보강 초안',d.shortDraft,'소문항 배점별 분량 배분',true)
      +textField('memoryKeywords','암기 키워드 · 3·3·3 회상',d.memoryKeywords)
      +'</div></div>';
  }
  function htmlLaw(r,d) {
    const fields=related(r);
    return '<div class="notice">각 입력값은 사람의 검토기록입니다. 시행일·판례번호·서지정보가 실제 원본에서 확인되기 전에는 승인 상태를 올리지 마세요.</div>'
      +'<div class="two"><div class="content-card"><h3>분야별 검증 근거</h3>'
      +textField('examLaw','시험 당시 시행 조문·효력일',d.examLaw,'현행법이 아닌 시험 당일 시행본',true)
      +textField('examSupplement','부칙·경과규정 및 시행일',d.examSupplement)
      +textField('precedent','판결선고일·사건번호·판례 전문',d.precedent)
      +textField('caseApplication','쟁점별 사안포섭',d.caseApplication)
      +'</div><div class="content-card"><h3>학술·계산 검증</h3><p class="muted">과목별 필수 확인: '+esc(fields.join(' · '))+'</p>'
      +textField('academicAuthority','학자·저서·논문·발행연도',d.academicAuthority)
      +textField('comparison','학설·모형 비교표 검토',d.comparison)
      +textField('calculation','수식·함수·그래프·계산 검산',d.calculation)
      +textField('authorityUrl','근거 원문 URL·서지·조회일',d.authorityUrl)
      +'</div></div>';
  }
  function htmlWrite(r,d) {
    if(r.stage==='first')return '<div class="content-card"><h3>기존 1차 문제풀이와 연결</h3><p>기존 1차의 선택지 제출, 자동저장, 새로고침 복원, 검토 플래그, 오답노트, 진도율, 재시험, 실전 모드, JSON 복원은 원래 화면을 사용합니다.</p>'
      +'<div class="link-list">'+link('/study-hub/','기존 학습 허브 이동')+link('/','기존 1차 문제풀이 이동')+'</div>'
      +'<div class="notice">원본 교열 승인이 없는 103·686문항은 자동채점 문제은행에 승격하지 않습니다.</div></div>';
    return '<div class="content-card"><h3>2차 학습 흐름</h3><div class="status-line"><span class="tag blue">① 상세답안</span><span class="tag blue">② 압축답안</span><span class="tag blue">③ 직접 작성</span><span class="tag blue">④ 비교·복습</span></div>'
      +'<p class="muted">기존 본문을 먼저 읽은 후 '+esc(sheet(r))+'를 목표로 직접 작성하고 비교하세요.</p>'
      +'<div class="link-list">'+link('/second/','원래 상세·압축 학습화면')+'</div>'
      +'<div class="two"><div>'+textField('writing','③ 직접 작성 · 자동저장',d.writing,'입력 즉시 독립 저장',true)+'</div>'
      +'<div>'+textField('reviewWriting','④ 자기 비교·복습 메모',d.reviewWriting,'빠진 논점, 법리, 수식, 비교표, 분량',true)+'</div></div>'
      +'<p class="muted">이 화면의 작성 기록은 기존 RC27 답안 저장키를 변경하지 않습니다.</p></div>';
  }
  function checkboxField(key,label,d) {
    const checks=jsonObj(d.checks)?d.checks:{};
    return '<label><input type="checkbox" data-check="'+esc(key)+'" '+(checks[key]?'checked':'')+'>'+esc(label)+'</label>';
  }
  function htmlReview(r,d) {
    const s=getStatus(r);
    return '<div class="two"><div class="content-card"><h3>문항 승인 상태</h3><label class="field">상태'
      +'<select id="itemStatus">'+STATES.map(v=>'<option value="'+esc(v)+'" '+(s===v?'selected':'')+'>'+esc(v)+'</option>').join('')+'</select></label>'
      +'<div class="notice">승인 완료는 검토기록용이며 실제 자동채점 반영을 실행하지 않습니다. 독립심사 증빙 없이는 승인으로 전환할 수 없습니다.</div>'
      +'<div class="checks">'
      +checkboxField('original','공식 원문·5선지 독립 대조',d)
      +checkboxField('answer','공식 최종정답 원장 대조',d)
      +checkboxField('theory','당시 법령·판례 / 학술·계산 검증',d)
      +checkboxField('independent','독립 2차 교열 증빙',d)
      +'</div>'
      +textField('reviewNote','검토 메모',d.reviewNote,'검토일·시험일·오류·교정안',true)
      +textField('blocking','현재 차단 사유',d.blocking)
      +textField('nextAction','다음 안전한 작업',d.nextAction)
      +'</div><div class="content-card"><h3>독립 검토 이력</h3>'
      +inputField('reviewer1','독립 검토자 1 · 서면 증빙 식별',d.reviewer1,'검토자/날짜/근거')
      +inputField('reviewer2','독립 검토자 2 · 서면 증빙 식별',d.reviewer2,'검토자/날짜/근거')
      +textField('approvalEvidence','독립승인 서명자료·문항 원고 SHA·승인 의견',d.approvalEvidence,'문항별 증빙 없으면 승인 금지')
      +'<p class="muted">원전 SHA: '+esc(r.source?.textSHA256 || r.source?.originalCropSHA256 || '미확인')+'</p>'
      +'<p class="muted">최근 작업시각: '+esc(d.updatedAt || '없음')+'</p>'
      +'<div class="link-list">'+link(gh('review/NOMUSA_V23_OPEN_ISSUES.md'),'2차 고위험 보류')+link(gh('review/NOMUSA_FIRST_V47_25_LAW_FULL_TEXT_HANDOFF_PACKET_20261118.md'),'법률 25개 핸드오프')+'</div></div></div>';
  }
  function renderDetail() {
    const r=bucket.get(current);if(!r)return;const d=itemData(r.id);
    E('detail').hidden=false;
    E('detailHeading').textContent= r.year+'년 · '+r.subject+' · '+(r.stage==='second'?'2차':'1차')+' 문항';
    E('detailMeta').textContent=r.id+(r.points?' · '+r.points+'점 · '+sheet(r):' · A형')+' · '+getStatus(r);
    E('detailInfo').innerHTML='<div class="status-line"><span class="tag hold">최종 내용검증 별도</span>'
      +(r.kind==='first103'?'<span class="tag blue">V43 구조 대조 PASS</span>':'')
      +'<span class="tag gray">저장키 분리</span></div>';
    for(const b of E('detailTabs').querySelectorAll('button'))b.classList.toggle('active',b.dataset.tab===detailTab);
    const html={source:htmlSource,answer:htmlAnswer,law:htmlLaw,write:htmlWrite,review:htmlReview}[detailTab](r,d);
    E('detailContent').innerHTML=html;
    if(detailTab==='source' && r.kind==='first103' && r.source?.originalRecord) {
      loadQuestionSource(r).catch(()=>{});
    }
  }
  async function loadQuestionSource(r) {
    if(sourceRecord?.id===r.id)return;
    const path=r.source.originalRecord;
    if(!/^(review)\/[A-Za-z0-9_.\/-]+\.json$/.test(path))return;
    try {
      const response=await fetch('/'+path);
      if(!response.ok)return;
      const json=await response.json();
      const candidates=Array.isArray(json)?json:[json.rows,json.items,json.questions,json.records,json.drafts].find(Array.isArray)||[];
      const row=candidates.find(x=>[x.id,x.questionId,x.key,x.k].includes(r.id));
      if(!row)return;
      sourceRecord={id:r.id,row};
      const question=row.stem || row.sourceText || row.questionText || row.question || '';
      const options=row.options || row.choices || row.o || [];
      if(current!==r.id || detailTab!=='source')return;
      const root=E('detailContent').querySelector('.content-card');
      if(root && question) {
        const pre=document.createElement('div');
        pre.className='stamp';
        pre.textContent='V43 원문 전사 초안 · 독립 대조 필요\n'+String(question)
          +(Array.isArray(options)?'\n'+options.map((o,i)=>(i+1)+'. '+o).join('\n'):'');
        root.append(pre);
      }
    } catch {/* source remains HOLD */}
  }
  function openItem(id) {
    if(!bucket.has(id))return;
    current=id;detailTab='source';sourceRecord=null;
    renderDetail();E('detail').scrollIntoView({block:'start',behavior:'smooth'});
  }
  function validateApproval(d) {
    const c=d.checks || {};
    return ['original','answer','theory','independent'].every(k=>c[k]===true)
      && clean(d.reviewer1).length>=5 && clean(d.reviewer2).length>=5
      && clean(d.reviewer1)!==clean(d.reviewer2) && clean(d.approvalEvidence).length>=20;
  }
  function writeValue(key,value) {
    if(!current)return;
    if(!isSafeKey(key))return;
    const d=itemData(current);
    d[key]=typeof value==='string'?value.slice(0,100000):value;
    d.updatedAt=new Date().toISOString();
    persist();
  }
  function bind() {
    E('views').addEventListener('click',e=>{const b=e.target.closest('[data-view]');if(b)switchView(b.dataset.view);});
    E('rows').addEventListener('click',e=>{const b=e.target.closest('[data-open]');if(b)openItem(b.dataset.open);});
    for(const id of ['q','year','subject','status','round'])E(id).addEventListener(id==='q'||id==='round'?'input':'change',()=>{page=0;filter();});
    E('clearBtn').onclick=()=>{for(const id of ['q','year','subject','status','round'])E(id).value='';page=0;filter();};
    E('prevBtn').onclick=()=>{page=Math.max(0,page-1);filter();};
    E('nextBtn').onclick=()=>{page++;filter();};
    E('closeDetail').onclick=()=>{E('detail').hidden=true;current=null;};
    E('detailTabs').addEventListener('click',e=>{const b=e.target.closest('[data-tab]');if(b && current){detailTab=b.dataset.tab;renderDetail();}});
    E('detailContent').addEventListener('input',e=>{const fld=e.target.dataset.field;if(fld)writeValue(fld,e.target.value);});
    E('detailContent').addEventListener('change',e=>{
      const check=e.target.dataset.check;
      if(check){const d=itemData(current);if(!jsonObj(d.checks))d.checks={};d.checks[check]=e.target.checked;d.updatedAt=new Date().toISOString();auditLog(current,'검토 증빙 표시 '+check);return;}
      if(e.target.id==='itemStatus'){
        const value=e.target.value,d=itemData(current);
        if(!STATES.includes(value))return;
        if(value==='승인 완료'&&!validateApproval(d)){
          toast('승인 불가: 원문·정답·법리/학술·독립심사 4개 증빙과 검토자 2명·서면근거가 필요합니다.');
          e.target.value=getStatus(bucket.get(current));return;
        }
        d.status=value;d.updatedAt=new Date().toISOString();auditLog(current,'상태 변경 → '+value);
        renderDetail();filter();
      }
    });
    E('exportBtn').onclick=()=> {
      const payload=JSON.stringify({...record,exportedAt:new Date().toISOString(),sourceRepo:REPO,sourceBranch:BRANCH},null,2);
      const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([payload],{type:'application/json;charset=utf-8'}));
      a.download='nomusa_quality_review_'+new Date().toISOString().slice(0,10)+'.json';a.click();
      setTimeout(()=>URL.revokeObjectURL(a.href),1000);toast('품질관리 기록 JSON 내보내기 완료');
    };
    E('importInput').onchange=async e=>{
      const file=e.target.files?.[0];if(!file)return;
      try {
        if(file.size>5*1024*1024)throw Error('파일이 5MB를 초과합니다.');
        const incoming=JSON.parse(await file.text());
        if(!jsonObj(incoming)||incoming.schema!==SCHEMA||!jsonObj(incoming.items))throw Error('품질관리 전용 JSON이 아닙니다.');
        if(Object.keys(incoming.items).some(k=>!isSafeKey(k)))throw Error('허용되지 않는 키가 있습니다.');
        for(const [id,v] of Object.entries(incoming.items)) {
          if(!jsonObj(v)||!isSafeKey(id))throw Error('문항 기록 형식이 잘못되었습니다.');
          if(v.status==='승인 완료'&&!validateApproval(v))throw Error('승인 증빙이 없는 기록이 포함되어 있습니다.');
        }
        if(!confirm('가져온 기록으로 품질관리 메모를 병합합니다. 기존 1차·2차 저장키는 변경하지 않습니다. 진행할까요?'))return;
        for(const [id,v] of Object.entries(incoming.items)) record.items[id]={...(record.items[id]||{}),...v};
        record.log=[...record.log,...(Array.isArray(incoming.log)?incoming.log:[])].slice(-250);
        blockedStorage=false;
        if(!persist())throw Error('브라우저 저장에 실패했습니다.');
        filter();if(current)renderDetail();toast('검토 기록 JSON 병합·복원 완료');
      }catch(err){toast('가져오기 HOLD: '+err.message);}
      finally{e.target.value='';}
    };
  }
  async function init() {
    readLocal();metrics();bind();E('locationText').textContent=location.host;
    prepareBaseline();
    await addPacked();
    const fetched=await Promise.all(Object.entries(SOURCES).map(async ([k,u])=>[k,await loadFile(k,u)]));
    const resources=Object.fromEntries(fetched);
    addFrom103(resources.first103);
    addFrom686(resources.remaining686);
    addEssay(resources.essay328);
    addCoverageGroups();
    addSocial();
    all=[...bucket.values()].sort((a,b)=>(b.year-a.year)||a.stage.localeCompare(b.stage)||a.subject.localeCompare(b.subject,'ko')||a.id.localeCompare(b.id));
    fillSelect();
    E('alerts').innerHTML='<div class="alert"><strong>승인 게이트:</strong> V43 103문항의 선택지 해설은 초안 구조검사를 마쳤지만 독립교열 0건입니다. 2차 328개도 독립 전문가 최종승인 0건입니다. <strong>새 콘솔의 PC1440/모바일390·360 로컬 Chromium E2E PASS, 보호 Preview 인증 후 실사용 검증 HOLD</strong>입니다.'
      +(failures.length?'<details><summary>자료 로드 제한 '+failures.length+'건</summary>'+failures.map(esc).join(' · ')+'</details>':'')+'</div>';
    switchView('all');
    window.NOMUSA_QUALITY_CONSOLE_READONLY = Object.freeze({
      schema:SCHEMA, reviewMode:true, sourceKeysUnchanged:true, approvalIsLocalOnly:true,
      getTotals:()=>({loaded:all.length,first103:all.filter(x=>x.kind==='first103').length,second:all.filter(x=>x.stage==='second').length,first686:all.filter(x=>x.kind==='first686'&&!x.group).length}),
      viewKeys:()=>Object.keys(record.items)
    });
  }
  init().catch(err=>{E('alerts').textContent='콘솔 초기화 HOLD: '+err.message;E('rows').innerHTML='<tr><td colspan="5">로드 실패 · 기존 학습 화면은 변경되지 않았습니다.</td></tr>';});
})();
#!/usr/bin/env python3
"""Run only against local user-supplied PDFs. Does NOT certify official answers.
Dependencies: pip install pymupdf
python scripts/rc29-2-pdf-reconcile.py --rc27 ZIP --rc17 ZIP --src-dir DIR
"""
import argparse,csv,hashlib,json,re,unicodedata,zipfile
from pathlib import Path
import fitz
arg=argparse.ArgumentParser()
arg.add_argument('--rc27',required=True,type=Path)
arg.add_argument('--rc17',required=True,type=Path)
arg.add_argument('--src-dir',required=True,type=Path)
arg.add_argument('--out',type=Path,default=Path('rc29-evidence/rc29-2-local'))
a=arg.parse_args()
m=json.loads(Path('data/rc29-2-source-manifest.json').read_text(encoding='utf8'))
with zipfile.ZipFile(a.rc27) as z:
 html=z.read('site/index.html').decode('utf8')
 mark='const FIRST='
 if mark not in html:raise ValueError('RC27 FIRST marker not found')
 src,_=json.JSONDecoder().raw_decode(html.split(mark,1)[1])
with zipfile.ZipFile(a.rc17) as z:
 keyrows=json.loads(z.read('nomusa_rc17_patch/data/rc17_official_A_keys_2022_2026.json'))['records']
keys={(int(x['year']),x['subject'],int(x['question_no'])):x['answers'] for x in keyrows}
if len(src)!=565 or len(keys)!=1020:raise ValueError('Candidate/key count unexpected')
lookup={};pages={}
for info in m['pdfSources']:
 p=a.src_dir/info['name']
 raw=p.read_bytes()
 if hashlib.sha256(raw).hexdigest()!=info['sha']:raise ValueError('PDF sha256 mismatch '+info['name'])
 pdf=fitz.open(stream=raw,filetype='pdf')
 if len(pdf)!=info['pages']:raise ValueError('PDF page count mismatch '+info['name'])
 pages[info['name']]=[page.get_text() for page in pdf]
 for sub in info['subjects']:
  lookup[(info['year'],sub)]=info['name']
def norm(x):
 return re.sub(r'\s+','',unicodedata.normalize('NFKC',str(x))).replace('·','ㆍ').replace('・','ㆍ')
out=[];draft=[];ids=set()
for q in src:
 y,s,n=int(q['year']),q['subject'],int(q['no'])
 k=(y,s,n)
 if k in ids:raise ValueError('duplicate candidate '+str(k))
 ids.add(k)
 f=lookup[(y,s)]
 page=int(q.get('source_page') or 0)
 if not 1<=page<=len(pages[f]):raise ValueError('source page invalid '+str(k))
 if not isinstance(q.get('options'),list) or len(q['options'])!=5:raise ValueError('invalid options '+str(k))
 text=norm(pages[f][page-1])
 stem=norm(q['stem'])
 stem_ok=bool(stem and stem in text)
 options=sum(bool(norm(v).lstrip('①②③④⑤') in text) for v in q['options'])
 full=stem_ok and options==5
 ans=keys.get(k)
 if not ans:raise ValueError('missing unapproved answer reference '+str(k))
 row={'id':q['id'],'year':y,'subject':s,'num':n,'sourceFile':f,'sourcePage':page,
      'stemExact':stem_ok,'matchedOptions':options,'fullTextMatch':full,
      'referenceAnswerLabels':ans,'scoringApproved':False,
      'verificationStatus':'PENDING_VISUAL_AND_FINAL_ANSWER_REVIEW'}
 out.append(row)
 draft.append({'id':q['id'],'year':y,'subject':s,'num':n,'question':q['stem'],
               'options':q['options'],'answer':None,'acceptedAnswers':None,
               'officialAnswerLabelsReference':ans,'sourceEvidence':row,
               'verificationStatus':'PENDING_VISUAL_AND_FINAL_ANSWER_REVIEW'})
years={}
for yy in (2022,2023,2024,2025,2026):
 subset=[x for x in out if x['year']==yy]
 years[yy]={'candidates':len(subset),'matched':sum(x['fullTextMatch'] for x in subset),
            'unmatched':sum(not x['fullTextMatch'] for x in subset)}
 for expected in m['byYear']:
  if expected['year']==yy and (len(subset),years[yy]['matched'],years[yy]['unmatched'])!=(expected['candidates'],expected['textMatch'],expected['needsReview']):
   raise ValueError('source evidence drift '+str(yy))
status={'schema':'rc29-2-local-original-pdf-v1','status':'SOURCE_PDF_HASHES_OK_RELEASE_HOLD',
        'candidateRows':len(out),'exactTextMatches':sum(x['fullTextMatch'] for x in out),
        'textMismatchRows':sum(not x['fullTextMatch'] for x in out),
        'scoringApproved':0,'byYear':years,
        'caveat':'No visual signoff or final-answer crosscheck. Text-layer matching is not grading authorization.'}
a.out.mkdir(parents=True,exist_ok=True)
(a.out/'source-summary.json').write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(a.out/'staged-unverified-565.json').write_text(json.dumps(draft,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
for name,rs in [('all-source-checks.csv',out),('priority-mismatch-checks.csv',[x for x in out if not x['fullTextMatch']])]:
 with (a.out/name).open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(out[0].keys()));w.writeheader()
  for x in rs:w.writerow({k:'/'.join(map(str,v)) if isinstance(v,list) else v for k,v in x.items()})
print(json.dumps(status,ensure_ascii=False,indent=2))

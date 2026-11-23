"""Cached Chinese translation of public feed text; original text is never overwritten."""
from __future__ import annotations
import argparse, hashlib, json, re, time, urllib.parse, urllib.request
from pathlib import Path
from core import stamp

MODEL = 'google-translate-web'
REVISION = 'zh-CN-news-v1'
FIELDS = ('title', 'summary')

def needs_chinese(text):
    text = str(text or '')
    latin = len(re.findall(r'[A-Za-z]', text))
    chinese = len(re.findall(r'[\u3400-\u9fff]', text))
    return latin >= 4 and chinese < max(2, latin * .14)

def source_hash(article):
    return hashlib.sha256(json.dumps({k: article.get(k, '') for k in FIELDS}, ensure_ascii=False, sort_keys=True).encode()).hexdigest()

def translated(article):
    value = article.get('translation', {})
    return value.get('sourceHash') == source_hash(article) and value.get('revision') == REVISION and all(
        isinstance(value.get(k), str) and value[k].strip() and not needs_chinese(value[k])
        for k in FIELDS if needs_chinese(article.get(k)))

def translation_status(articles):
    foreign = [a for a in articles if any(needs_chinese(a.get(k)) for k in FIELDS)]
    done = sum(translated(a) for a in foreign)
    return {'engine': MODEL, 'translated': done, 'pending': len(foreign)-done, 'total': len(foreign), 'scope': 'title-and-feed-summary'}

def terminology(source, text):
    # Context-specific, deterministic name/term corrections, no invented facts.
    mappings = [('Codex', ['法典']), ('Gemini', ['双子座','双子星']), ('ChatGPT', ['查特格普特','查特格PT']), ('MoE', ['教育部']), ('Genie', ['精灵']), ('Kling', ['克林']), ('Daybreak Red', ['黎明红']), ('Daybreak Blue', ['黎明蓝'])]
    for name, alternatives in mappings:
        if re.search(r'\b'+name+r'\b',source,re.I):
            for wrong in alternatives:text=text.replace(wrong,'混合专家（MoE）' if name=='MoE' else name)
    if re.search(r'\bharness(?:es)?\b',source,re.I):text=text.replace('线束','运行框架')
    if re.search(r'\btrain(?:ing)?\b',source,re.I):text=text.replace('培训','训练')
    if re.search(r'\bFLOPs?\b',source):text=text.replace('FLOP 所说的','理论计算量预估').replace('FLOPs 所说的','理论计算量预估')
    if source.strip().lower()=='perplexity and intelligence':return '困惑度与智能'
    return text

class WebTranslator:
    """Public web translation, not the paid Cloud Translation API or an SLA.

    Only published feed text is sent. Rate limits/errors leave a visible backlog.
    No browser data, account cookies or private credentials are used.
    """
    @staticmethod
    def translate(text):
        query=urllib.parse.urlencode({'client':'gtx','sl':'auto','tl':'zh-CN','dt':'t','q':text})
        request=urllib.request.Request('https://translate.googleapis.com/translate_a/single?'+query,headers={'User-Agent':'AI-Rizhi/3.0 (public news reader)'})
        with urllib.request.urlopen(request,timeout=18) as response:
            raw=response.read(131073)
        if len(raw)>131072:raise ValueError('translation response too large')
        result=json.loads(raw)
        if not isinstance(result,list) or not result or not isinstance(result[0],list):raise ValueError('translation response changed')
        output=''.join(part[0] for part in result[0] if isinstance(part,list) and part and isinstance(part[0],str))
        return output

    def __call__(self,texts):
        # Preserve newline alignment; fewer requests and context across short fields.
        result=[];chunk=[];size=0
        for text in texts:
            if chunk and size+len(text)>2200:
                result.extend(self.batch(chunk));chunk=[];size=0
            chunk.append(text);size+=len(text)+1
        if chunk:result.extend(self.batch(chunk))
        return result

    def batch(self,texts):
        output=self.translate('\n'.join(texts))
        lines=output.strip().split('\n')
        if len(lines)!=len(texts):raise ValueError('translation paragraph alignment changed')
        time.sleep(1.2)
        return [terminology(source,line.strip()) for source,line in zip(texts,lines)]

def translate_articles(articles, translator, max_articles=500, seconds=600, checkpoint=None):
    started = time.monotonic(); done = 0; failed = 0; consecutive_failures = 0
    backlog = sorted((a for a in articles if any(needs_chinese(a.get(k)) for k in FIELDS) and not translated(a)), key=lambda a:(a.get('eventDate',''),a.get('publishedAt','')), reverse=True)
    for offset in range(0, min(len(backlog), max_articles), 4):
        if time.monotonic()-started > seconds: break
        batch = backlog[offset:min(offset+4, max_articles)]
        work = [(a,k) for a in batch for k in FIELDS if needs_chinese(a.get(k))]
        try:
            output = translator([str(a[k]) for a,k in work])
            if len(output) != len(work): raise ValueError('translation count mismatch')
            results = {}
            for (a,k),text in zip(work,output):
                if not isinstance(text,str) or not text.strip() or needs_chinese(text) or len(text)>6000 or re.search(r'(.{2,5})\1{5,}',text):
                    raise ValueError('translation did not return Chinese')
                results.setdefault(a['id'], {})[k] = text.strip()
            consecutive_failures = 0
            for a in batch:
                a['translation'] = {**{k:a.get(k,'') for k in FIELDS}, **results.get(a['id'],{}), 'sourceHash':source_hash(a), 'engine':MODEL, 'revision':REVISION, 'translatedAt':stamp()}
                done += 1
        except Exception as exc:
            # Do not leak response bodies or credentials in public output.
            failed += len(batch); consecutive_failures += 1
            if getattr(exc,'code',None) in (403,429):
                print('翻译入口限流，下次更新继续。',flush=True)
                break
            print('翻译批次失败：'+type(exc).__name__, flush=True)
            if consecutive_failures >= 3:break
        if checkpoint:checkpoint()
        print(f'中文翻译：本次完成 {done} 条，失败 {failed} 条。', flush=True)
        time.sleep(.25)
    return {**translation_status(articles), 'doneThisRun':done, 'failedThisRun':failed, 'checkedAt':stamp()}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--library',default=str(Path(__file__).resolve().parents[1]/'site/library.json'));parser.add_argument('--limit',type=int,default=500);parser.add_argument('--seconds',type=int,default=600)
    args=parser.parse_args();path=Path(args.library);data=json.loads(path.read_text());articles=data['articles']
    def save_progress():
        data.setdefault('status',{})['translation']={**translation_status(articles),'state':'partial','checkedAt':stamp()}
        temp=path.with_suffix('.tmp');temp.write_text(json.dumps(data,ensure_ascii=False,indent=2));temp.replace(path)
    try:
        report=translation_status(articles)
        if report['pending']:report=translate_articles(articles,WebTranslator(),args.limit,args.seconds,checkpoint=save_progress)
        else:report.update(doneThisRun=0,failedThisRun=0,checkedAt=stamp())
        report['state']='ready' if not report['pending'] else 'partial'
    except Exception as exc:
        report={**translation_status(articles),'state':'unavailable','error':type(exc).__name__,'checkedAt':stamp()}
        print('中文翻译暂未完成：'+type(exc).__name__,flush=True)
    data.setdefault('status',{})['translation']=report
    temp=path.with_suffix('.tmp');temp.write_text(json.dumps(data,ensure_ascii=False,indent=2));temp.replace(path)
    print(json.dumps(report,ensure_ascii=False),flush=True)

if __name__=='__main__':main()

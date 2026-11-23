"""Cached Chinese translation of public feed text; original text is never overwritten."""
from __future__ import annotations
import argparse, datetime as dt, hashlib, json, re, time, urllib.parse, urllib.request
from pathlib import Path
from core import stamp

MODEL = 'Qwen3-4B-Q4_K_M'
REVISION = 'qwen3-bc640142-natural-zh-v2'
REVIEW_REVISION='source-summary-review-v1'
VALID_REVISIONS = {REVISION,REVIEW_REVISION}
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
    return value.get('sourceHash') == source_hash(article) and value.get('revision') in VALID_REVISIONS and len(value.get('summary',''))<=320 and len(re.findall(r'[\u3400-\u9fff]',value.get('title','')))>=2 and all(
        isinstance(value.get(k), str) and len(re.findall(r'[\u3400-\u9fff]',value[k]))>=2
        for k in FIELDS if needs_chinese(article.get(k)))

def translation_status(articles):
    foreign = [a for a in articles if any(needs_chinese(a.get(k)) for k in FIELDS)]
    done = sum(translated(a) for a in foreign)
    return {'engine': MODEL, 'translated': done, 'pending': len(foreign)-done, 'total': len(foreign), 'scope': 'title-and-feed-summary'}

def terminology(source, text):
    # Context-specific, deterministic name/term corrections, no invented facts.
    mappings = [('Codex', ['法典','古典']), ('Gemini', ['双子座','双子星','双胞胎']), ('ChatGPT', ['查特格普特','查特格PT']), ('MoE', ['教育部']), ('Genie', ['精灵']), ('Kling', ['克林']), ('Daybreak Red', ['黎明红']), ('Daybreak Blue', ['黎明蓝'])]
    for name, alternatives in mappings:
        if re.search(r'\b'+name+r'\b',source,re.I):
            for wrong in alternatives:text=text.replace(wrong,'混合专家（MoE）' if name=='MoE' else name)
    if re.search(r'\bharness(?:es)?\b',source,re.I):
        for wrong in ['线束','马具','⁇ 带','⁇带']:text=text.replace(wrong,'运行框架')
    if re.search(r'\bTransformers?\b',source):text=text.replace('变压器','Transformer')
    if re.search(r'\bmodels?\b',source,re.I) and not re.search(r'role model',source,re.I):text=text.replace('车型','模型').replace('模特','模型')
    if re.search(r'\btrain(?:ing)?\b',source,re.I):text=text.replace('培训','训练')
    if re.search(r'\bFLOPs?\b',source):text=text.replace('FLOP 所说的','理论计算量预估').replace('FLOPs 所说的','理论计算量预估')
    if 'Flash' in source:text=text.replace('闪存','Flash')
    if source.strip().lower()=='perplexity and intelligence':return '困惑度与智能'
    missing=[name for name in ['Codex','ChatGPT','Gemini','Claude','DeepSeek','Qwen','Llama','Hugging Face','OpenAI','Genie','Kling','Gemma'] if re.search(r'\b'+name+r'\b',source,re.I) and name.lower() not in text.lower()]
    if missing:text+='（'+', '.join(missing)+'）'
    return text

def sentences(text):
    return [part.strip() for part in re.split(r'(?<=[.!?])\s+(?=[A-Z])',text.strip()) if part.strip()]

class LocalTranslator:
    def __init__(self):
        from editor import QwenEditor
        self.editor=QwenEditor()
    def edit(self,articles):return self.editor.edit(articles)
    def close(self):self.editor.close()

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
    def eligible(a):
        review=a.get('translationReview',{})
        return review.get('sourceHash')!=source_hash(a) or review.get('retryAfter','')<=stamp()
    backlog = sorted((a for a in articles if any(needs_chinese(a.get(k)) for k in FIELDS) and not translated(a) and eligible(a)), key=lambda a:(a.get('platform')=='GitHub',a.get('eventDate',''),a.get('publishedAt','')), reverse=True)
    batches=[backlog[offset:min(offset+4,max_articles)] for offset in range(0,min(len(backlog),max_articles),4)]
    while batches:
        if time.monotonic()-started > seconds: break
        batch = batches.pop(0)
        work = [(a,k) for a in batch for k in FIELDS if needs_chinese(a.get(k))]
        try:
            edited=translator.edit(batch) if hasattr(translator,'edit') else None
            output = [next(row for row in edited if row['id']==a['id'])[k] for a,k in work] if edited is not None else translator([str(a[k]) for a,k in work])
            if len(output) != len(work): raise ValueError('translation count mismatch')
            results = {}
            for (a,k),text in zip(work,output):
                if not isinstance(text,str) or not text.strip() or len(re.findall(r'[\u3400-\u9fff]',text))<2 or len(text)>6000 or re.search(r'(.{2,5})\1{5,}',text):
                    raise ValueError('translation did not return Chinese')
                results.setdefault(a['id'], {})[k] = text.strip()
            consecutive_failures = 0
            for a in batch:
                if edited is not None and re.fullmatch(r'[vb]?\d[\w.\-]*',a['title'],re.I):
                    results.setdefault(a['id'],{})['title']=next(row['title'] for row in edited if row['id']==a['id'])
                a['translation'] = {**{k:a.get(k,'') for k in FIELDS}, **results.get(a['id'],{}), 'sourceHash':source_hash(a), 'engine':MODEL, 'revision':REVISION, 'translatedAt':stamp(),'style':'natural-zh','simple':next((row.get('simple','') for row in (edited or []) if row['id']==a['id']),'')}
                a.pop('translationReview',None)
                done += 1
        except Exception as exc:
            # Do not leak response bodies or credentials in public output.
            # Isolate malformed model output instead of blocking unrelated articles.
            if len(batch)>1 and isinstance(exc,(ValueError,KeyError,StopIteration)):
                batches[0:0]=[[a] for a in batch]
                print('中文整理批次需逐条核对，继续处理。',flush=True)
                continue
            for a in batch:
                a['translationReview']={'sourceHash':source_hash(a),'lastAttemptAt':stamp(),'retryAfter':(dt.datetime.fromisoformat(stamp())+dt.timedelta(hours=24)).isoformat(),'reason':'中文稿未通过自动检查，保留原文。'}
            failed += len(batch); consecutive_failures = consecutive_failures+1 if not isinstance(exc,ValueError) else 0
            if getattr(exc,'code',None) in (403,429):
                print('翻译入口限流，下次更新继续。',flush=True)
                break
            print('翻译批次失败：'+type(exc).__name__+(' / '+str(exc)[:100] if isinstance(exc,ValueError) else ''), flush=True)
            if consecutive_failures >= 3:break
        if checkpoint:checkpoint()
        print(f'中文翻译：本次完成 {done} 条，失败 {failed} 条。', flush=True)
        time.sleep(.25)
    return {**translation_status(articles), 'doneThisRun':done, 'failedThisRun':failed, 'checkedAt':stamp()}

def apply_editorial(articles,reviews=None):
    from editor import validate_edits,correct_plan_names
    if reviews is None:
        path=Path(__file__).with_name('editorial-zh.json')
        reviews=json.loads(path.read_text()) if path.exists() else {}
    count=0
    for a in articles:
        old=a.get('translation',{})
        if old.get('sourceHash')==source_hash(a):
            corrected=correct_plan_names(a,old)
            if corrected!=old:a['translation']=corrected
        reviewed=reviews.get(source_hash(a))
        if not reviewed:continue
        row=validate_edits([a],[{'id':a['id'],**reviewed}])[0]
        if old.get('revision')==REVIEW_REVISION and all(old.get(k)==row.get(k) for k in ('title','summary','simple')):continue
        a['translation']={**{k:row[k] for k in ('title','summary','simple')},'sourceHash':source_hash(a),'engine':'source-summary-review','revision':REVIEW_REVISION,'style':'natural-zh','translatedAt':stamp(),'reviewNote':'按公开来源的标题与摘要校订，未声称阅读全文或实测。'}
        a.pop('translationReview',None);count+=1
    return count

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--library',default=str(Path(__file__).resolve().parents[1]/'site/library.json'));parser.add_argument('--limit',type=int,default=500);parser.add_argument('--seconds',type=int,default=600)
    args=parser.parse_args();path=Path(args.library);data=json.loads(path.read_text());news=data['articles'];resource_path=path.parent/'discovery.json';resource_data=json.loads(resource_path.read_text()) if resource_path.exists() else {'items':[]};resource_items=resource_data.get('items',[]);articles=news+[a for a in resource_items if not a.get('curated') and a.get('platform')=='GitHub']
    def save_progress():
        if resource_path.exists():
            resource_temp=resource_path.with_suffix('.tmp');resource_temp.write_text(json.dumps(resource_data,ensure_ascii=False,indent=2));resource_temp.replace(resource_path)
        data.setdefault('status',{})['translation']={**translation_status(news),'state':'partial','checkedAt':stamp()}
        temp=path.with_suffix('.tmp');temp.write_text(json.dumps(data,ensure_ascii=False,indent=2));temp.replace(path)
    reviewed=apply_editorial(articles)
    if reviewed:print('来源摘要校订：'+str(reviewed)+' 条。',flush=True)
    engine=None
    try:
        report=translation_status(articles)
        if report['pending']:
            engine=LocalTranslator()
            report=translate_articles(articles,engine,args.limit,args.seconds,checkpoint=save_progress)
        else:report.update(doneThisRun=0,failedThisRun=0,checkedAt=stamp())
        report['state']='ready' if not report['pending'] else 'partial'
    except Exception as exc:
        report={**translation_status(articles),'state':'unavailable','error':type(exc).__name__,'checkedAt':stamp()}
        print('中文翻译暂未完成：'+type(exc).__name__,flush=True)
    finally:
        if engine and hasattr(engine,'close'):engine.close()
    data.setdefault('status',{})['translation']={**report,**translation_status(news)}
    data['status']['translation']['state']='ready' if not data['status']['translation']['pending'] else 'partial'
    if resource_path.exists():
        resource_data.setdefault('status',{})['translation']=translation_status([a for a in resource_items if not a.get('curated') and a.get('platform')=='GitHub'])
        resource_temp=resource_path.with_suffix('.tmp');resource_temp.write_text(json.dumps(resource_data,ensure_ascii=False,indent=2));resource_temp.replace(resource_path)
    temp=path.with_suffix('.tmp');temp.write_text(json.dumps(data,ensure_ascii=False,indent=2));temp.replace(path)
    print(json.dumps(report,ensure_ascii=False),flush=True)

if __name__=='__main__':main()

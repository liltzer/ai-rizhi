"""Public model/software discovery. Resource updates are not news publication dates."""
from __future__ import annotations
import concurrent.futures,hashlib,json,os,re,shutil,subprocess,time,urllib.parse,urllib.request
from pathlib import Path
from core import clean,safe_url,stamp
ROOT=Path(__file__).resolve().parents[1]

class JSONClient:
    def __call__(self,url):
        host=urllib.parse.urlsplit(url).hostname
        headers={'User-Agent':'AI-Rizhi/4.0 (public AI resource discovery)','Accept':'application/json'}
        if host=='api.github.com':
            token=os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
            if token:headers['Authorization']='Bearer '+token
            else:
                cli=shutil.which('gh') or next((str(p) for p in (ROOT/'work/gh-cli').glob('*/bin/gh')),None)
                if cli:
                    endpoint=url.removeprefix('https://api.github.com/')
                    result=subprocess.run([cli,'api',endpoint],capture_output=True,timeout=35)
                    if result.returncode:raise RuntimeError('GitHub API unavailable')
                    return json.loads(result.stdout)
        req=urllib.request.Request(url,headers=headers)
        with urllib.request.urlopen(req,timeout=30) as response:raw=response.read(5*1024*1024+1)
        if len(raw)>5*1024*1024:raise ValueError('API response too large')
        return json.loads(raw)

def identifier(prefix,value):return prefix+'-'+hashlib.sha256(value.encode()).hexdigest()[:24]

def license_label(spdx):
    if not spdx or spdx in ('NOASSERTION','other','unknown'):return '自定义或未明确许可，查看原项目'
    if spdx.lower() in ('mit','apache-2.0','gpl-3.0','gpl-3.0-only','agpl-3.0','agpl-3.0-only','bsd-3-clause','bsd-2-clause','mpl-2.0'):return spdx
    return spdx+' · 使用前核对条款'

def github_item(raw,config=None):
    config=config or {};repo=raw.get('full_name','')
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+',repo) or not safe_url(raw.get('html_url')):raise ValueError('Invalid repository')
    if raw.get('private') or raw.get('fork') or raw.get('archived'):return None
    kind=config.get('kind','software');description=clean(raw.get('description'),650)
    item={'id':identifier('github',repo.lower()),'kind':kind,'title':config.get('name') or repo,'originalTitle':repo,'summary':config.get('summary') or description or '该项目未提供简介，请打开仓库说明了解用途。','originalSummary':description,'category':config.get('category','GitHub 软件'),'platform':'GitHub','url':raw['html_url'],'sources':[{'title':repo+' · 项目主页','url':raw['html_url']}],'license':license_label((raw.get('license') or {}).get('spdx_id')),'lastActivityAt':raw.get('pushed_at'),'createdAt':raw.get('created_at'),'checkedAt':stamp(),'stars':int(raw.get('stargazers_count',0)),'language':raw.get('language') or '多语言 / 未标注','tags':(raw.get('topics') or [])[:8],'mode':'resource','curated':bool(config.get('name')),'assetType':config.get('assetType','软件项目' if kind=='software' else '社区流程 / 组件'),'fit':config.get('fit','按仓库说明判断是否适合你的任务。'),'start':config.get('start','先看项目 README、最近提交和 Issues，再决定是否安装。'),'requirements':config.get('requirements','需要的模型、账号、硬件和许可条件以原项目说明为准。'),'verification':'根据项目公开说明与 API 整理，未逐项安装或实测。'}
    return item

def hf_item(raw,config):
    name=raw.get('id') or raw.get('modelId','')
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+',name):return None
    card=raw.get('cardData') or {};license=card.get('license') or next((tag.split(':',1)[1] for tag in raw.get('tags',[]) if tag.startswith('license:')),None)
    if isinstance(license,list):license=', '.join(map(str,license))
    if re.search(r'uncensored|nsfw|porn|erotic',name,re.I):return None
    pipeline=raw.get('pipeline_tag') or config.get('pipeline','unknown')
    tasks={'text-generation':('开源模型','文本生成与对话'),'image-text-to-text':('开源模型','图文理解与对话'),'text-to-image':('图像与设计','根据文字生成图像'),'image-to-image':('图像与设计','图像编辑与转换'),'text-to-video':('视频与动画','根据文字生成视频'),'image-to-video':('视频与动画','根据图像生成视频'),'text-to-speech':('音频与语音','将文字合成为语音'),'text-to-audio':('音频与语音','生成声音'),'automatic-speech-recognition':('音频与语音','将语音转成文字')}
    tasks.update({'image-text-to-video':('视频与动画','图文生成视频'),'token-classification':('数据与训练','文本标注与信息抽取')})
    notes=config.get('notes',{}).get(name,{})
    category,purpose=tasks.get(pipeline,(config.get('category','开源模型'),config.get('purpose','其他模型资料')))
    category=notes.get('category',category);purpose=notes.get('purpose',purpose)
    gated=bool(raw.get('gated'))
    item={'id':identifier('hf',name.lower()),'kind':'model','title':name+' · '+purpose,'originalTitle':name,'summary':('发布者未标注标准任务类型，请查看模型卡确认用途。' if purpose=='其他模型资料' else purpose+'模型。可用版本、模型大小和适用条件见模型卡。'),'category':category,'platform':'Hugging Face','url':'https://huggingface.co/'+name,'sources':[{'title':name+' · 模型卡','url':'https://huggingface.co/'+name}],'license':license_label(license),'lastActivityAt':raw.get('lastModified') or raw.get('last_modified'),'createdAt':raw.get('createdAt'),'checkedAt':stamp(),'downloads':int(raw.get('downloads',0)),'likes':int(raw.get('likes',0)),'pipeline':raw.get('pipeline_tag') or config.get('pipeline','unknown'),'tags':[t for t in raw.get('tags',[]) if not t.startswith(('arxiv:','base_model:','license:','region:'))][:8],'gated':gated,'assetType':'需申请访问的模型' if gated else '公开模型权重','mode':'resource','curated':bool(config.get('author')),'fit':'想试验'+purpose+'能力的用户。','start':'先阅读模型卡中的使用示例、许可和硬件要求，再选择适合的版本。','requirements':'需申请访问。' if gated else '公开权重不代表任意商用；具体许可、依赖和硬件要求以模型卡为准。','verification':'来自 Hugging Face 公开模型元数据与维护者目录；不是本项目的实测排行。'}
    for key in ['summary','fit','start','requirements','assetType']:
        if notes.get(key):item[key]=notes[key]
    if safe_url(notes.get('reference')):item['sources'].append({'title':'官方用途与使用说明','url':notes['reference']})
    return item

def collect_resources(config,previous=None,client=None):
    client=client or JSONClient();items={a['id']:a for a in (previous or {}).get('items',[]) if isinstance(a,dict) and a.get('id')};health=[]
    jobs=[]
    for repo in config.get('github',[]):
        jobs.append(('github',repo,'https://api.github.com/repos/'+repo['repo']))
    for query in config.get('githubSearch',[]):
        jobs.append(('search',query,'https://api.github.com/search/repositories?'+urllib.parse.urlencode({'q':query['query'],'sort':'updated','order':'desc','per_page':12})))
    for query in config.get('huggingface',[]):
        jobs.append(('hf',query,'https://huggingface.co/api/models?'+urllib.parse.urlencode({'filter':query['pipeline'],'sort':'trendingScore','direction':-1,'limit':query.get('limit',8),'full':'true','config':'true'})))
    for query in config.get('hfAuthors',[]):
        jobs.append(('hf',query,'https://huggingface.co/api/models?'+urllib.parse.urlencode({'author':query['author'],'sort':'lastModified','direction':-1,'limit':query.get('limit',4),'full':'true'})))
    def run(job):
        kind,cfg,url=job;raw=client(url)
        if kind=='github':values=[github_item(raw,cfg)]
        elif kind=='search':values=[github_item(row,cfg) for row in raw.get('items',[])]
        else:values=[hf_item(row,{**cfg,'notes':config.get('hfNotes',{})}) for row in raw]
        return [a for a in values if a]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        futures={pool.submit(run,job):job for job in jobs}
        for future in concurrent.futures.as_completed(futures):
            kind,cfg,url=futures[future];name=cfg.get('repo') or cfg.get('pipeline') or cfg.get('author') or cfg.get('query')
            try:
                values=future.result()
                for item in values:
                    old=items.get(item['id'],{})
                    if old.get('curated') and not item.get('curated'):
                        for field in ['title','summary','category','kind','curated','fit','start','requirements','assetType']:item[field]=old[field]
                    if old.get('translation') and old.get('originalSummary')==item.get('originalSummary'):item['translation']=old['translation']
                    items[item['id']]=item
                health.append({'name':name,'ok':True,'count':len(values),'checkedAt':stamp()})
            except Exception as exc:health.append({'name':name,'ok':False,'error':type(exc).__name__,'checkedAt':stamp()})
    valid=[a for a in items.values() if safe_url(a.get('url')) and not re.search(r'uncensored|nsfw|porn|erotic',a.get('originalTitle',''),re.I)]
    # Keep the directory bounded; old resources remain distinguishable from fresh news.
    valid=sorted(valid,key=lambda a:(bool(a.get('curated')),a.get('lastActivityAt') or ''),reverse=True)[:240]
    ok=sum(h['ok'] for h in health)
    return {'format':'ai-rizhi-discovery','version':1,'generatedAt':stamp(),'lastSuccessfulAt':stamp() if ok else (previous or {}).get('lastSuccessfulAt'),'status':{'state':'success' if ok==len(jobs) else 'partial' if ok else 'failed','sourcesOk':ok,'sourcesTotal':len(jobs),'sources':sorted(health,key=lambda a:a['name'])},'items':valid}

def main():
    target=ROOT/'site/discovery.json';previous=json.loads(target.read_text()) if target.exists() else {}
    config=json.loads((ROOT/'scripts/resource_sources.json').read_text());data=collect_resources(config,previous)
    from translation import translation_status
    data['status']['translation']=translation_status([a for a in data['items'] if a.get('platform')=='GitHub' and not a.get('curated')])
    temp=target.with_suffix('.tmp');temp.write_text(json.dumps(data,ensure_ascii=False,indent=2));temp.replace(target)
    print('开源发现：'+str(len(data['items']))+' 项，来源成功 '+str(data['status']['sourcesOk'])+'/'+str(data['status']['sourcesTotal']))
if __name__=='__main__':main()

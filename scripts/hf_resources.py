"""Public Hugging Face model cards, Spaces, and actual ComfyUI JSON files."""
from __future__ import annotations
import concurrent.futures,hashlib,json,re,urllib.parse,urllib.request
from pathlib import Path
from html.parser import HTMLParser
from core import stamp,safe_url

CACHE=Path(__file__).resolve().parents[1]/'work/hf-cards'
REPO=re.compile(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+')
def public_text(url,limit=2500000):
    if urllib.parse.urlsplit(url).hostname!='huggingface.co':raise ValueError('Not a Hub URL')
    request=urllib.request.Request(url,headers={'User-Agent':'AI-Rizhi public model-card reader'})
    with urllib.request.urlopen(request,timeout=25) as response:data=response.read(limit+1)
    if len(data)>limit:raise ValueError('Model card too large')
    return data.decode('utf-8')

class PublicCardParser(HTMLParser):
    # Read only the public model-card body, excluding login prompts and scripts.
    def __init__(self):super().__init__(convert_charrefs=True);self.depth=0;self.parts=[];self.skip=0
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if not self.depth:
            if 'model-card-content' not in attrs.get('class','').split():return
            self.depth=1;return
        if tag not in ('img','br','hr','input','meta','link','source','wbr'):self.depth+=1
        if tag in ('script','style'):self.skip+=1
        if tag in ('p','div','li','h1','h2','h3','h4','tr','pre','br'):self.parts.append('\n')
    def handle_endtag(self,tag):
        if not self.depth:return
        if tag in ('script','style') and self.skip:self.skip-=1
        if tag not in ('img','br','hr','input','meta','link','source','wbr'):self.depth-=1
        if tag in ('p','div','li','h1','h2','h3','h4','tr','pre'):self.parts.append('\n')
    def handle_data(self,data):
        if self.depth and not self.skip:self.parts.append(data)

def public_card_text(html):
    parser=PublicCardParser();parser.feed(html);text=''.join(parser.parts).strip()
    if len(text)<100:raise ValueError('Public model card body not found')
    return re.sub(r'\n\s*\n+', '\n\n', re.sub(r'[ \t]+',' ',text))

def read_card(name,text_client=public_text):
    try:return text_client('https://huggingface.co/'+name+'/raw/main/README.md')
    except Exception:
        # A gated weight repo may still publish its model card on the public page.
        return public_card_text(text_client('https://huggingface.co/'+name))

def excerpt(card):
    card=re.sub(r'\n\s*\n+','\n\n',re.sub(r'[ \t]+',' ',card))
    card=re.sub(r'^---\s*\n.*?\n---\s*\n','',card,count=1,flags=re.S)
    card=re.sub(r'<table\b.*?</table>|<script\b.*?</script>|<style\b.*?</style>',' ',card,flags=re.S|re.I)
    card=re.sub(r'!\[[^\]]*\]\([^)]*\)|<[^>]*>',' ',card)
    # Keep the overview plus explicit usage/format/requirements sections, not benchmark tables.
    chunks=[]
    for heading,body in re.findall(r'(?:^|\n)(#{1,4}[^\n]*)\n([\s\S]*?)(?=\n#{1,4} |\Z)',card):
        if re.search(r'overview|introduction|highlight|feature|quick.?start|usage|requirement|memory|deploy|variant|limitations|模型|简介|特点|部署|使用|硬件',heading,re.I):
            body=re.sub(r'```[\s\S]*?```',' [代码示例见模型卡] ',body);body='\n'.join(line for line in body.splitlines() if not re.match(r'\s*\|',line))
            chunks.append(heading+'\n'+body[:2300])
    intro=re.sub(r'```[\s\S]*?```',' ',card[:6500]);intro='\n'.join(line for line in intro.splitlines() if not re.match(r'\s*\|',line))
    return (intro[:4800]+'\n'+'\n'.join(chunks)[:11000]).strip()[:15000]

def facts(meta):
    result=[];total=(meta.get('safetensors') or {}).get('total');config=meta.get('config') or {};card=meta.get('cardData') or {}
    if isinstance(total,(int,float)) and total>0:result.append({'label':'仓库参数统计','value':f'{total/1e9:.2f}B' if total>=1e9 else f'{total/1e6:.1f}M'})
    files=[s.get('rfilename','') for s in meta.get('siblings',[])];formats=[]
    for suffix,label in [('.gguf','GGUF'),('.safetensors','Safetensors'),('.onnx','ONNX'),('.bin','PyTorch BIN')]:
        if any(f.endswith(suffix) for f in files):formats.append(label)
    if formats:result.append({'label':'权重格式','value':' / '.join(formats)})
    if meta.get('library_name'):result.append({'label':'适配框架','value':meta['library_name']})
    languages=card.get('language') or [];languages=[languages] if isinstance(languages,str) else languages
    if languages:result.append({'label':'标注语言','value':' / '.join(languages[:8])})
    base=card.get('base_model');base=[base] if isinstance(base,str) else base
    if isinstance(base,list) and base:result.append({'label':'基于模型','value':' / '.join(str(v) for v in base[:2])})
    if config.get('model_type'):result.append({'label':'架构标记','value':str(config['model_type'])})
    return result

def model_details(item,meta,card):
    out=dict(item);sha=meta.get('sha') or hashlib.sha256(card.encode()).hexdigest()
    digest=hashlib.sha256(card.encode()).hexdigest();CACHE.mkdir(parents=True,exist_ok=True);(CACHE/(digest+'.txt')).write_text(excerpt(card))
    out.pop('cardExcerpt',None);out.update(cardSha=sha,cardHash=digest,modelFacts=facts(meta))
    out['detailStatus']='available';out['cardCheckedAt']=stamp()
    return out

def space_item(meta,cfg):
    from discover import identifier,license_label
    name=meta.get('id','')
    if not REPO.fullmatch(name) or meta.get('private') or meta.get('disabled'):return None
    card=meta.get('cardData') or {};runtime=meta.get('runtime') or {};url='https://huggingface.co/spaces/'+name
    return {'id':identifier('hf-space',name.lower()),'kind':'workflow','resourceType':'space','title':cfg['name'],'originalTitle':name,'summary':cfg['summary'],'originalSummary':card.get('short_description') or cfg['summary'],'category':cfg['category'],'platform':'Hugging Face','url':url,'sources':[{'title':name+' · Space 与代码','url':url}],'license':license_label(card.get('license'))+'（Space 代码，模型许可另看模型卡）','lastActivityAt':meta.get('lastModified'),'checkedAt':stamp(),'likes':int(meta.get('likes',0)),'tags':['HF Spaces','在线体验',meta.get('sdk') or '应用'],'assetType':'在线演示 · HF Space','fit':cfg['fit'],'start':cfg['start'],'requirements':cfg.get('requirements','在浏览器打开 Space。运行可能需要登录、排队或等待唤醒；以 Space 当前提示为准。'),'mode':'resource','curated':True,'runtimeStage':runtime.get('stage','UNKNOWN'),'relatedModels':[m for m in meta.get('models',[]) if REPO.fullmatch(m)],'verification':'已核对公开 Space 元数据；在线状态会变化，未逐项执行生成。'}

def workflow_item(meta,body,cfg):
    from discover import identifier,license_label
    name=cfg['repo'];path=cfg['path']
    if meta.get('private') or not REPO.fullmatch(name) or '..' in path.split('/'):return None
    if not any(f.get('rfilename')==path for f in meta.get('siblings',[])):raise ValueError('Workflow file absent')
    graph=json.loads(body)
    # Only advertise downloadable node graphs, never arbitrary JSON/config as a workflow.
    ui=isinstance(graph,dict) and isinstance(graph.get('nodes'),list) and bool(graph['nodes']) and isinstance(graph.get('links'),list)
    api=isinstance(graph,dict) and bool(graph) and all(isinstance(v,dict) and isinstance(v.get('class_type'),str) and isinstance(v.get('inputs'),dict) for v in graph.values())
    if not(ui or api):raise ValueError('Not a ComfyUI workflow')
    url='https://huggingface.co/'+name+'/blob/main/'+urllib.parse.quote(path,safe='/');download='https://huggingface.co/'+name+'/resolve/main/'+urllib.parse.quote(path,safe='/')
    types=sorted({str(n.get('type','')) for n in graph['nodes']} if ui else {v['class_type'] for v in graph.values()})
    return {'id':identifier('hf-workflow',name+'/'+path),'kind':'workflow','resourceType':'workflow-file','title':cfg['name'],'originalTitle':name+'/'+path,'summary':cfg['summary'],'category':'ComfyUI 工作流','platform':'Hugging Face','url':url,'downloadURL':download,'sources':[{'title':'工作流 JSON 原文件','url':url},{'title':'配套模型与作者说明','url':'https://huggingface.co/'+name}],'license':license_label((meta.get('cardData') or {}).get('license')),'lastActivityAt':meta.get('lastModified'),'checkedAt':stamp(),'tags':['ComfyUI','工作流 JSON'],'assetType':'可下载工作流 · JSON','fit':cfg['fit'],'start':cfg['start'],'requirements':cfg['requirements'],'relatedModels':[name],'nodeTypes':types[:40],'nodeCount':len(graph['nodes']) if ui else len(graph),'workflowFormat':'ComfyUI UI JSON' if ui else 'ComfyUI API JSON','mode':'resource','curated':True,'verification':'已读取 JSON 并核对节点图结构；尚未在本机安装模型运行。'}

def apply_reviews(items):
    path=Path(__file__).with_name('hf_reviews.json');reviews=json.loads(path.read_text()) if path.exists() else {}
    def normalize(value):return re.sub(r'\s+',' ',re.sub(r'[*_`#]','',value)).strip().lower()
    for item in items:
        review=reviews.get(item.get('originalTitle',''),{});matched=review.get('cardHash') and review['cardHash']==item.get('cardHash')
        # A documentation-only revision need not invalidate independently reviewed facts.
        # Carry the review forward only while every selected supporting statement remains.
        evidence=review.get('evidence') or [];cache=CACHE/(str(item.get('cardHash',''))+'.txt')
        if not matched and evidence and cache.exists():
            source=normalize(cache.read_text());matched=all(normalize(text) in source for text in evidence)
        if matched:
            item['profile']={**review,'reviewSourceCardHash':review['cardHash'],'cardHash':item['cardHash']}
            for ref in review.get('references',[]):
                if safe_url(ref.get('url')) and not any(s.get('url')==ref['url'] for s in item['sources']):item['sources'].append(ref)
    return items

def extend_catalog(data,config,previous,client,text_client=public_text):
    items={a['id']:a for a in data['items']};old={a['id']:a for a in previous.get('items',[])};health=[]
    def model(item):
        meta=client('https://huggingface.co/api/models/'+item['originalTitle']);prior=old.get(item['id'],{})
        if meta.get('sha') and prior.get('cardSha')==meta['sha'] and prior.get('cardHash') and ((CACHE/(prior['cardHash']+'.txt')).exists() or prior.get('profile',{}).get('cardHash')==prior['cardHash']):
            out=dict(item)
            for field in ['cardSha','cardHash','modelFacts','profile','detailStatus','cardCheckedAt']:
                if field in prior:out[field]=prior[field]
            return out
        try:card=read_card(item['originalTitle'],text_client)
        except Exception:
            out={**item,'modelFacts':facts(meta),'detailStatus':'unavailable','cardCheckedAt':stamp()}
            for field in ['cardSha','cardHash','profile']:
                if field in prior:out[field]=prior[field]
            if prior.get('profile'):out['detailStatus']='stale'
            return out
        return model_details(item,meta,card)
    jobs=[]
    if config.get('hfDetails'):
        jobs.extend(('model',a,lambda a=a:model(a)) for a in data['items'] if a.get('platform')=='Hugging Face' and a.get('kind')=='model')
    for cfg in config.get('hfSpaces',[]):jobs.append(('space',cfg,lambda cfg=cfg:space_item(client('https://huggingface.co/api/spaces/'+cfg['repo']),cfg)))
    for cfg in config.get('hfWorkflows',[]):
        def workflow(cfg=cfg):return workflow_item(client('https://huggingface.co/api/models/'+cfg['repo']),text_client('https://huggingface.co/'+cfg['repo']+'/raw/main/'+urllib.parse.quote(cfg['path'],safe='/')),cfg)
        jobs.append(('workflow-file',cfg,workflow))
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        futures={pool.submit(job[2]):job for job in jobs}
        for future in concurrent.futures.as_completed(futures):
            kind,source,_=futures[future];name=source.get('repo') or source.get('originalTitle')
            try:
                item=future.result()
                if item:items[item['id']]=item
                health.append({'name':name,'type':kind,'ok':not item or item.get('detailStatus') not in ('stale','unavailable'),'checkedAt':stamp()})
            except Exception as exc:
                if kind=='model':
                    item=dict(source);prior=old.get(item['id'],{})
                    # Preserve a previous complete card on temporary Hub failures.
                    for field in ['cardSha','cardHash','modelFacts','profile','cardCheckedAt']:
                        if field in prior:item[field]=prior[field]
                    item['detailStatus']='stale' if prior.get('cardHash') else 'unavailable';items[item['id']]=item
                health.append({'name':name,'type':kind,'ok':False,'error':type(exc).__name__,'checkedAt':stamp()})
    data['items']=apply_reviews(list(items.values()));data['status']['huggingfaceDetails']={'ok':sum(v['ok'] for v in health),'total':len(health),'sources':health}
    return data

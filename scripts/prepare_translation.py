"""Download the pinned, data-only translation model and verify every file."""
import hashlib,json,os,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MODEL_DIR=ROOT/'work'/'nllb-ct2'

def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()

def prepare():
    metadata=json.loads((ROOT/'scripts/translation-model.json').read_text())
    MODEL_DIR.mkdir(parents=True,exist_ok=True)
    for item in metadata['files']:
        target=MODEL_DIR/item['name']
        if target.exists() and digest(target)==item['sha256']:continue
        url='https://huggingface.co/'+metadata['convertedRepository']+'/resolve/'+metadata['revision']+'/'+item['name']
        part=target.with_suffix(target.suffix+'.part');size=0
        try:
            with urllib.request.urlopen(url,timeout=60) as response,part.open('wb') as f:
                while True:
                    block=response.read(1024*1024)
                    if not block:break
                    size+=len(block)
                    if size>700*1024*1024:raise ValueError('Model file exceeded maximum size')
                    f.write(block)
            if digest(part)!=item['sha256']:raise ValueError('Model checksum mismatch')
            part.replace(target)
        finally:
            if part.exists():part.unlink()
        print('中文翻译模型文件已就绪：'+item['name'],flush=True)
    return MODEL_DIR
if __name__=='__main__':prepare()

"""Pinned official Qwen GGUF + official llama.cpp, no third-party model code."""
import hashlib,json,platform,tarfile,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MODEL_DIR=ROOT/'work/qwen'
def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(4*1024*1024),b''):h.update(block)
    return h.hexdigest()

def download(url,target,sha,max_bytes):
    if target.exists() and digest(target)==sha:return
    part=target.with_suffix(target.suffix+'.download');size=0
    try:
        req=urllib.request.Request(url,headers={'User-Agent':'AI-Rizhi/4.0'})
        with urllib.request.urlopen(req,timeout=90) as response,part.open('wb') as f:
            while True:
                block=response.read(2*1024*1024)
                if not block:break
                size+=len(block)
                if size>max_bytes:raise ValueError('Download exceeded size bound')
                f.write(block)
        if digest(part)!=sha:raise ValueError('Model/runtime checksum mismatch')
        part.replace(target)
    finally:
        if part.exists():part.unlink()

def prepare():
    metadata=json.loads((ROOT/'scripts/translation-model.json').read_text());MODEL_DIR.mkdir(parents=True,exist_ok=True)
    model=MODEL_DIR/metadata['file']
    download('https://huggingface.co/'+metadata['model']+'/resolve/'+metadata['revision']+'/'+metadata['file'],model,metadata['sha256'],metadata['bytes']+1)
    key=platform.system()+'-'+platform.machine();runtime=metadata['runtime'].get(key)
    if not runtime:raise RuntimeError('Translation runtime requires Apple Silicon macOS or Linux x64')
    archive=MODEL_DIR/runtime['file'];download(runtime['url'],archive,runtime['sha256'],500*1024*1024)
    destination=MODEL_DIR/'runtime';marker=destination/('.verified-'+runtime['sha256'])
    if not marker.exists():
        destination.mkdir(parents=True,exist_ok=True)
        with tarfile.open(archive) as tar:tar.extractall(destination,filter='data')
        marker.write_text('Official release hash verified\n')
    binary=next(destination.glob('**/llama-server'),None)
    if not binary:raise RuntimeError('llama-server missing from official archive')
    return model,binary
if __name__=='__main__':
    prepare();print('Qwen 文字模型与官方推理运行包校验通过。')

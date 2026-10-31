"""GitHub Actions collector: only public news/state enters the published JSON."""
import json,os,sys,tempfile
from pathlib import Path
from core import Store,Updater,stamp
ROOT=Path(__file__).resolve().parents[1]
LIBRARY=ROOT/'site/library.json'
def main():
 previous=json.loads(LIBRARY.read_text()) if LIBRARY.exists() else {'format':'ai-rizhi-independent','version':2,'articles':[]}
 with tempfile.TemporaryDirectory() as temp:
  store=Store(Path(temp)/'news.sqlite3');store.import_backup(previous)
  oldstatus=previous.get('status',{})
  for field,key in [('lastCheckedAt','lastCheckedAt'),('lastSuccessfulAt','lastSuccessfulAt'),('lastContentAt','lastContentAt'),('sources','sourceHealth')]:
   if oldstatus.get(field) is not None:store.set(key,oldstatus[field])
  updater=Updater(store,json.loads((ROOT/'sources.json').read_text()))
  updater.lock.acquire()
  try:result=updater.run()
  finally:updater.lock.release()
  status=updater.status();status.update(running=False,intervalMinutes=30,hosting='github-pages',collectionMode='scheduled-workflow')
  data={**store.export(),'status':status}
  target=LIBRARY.with_suffix('.tmp');target.write_text(json.dumps(data,ensure_ascii=False,indent=2));target.replace(LIBRARY)
  report=f"新闻检查：{result['status']}，新增 {result['added']} 条，来源 {result['sourcesOk']}/{result['sourcesTotal']} 成功。"
  print(report)
  if os.environ.get('GITHUB_STEP_SUMMARY'):
   with open(os.environ['GITHUB_STEP_SUMMARY'],'a') as f:
    f.write('## AI日知采集结果\n\n'+report+'\n\n检查时间：'+stamp()+'\n\n')
    for source in status['sources']:f.write('- '+source['name']+'：'+('成功' if source['ok'] else source.get('error','失败'))+'\n')
  # Persist failure status and publish it first; workflow explicitly fails after publishing.
  if os.environ.get('GITHUB_OUTPUT'):
   with open(os.environ['GITHUB_OUTPUT'],'a') as f:f.write('collection_failed='+str(result['status']=='failed').lower()+'\n')
 return result
if __name__=='__main__':main()

"""Deploy the uploaded Pages artifact through GitHub's documented REST API.

Uses only the current workflow's short-lived token and OIDC identity. Never prints
or persists either credential. The REST artifact list avoids a Results SDK listing
failure observed in deploy-pages on this repository.
"""
import json, os, time, urllib.parse, urllib.request

def main():
    api=os.environ.get('GITHUB_API_URL','https://api.github.com').rstrip('/')
    repository=os.environ['GITHUB_REPOSITORY'];token=os.environ['GH_TOKEN']
    def call(url,payload=None,auth=token):
        if urllib.parse.urlsplit(url).netloc != urllib.parse.urlsplit(api).netloc:raise ValueError('Unexpected GitHub API host')
        req=urllib.request.Request(url,data=json.dumps(payload).encode() if payload is not None else None,headers={'Authorization':'Bearer '+auth,'Accept':'application/vnd.github+json','Content-Type':'application/json'})
        with urllib.request.urlopen(req,timeout=30) as r:return json.load(r)
    url=api+'/repos/'+repository+'/actions/runs/'+os.environ['GITHUB_RUN_ID']+'/artifacts'
    for _ in range(15):
        artifacts=call(url).get('artifacts',[])
        artifact=next((a for a in artifacts if a['name']=='github-pages' and not a.get('expired')),None)
        if artifact:break
        time.sleep(2)
    else:raise RuntimeError('Pages artifact not visible')
    req=urllib.request.Request(os.environ['ACTIONS_ID_TOKEN_REQUEST_URL'],headers={'Authorization':'Bearer '+os.environ['ACTIONS_ID_TOKEN_REQUEST_TOKEN']})
    with urllib.request.urlopen(req,timeout=30) as r:identity=json.load(r)['value']
    deployment=call(api+'/repos/'+repository+'/pages/deployments',{'artifact_id':artifact['id'],'pages_build_version':os.environ['GITHUB_SHA'],'oidc_token':identity})
    page=deployment.get('page_url','')
    if os.environ.get('GITHUB_OUTPUT'):
        with open(os.environ['GITHUB_OUTPUT'],'a') as f:f.write('page_url='+page+'\n')
    status_url=deployment.get('status_url') or api+'/repos/'+repository+'/pages/deployments/'+str(deployment['id'])
    for _ in range(80):
        state=call(status_url).get('status')
        if state in ('succeed','succeeded','success','built'):
            print('网站发布成功：'+page);return
        if state in ('errored','failed','failure','cancelled','canceled'):raise RuntimeError('Pages deployment failed: '+state)
        print('等待网站发布：'+str(state),flush=True);time.sleep(3)
    raise TimeoutError('Pages deployment status did not complete')

if __name__=='__main__':main()

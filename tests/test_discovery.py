import copy,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from discover import collect_resources,github_item,hf_item

class DiscoveryTests(unittest.TestCase):
    def repo(self):return {'full_name':'example/tool','html_url':'https://github.com/example/tool','description':'A workflow editor','pushed_at':'2026-11-20T12:00:00Z','license':{'spdx_id':'MIT'},'stargazers_count':12}
    def test_failure_preserves_previous_directory_and_timestamp(self):
        item=github_item(self.repo(),{'name':'流程编辑器','kind':'workflow'})
        old={'items':[item],'lastSuccessfulAt':'2026-11-20T13:00:00Z'};snapshot=copy.deepcopy(old)
        def failed(url):raise TimeoutError()
        result=collect_resources({'github':[{'repo':'example/tool'}]},old,failed)
        self.assertEqual(result['items'],[item]);self.assertEqual(result['status']['state'],'failed');self.assertEqual(result['lastSuccessfulAt'],old['lastSuccessfulAt']);self.assertEqual(old,snapshot)
    def test_curated_description_survives_search_result(self):
        old=github_item(self.repo(),{'name':'流程编辑器','summary':'把工作步骤连起来。','kind':'workflow'})
        result=collect_resources({'githubSearch':[{'query':'topic:workflow'}]},{'items':[old]},lambda url:{'items':[self.repo()]})
        item=result['items'][0];self.assertEqual(item['summary'],old['summary']);self.assertEqual(item['kind'],'workflow');self.assertEqual(item['lastActivityAt'],'2026-11-20T12:00:00Z');self.assertNotIn('eventDate',item)
    def test_private_forks_and_archived_not_listed(self):
        for key in ('private','fork','archived'):self.assertIsNone(github_item({**self.repo(),key:True}))
    def test_model_license_and_gated_access_are_distinct(self):
        a=hf_item({'id':'example/model','pipeline_tag':'text-to-image','gated':'manual','tags':['license:custom-research']},{})
        self.assertEqual(a['kind'],'model');self.assertTrue(a['gated']);self.assertIn('申请',a['assetType']);self.assertIn('custom-research',a['license']);self.assertNotIn('eventDate',a)

if __name__=='__main__':unittest.main()

import copy,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from hf_resources import extend_catalog,facts,model_details,space_item,workflow_item,public_card_text
from discover import hf_item,collect_resources

class HubTests(unittest.TestCase):
 def test_public_card_fallback_excludes_auth_prompt_and_footer(self):
  content='<div class="prose">Login to share information</div><div class="model-card-content prose"><h2>Model overview</h2><p>'+('Public model facts. '*12)+'</p><script>ignore-this()</script></div><footer>Download advertising</footer>'
  text=public_card_text(content);self.assertIn('Public model facts',text);self.assertNotIn('Login',text);self.assertNotIn('ignore-this',text);self.assertNotIn('advertising',text)
  with self.assertRaises(ValueError):public_card_text('<div>Sign in</div>')
 def test_workflow_requires_real_graph_and_matching_repository_file(self):
  cfg={'repo':'a/model','path':'examples/test.json','name':'节点示例','summary':'像素图流程','fit':'创作者','start':'导入节点图','requirements':'先准备模型'};meta={'siblings':[{'rfilename':cfg['path']}],'cardData':{'license':'apache-2.0'}}
  a=workflow_item(meta,json.dumps({'nodes':[{'type':'Loader'},{'type':'Sampler'}],'links':[[1,0,0,1,0,'MODEL']]}),cfg)
  self.assertEqual(a['nodeCount'],2);self.assertEqual(a['resourceType'],'workflow-file');self.assertIn('/resolve/main/examples/test.json',a['downloadURL'])
  with self.assertRaises(ValueError):workflow_item(meta,'{"model_type":"foo"}',cfg)
  with self.assertRaises(ValueError):workflow_item({'siblings':[]},'{"nodes":[{}],"links":[]}',cfg)
 def test_private_spaces_are_excluded_and_runtime_is_not_a_free_promise(self):
  cfg={'name':'语音体验','category':'音频与语音','summary':'输入文字试听语音','fit':'创作者','start':'打开体验'}
  self.assertIsNone(space_item({'id':'a/space','private':True},cfg))
  a=space_item({'id':'a/space','runtime':{'stage':'RUNTIME_ERROR'},'cardData':{'license':'mit'}},cfg)
  self.assertEqual(a['runtimeStage'],'RUNTIME_ERROR');self.assertEqual(a['kind'],'workflow');self.assertIn('排队',a['requirements']);self.assertIn('模型许可另看',a['license']);self.assertNotIn('downloadURL',a)
 def test_raw_model_cards_are_local_and_failed_refresh_keeps_verified_profile(self):
  meta={'id':'a/model','sha':'abc','safetensors':{'total':2230000000},'siblings':[{'rfilename':'weights.gguf'}]};a=hf_item(meta,{})
  with tempfile.TemporaryDirectory() as d,patch('hf_resources.CACHE',Path(d)):
   old=model_details(a,meta,'# Model\nA small model for searching images.');old['profile']={'cardHash':old['cardHash'],'summary':'图像检索模型'}
   self.assertNotIn('cardExcerpt',old);self.assertEqual(old['modelFacts'][0]['value'],'2.23B');snapshot=copy.deepcopy(old)
   def client(url):raise TimeoutError()
   data={'items':[a],'status':{}};out=extend_catalog(data,{'hfDetails':True},{'items':[old]},client)
   self.assertEqual(out['items'][0]['profile'],old['profile']);self.assertEqual(old,snapshot);self.assertEqual(out['status']['huggingfaceDetails']['ok'],0)
 def test_existing_card_sha_uses_cache_and_reuses_profile(self):
  meta={'id':'a/model','sha':'abc'};a=hf_item(meta,{})
  with tempfile.TemporaryDirectory() as d,patch('hf_resources.CACHE',Path(d)):
   old=model_details(a,meta,'# Model\nModel card.');old['profile']={'cardHash':old['cardHash'],'summary':'模型说明'}
   def forbidden(url):raise AssertionError('Card should be cached')
   out=extend_catalog({'items':[a],'status':{}},{'hfDetails':True},{'items':[old]},lambda url:meta,forbidden)
   self.assertEqual(out['items'][0]['profile'],old['profile']);self.assertEqual(out['status']['huggingfaceDetails']['ok'],1)
 def test_explicit_models_keep_their_metadata_and_are_curated(self):
  a=collect_resources({'hfModels':[{'repo':'a/model','curated':True}]},client=lambda url:{'id':'a/model','downloads':42,'cardData':{'pipeline_tag':'image-text-to-text'}})['items'][0]
  self.assertEqual(a['pipeline'],'image-text-to-text');self.assertEqual(a['downloads'],42);self.assertTrue(a['curated'])
if __name__=='__main__':unittest.main()

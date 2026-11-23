import copy,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from editor import validate_edits
from translation import translate_articles,translated

class EditorTests(unittest.TestCase):
    def source(self):return {'id':'news-a','title':'Gemini 4.0 update','summary':'Gemini 4.0 can read images.'}
    def draft(self):return {'id':'news-a','title':'Gemini 4.0 支持读图','summary':'Gemini 4.0 可以读取图片。','simple':'把图片交给模型来阅读。'}
    def test_preserves_ids_names_and_numbers(self):
        self.assertEqual(validate_edits([self.source()],[self.draft()])[0]['title'],self.draft()['title'])
        for field,value in [('id','other'),('title','Gemini 5.0 支持读图'),('summary','Gemini 4.0 即将推出后续版本。'),('simple','能够处理 99 张图。')]:
            a=self.draft();a[field]=value
            with self.assertRaises(ValueError):validate_edits([self.source()],[a])
    def test_rejects_dropped_product_and_duplicate_rows(self):
        a=self.draft();a['title']='模型支持读图';a['summary']='模型可以读图片。'
        with self.assertRaises(ValueError):validate_edits([self.source()],[a])
        with self.assertRaises(ValueError):validate_edits([self.source(),{**self.source(),'id':'news-b'}],[self.draft(),self.draft()])
    def test_company_name_alone_never_triggers_specific_story_correction(self):
        source={'id':'news-a','title':'Sumitomo Life changes its office','summary':'The office has moved.'};draft={'id':'news-a','title':'住友生命保险搬迁办公室','summary':'办公室搬迁。','simple':'办公地点变了。'}
        self.assertEqual(validate_edits([source],[draft])[0]['summary'],'办公室搬迁。')
    def test_missing_summary_not_invented(self):
        a={**self.source(),'summary':'该来源未提供摘要，请打开原文阅读。'}
        result=validate_edits([a],[self.draft()])[0];self.assertEqual(result['summary'],a['summary']);self.assertEqual(result['simple'],'')
    def test_bad_batch_isolated_and_original_unchanged(self):
        articles=[self.source(),{**self.source(),'id':'news-b'}];original=copy.deepcopy(articles)
        class Editor:
            def edit(self,rows):
                if len(rows)>1:raise ValueError('Bad alignment')
                return [{'id':rows[0]['id'],'title':'Gemini 4.0 支持读图','summary':'Gemini 4.0 可以读取图片。','simple':'可以阅读图片。'}]
        result=translate_articles(articles,Editor());self.assertEqual(result['translated'],2)
        for a,b in zip(articles,original):self.assertEqual(a['title'],b['title']);self.assertEqual(a['summary'],b['summary']);self.assertTrue(translated(a))
    def test_long_english_product_name_does_not_hide_valid_chinese(self):
        a={'id':'news-a','title':'Introducing Transformers and Diffusers','summary':'Transformers and Diffusers receive updates.'}
        class Editor:
            def edit(self,rows):return [{'id':'news-a','title':'Transformers 与 Diffusers 更新','summary':'Transformers 与 Diffusers 更新。','simple':'两个项目有更新。'}]
        translate_articles([a],Editor());self.assertTrue(translated(a))

if __name__=='__main__':unittest.main()

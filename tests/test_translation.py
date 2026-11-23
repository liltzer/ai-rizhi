import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from translation import needs_chinese,source_hash,translated,translate_articles,translation_status,terminology,WebTranslator

class TranslationTests(unittest.TestCase):
    def article(self):return {'id':'one','title':'A new model for coding','summary':'The model can write code.','eventDate':'2026-11-23'}
    def test_translate_preserves_original_and_idempotent(self):
        a=self.article();original=dict(a)
        result=translate_articles([a],lambda texts:['用于编程的新模型','这款模型可以编写代码。'])
        self.assertEqual(result['translated'],1);self.assertEqual(a['title'],original['title']);self.assertEqual(a['summary'],original['summary']);self.assertTrue(translated(a))
        translate_articles([a],lambda texts:self.fail('cached item translated twice'))
        a['summary']='Changed summary';self.assertFalse(translated(a))
    def test_rejects_english_and_keeps_existing_content(self):
        a=self.article();report=translate_articles([a],lambda texts:texts)
        self.assertEqual(report['pending'],1);self.assertNotIn('translation',a)
    def test_partial_chinese_only_translates_foreign_field(self):
        a=self.article();a['title']='编程模型有了新变化'
        translate_articles([a],lambda texts:['这款模型可以编写代码。'])
        self.assertEqual(a['translation']['title'],a['title']);self.assertTrue(translated(a))
    def test_native_and_bad_empty_result(self):
        self.assertFalse(needs_chinese('Gemini 新版本支持中文'))
        self.assertFalse(needs_chinese(''))
        self.assertTrue(needs_chinese('Introducing GPT-5'))
        a=self.article();translate_articles([a],lambda texts:[''])
        self.assertEqual(translation_status([a])['translated'],0)

    def test_domain_terms_and_repeated_gibberish(self):
        self.assertEqual(terminology('Inside the Codex sandbox','法典沙盒内部'),'Codex沙盒内部')
        self.assertEqual(terminology('Introducing harness adapters','推出线束适配器'),'推出运行框架适配器')
        a=self.article();report=translate_articles([a],lambda texts:['重复重复重复重复重复重复重复','模型可以写代码'])
        self.assertEqual(report['translated'],0)

    def test_batch_alignment_and_source_context(self):
        translator=WebTranslator()
        translator.translate=lambda text:'法典沙盒\n普通法典'
        self.assertEqual(translator.batch(['Codex sandbox','Ordinary statute']),['Codex沙盒','普通法典'])
        translator.translate=lambda text:'合并成一段'
        with self.assertRaises(ValueError):translator.batch(['One title','One summary'])

if __name__=='__main__':unittest.main()

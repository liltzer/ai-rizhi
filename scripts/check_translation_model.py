"""A real-model check; fixtures never enter the public news library."""
from translation import LocalTranslator
engine=LocalTranslator()
try:
    articles=[{'id':'check-code','title':'Codex helps people write code.','summary':'Codex can help a team write and review code.'},
              {'id':'check-version','title':'Gemini 4.0 update','summary':'Gemini 4.0 can read text and images.'}]
    output=engine.edit(articles)
    assert len(output)==2 and all(any('\u3400'<=c<='\u9fff' for c in a['summary']) for a in output)
    assert 'Codex' in output[0]['title']+output[0]['summary']
    assert 'Gemini' in output[1]['title'] and '4.0' in output[1]['title']+output[1]['summary']
    print('免费 Qwen 文字模型实测通过：中文输出、产品名和版本号保留。')
finally:
    engine.close()

"""Small real-model smoke test; no sample is inserted into the news library."""
from translation import LocalTranslator, needs_chinese
engine=LocalTranslator()
source=['The model can read text and images.','Codex helps people write code.','GPT-6.2 is a model.']
output=engine(source)
assert len(output)==len(source) and all(not needs_chinese(text) and text.strip() for text in output)
assert 'Codex' in output[1] and '6.2' in output[2]
print('离线模型实测通过：中文输出、产品名和版本号保留。')

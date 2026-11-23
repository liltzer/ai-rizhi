import { Window } from '../work/domqa/node_modules/happy-dom/lib/index.js';
import fs from 'node:fs';import assert from 'node:assert/strict';
const w=new Window();w.eval(fs.readFileSync(new URL('../site/catalog.js',import.meta.url),'utf8'));const c=w.RizhiCatalog;
const model=(id,name)=>({id,kind:'model',originalTitle:name,summary:'generic'});
const base=model('base','tencent/WePocketModel1.0-2B'),gguf=model('gguf','tencent/WePocketModel1.0-2B-GGUF'),larger=model('large','tencent/WePocketModel1.0-4B');
const grouped=c.group([gguf,base,larger]);assert.equal(grouped.length,2,'parameter sizes remain distinct');assert.equal(grouped[0].id,'base');assert.equal(grouped[0].variants.length,2);assert.equal(base.variants,undefined,'raw records are preserved');
const a={...base,cardHash:'changed',profile:{cardHash:'old',purpose:'old',summary:'outdated'}};assert.equal(c.profile(a),null,'changed model cards cannot show a stale AI profile');a.profile.cardHash='changed';assert.equal(c.text(a).summary,'outdated');assert.match(c.state({runtimeStage:'RUNTIME_ERROR'}),/异常/);assert.equal(c.type({kind:'workflow',resourceType:'space'}),'space');assert.equal(c.type({kind:'workflow',resourceType:'workflow-file'}),'workflow-file');
console.log('PASS: family formats grouped without merging parameter sizes; immutable inputs; model-card hash invalidation; Spaces status and JSON workflow types.');w.close();

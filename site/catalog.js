'use strict';
(() => {
 function profile(a){return a.kind==='model'&&a.profile?.cardHash&&a.profile.cardHash===a.cardHash?a.profile:null;}
 function text(a){const p=profile(a);return p?{...a,title:a.originalTitle+' · '+p.purpose,summary:p.summary}:a;}
 function family(a){if(a.kind!=='model')return a.id;return (a.originalTitle||a.title).replace(/-(?:GGUF|FP8|onnx|Diffusers)$/i,'').toLowerCase();}
 function group(items){const groups=new Map();for(const a of items){const key=family(a);if(!groups.has(key))groups.set(key,[]);groups.get(key).push(a);}return [...groups.values()].map(variants=>{if(variants.length===1)return variants[0];const main=variants.find(a=>!/-GGUF$|-FP8$|-onnx$|-Diffusers$/i.test(a.originalTitle))||variants[0];return {...main,variants:[...variants].sort((a,b)=>a.id===main.id?-1:b.id===main.id?1:0)};});}
 function type(a){return a.resourceType||(a.kind==='model'?'weights':a.kind==='workflow'?'nodes':'software');}
 function state(a){return ({RUNNING:'服务运行中',SLEEPING:'休眠中，打开后等待唤醒',RUNTIME_ERROR:'服务运行异常',BUILD_ERROR:'构建异常',BUILDING:'构建中',PAUSED:'已暂停',UNKNOWN:'当前状态未提供'})[a.runtimeStage]||'运行状态未确认';}
 window.RizhiCatalog={profile,text,group,type,state};
})();

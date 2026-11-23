'use strict';
(() => {
 const guides={
  'ggml-org/llama.cpp':{name:'llama.cpp',what:'让大模型在自己的电脑或服务器上运行的底层引擎。',who:'主要面向本地部署用户和开发者；只使用网页聊天的人通常不用逐个追踪构建号。',steps:['载入模型文件','用本机硬件计算','输出给聊天或程序界面']},
  'n8n-io/n8n':{name:'n8n',what:'把多个软件的操作连接成自动流程的工具，例如收集资料后再交给 AI 处理。',who:'适合需要自动整理资料、处理表格或连接业务系统的人。',steps:['设定触发条件','处理或传递资料','交给 AI 或其他软件']},
  'ollama/ollama':{name:'Ollama',what:'在本地下载、启动和管理大模型的工具。',who:'想在自己的设备上使用模型的人，可关注是否新增需要的模型支持。',steps:['选择模型','在本机启动','通过界面或程序使用']},
  'comfy-org/comfyui':{name:'ComfyUI',what:'通过连接可视化节点，组织 AI 生图、视频等创作步骤的工具。',who:'搭建 AI 图像与视频工作流的人，可以关注节点和模型兼容性。',steps:['准备模型与素材','连接处理节点','运行并查看生成结果']},
  'huggingface/transformers':{name:'Transformers',what:'帮助开发者加载、训练和使用不同 AI 模型的 Python 工具库。',who:'主要面向写代码或部署模型的人；普通读者更值得关注它新增支持了什么模型。'},
  'huggingface/diffusers':{name:'Diffusers',what:'帮助开发者运行图像、视频等生成模型的工具库。',who:'主要面向编写生成程序或搭建生成流程的人。'},
  'langgenius/dify':{name:'Dify',what:'把模型、资料和工具组合成 AI 应用与自动流程的平台。',who:'需要搭建知识库助手、AI 应用或业务流程的人。'},
  'flowiseai/flowise':{name:'Flowise',what:'通过可视化节点搭建 AI 智能体和处理流程的工具。',who:'想把模型和不同工具连接起来，搭建可运行流程的人。'},
  'm-bain/whisperx':{name:'WhisperX',what:'把语音转成文字，并对齐文字在音视频中出现时间的工具。',who:'需要制作转写、字幕或处理带时间轴文本的人。'}
 };
 function projectKey(a){for(const s of a.sources||[]){try{const u=new URL(s.url);if(u.hostname==='github.com'&&/\/releases(?:\/|$)/.test(u.pathname))return u.pathname.split('/').slice(1,3).join('/').toLowerCase();}catch{}}return (a.company||'').replace(/\s*更新$/,'').toLowerCase();}
 function isToolUpdate(a){return !a.isResource&&(a.channel==='tool-update'||(Array.isArray(a.tags)&&a.tags.includes('开源更新'))||(a.sources||[]).some(s=>/^https?:\/\/github\.com\/[^/]+\/[^/]+\/releases(?:\/|$)/i.test(s.url)));}
 function guide(a){const key=projectKey(a);return guides[key]||{name:(a.company||'软件项目').replace(/\s*更新$/,''),what:'这是一个软件项目的版本记录。',who:'如果正在使用这个项目，可以查看官方发布说明判断改动是否影响自己。'};}
 function nature(a){const text=a.title+' '+a.summary;
  if(/CVE-\d|security (?:fix|vulnerabil|advisory)|安全(?:漏洞|修复)/i.test(text))return {label:'安全相关更新',note:'发布说明涉及安全问题。正在使用这个工具的人，应核对受影响的版本和官方处理建议。'};
  if(/\bNew Models\b|新增模型支持/i.test(text))return {label:'新增模型适配',note:'此版本包含新增模型支持。需要使用这些模型的人，可以查看具体名单和运行要求。'};
  if(/\bNew Features\b|\bFeatures\b|What's New|新功能/i.test(text))return {label:'功能与维护更新',note:'发布说明包含功能调整和维护改动。具体是否用得上，要看你正在使用哪些功能。'};
  return {label:'近期维护更新',note:'这是一条开发维护记录。只想了解 AI 新产品的读者，可以先看最新消息；正在使用这个工具的人再查看详细改动。'};
 }
 function toolText(a){const g=guide(a),n=nature(a);return {title:g.name+'：'+n.label,summary:g.what+' '+(n.label==='近期维护更新'?'近期主要收录版本维护记录。':n.note),simple:g.who,guide:g,nature:n};}
 function groupTools(items){
  const groups=new Map();for(const a of items){const key=projectKey(a);if(!groups.has(key))groups.set(key,[]);groups.get(key).push(a);}
  const floating=a=>/^(stable|latest|beta|nightly|next|main|master)$/i.test(a.title.trim());
  const version=a=>(a.title.match(/\bb\d+\b/i)|| (a.title+' '+a.summary).match(/\d+\.\d+(?:\.\d+)*(?:[-.](?:rc|beta|alpha)\d*)?/i)||[a.id])[0];
  return [...groups.values()].map(rows=>{const unique=new Map();for(const row of rows){const key=version(row),old=unique.get(key);if(!old||floating(old)&&!floating(row))unique.set(key,row);}const versions=[...unique.values()].sort((a,b)=>(b.publishedAt||b.eventDate).localeCompare(a.publishedAt||a.eventDate));return {...versions[0],relatedUpdates:versions,recordCount:rows.length,projectKey:projectKey(versions[0])};});
 }

 window.RizhiContent={isToolUpdate,projectKey,guide,nature,toolText,groupTools};
})();

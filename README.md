# AI 日知 · 独立公网站

手机、Windows 和 Mac 打开同一个网址阅读，不需要登录 GPT，也不需要家里的电脑一直开机。

- 网站：[https://liltzer.github.io/ai-rizhi/](https://liltzer.github.io/ai-rizhi/)
- 源码与运行记录：[https://github.com/liltzer/ai-rizhi](https://github.com/liltzer/ai-rizhi)

## 这版有什么

- **中文整理**：免费 Qwen 文字模型把英文标题、RSS 摘要整理成简明中文，加一句通俗说明；产品名、版本号与重要数字保留。你反馈的住友生命案例以及少量边界条目，按来源摘要校订；校订结果由来源哈希限定，源文变化后不会套用旧稿。支持原文对照与搜索。
- **开源发现**：读取 Hugging Face 模型目录、维护者账号，以及 GitHub 仓库和更新记录。模型、软件、工作流／节点分别筛选，提供用途、入门路径、许可与真实项目入口。资源最近更新时间与新闻发布日期分开。
- **10 套主题**：晴空、夜航、森林、赛博、樱花、落日、海盐、葡萄、墨白、极光；背景、强调色和首页图形随主题变化，选择保存在浏览器。
- **实际互动**：可见的点击波纹、细短渐隐的单色曲线拖尾（轻柔模式更短），点击反馈、卡片轻微倾斜与滚动入场，页面和详情阅读进度、返回顶部、收藏反馈；首页 AI 星球可拖动或用方向键移动，双击／Home 复位。关注标签可拖动排序，也支持 Alt + 左右键，顺序在本机保存。
- **新闻与工具更新分开**：首页先显示已完成中文整理的行业和产品消息；小版本、构建号和开发日志集中放到“工具更新”，同一项目合并展示，先解释工具用途与适用人群。旧版本保留在三个月记录里，往期可勾选包含工具版本。普通新闻优先翻译，维护日志不占自动翻译预算。
- **阅读与迁移**：近一个月／三个月日期回看、分类与关键词搜索、收藏、JSON 备份导入导出。手机适配；系统减少动态效果时默认轻柔，也可在主题菜单关闭装饰动效。

首次打开新版若仍是旧页面，请刷新一次。旧的主题、收藏与备份继续兼容。收藏和偏好保存在当前浏览器，可用导出／导入迁移，不会自动跨设备同步。

## 内容是怎么更新的

GitHub Pages 提供网页，GitHub Actions 在每小时第 7 和 37 分钟尝试采集公开来源；可在 Actions 手动运行。GitHub 排队可能延迟，页面显示最近成功时间，超过一小时会提示滞后。“读取最新”按钮读取已经发布的数据，不能代表实时抓取外站。

新闻按 URL 去重，保留最近三个月；不把收录时间当成事件发生时间，也不为缺失日期编造新闻。开源资源有独立的 `site/discovery.json`，有数量上限；资源活跃更新不等于今天发布的新产品。HF 热度与下载量、GitHub 星标只是元数据，不是质量或实测排名。精选说明来自项目公开文档，没有逐项安装测试。开放权重、自定义许可、需申请访问的模型均应再核对模型卡。

新闻源配置在 `sources.json`，包括官方博客、媒体 RSS 和部分项目的稳定版 Release。无效日期、未来日期、预发布版本会跳过。资源目录配置在 `scripts/resource_sources.json`，涵盖文本、图像、视频、语音模型，以及 ComfyUI、自动化、Agent、本地运行等工具。抓取部分失败保留旧内容和来源状态；全部失败仍发布旧内容与失败状态，然后将任务明确标为失败。

## 免费中文后台

默认使用官方 [Qwen3-4B GGUF](https://huggingface.co/Qwen/Qwen3-4B-GGUF) 的 Q4_K_M 量化模型和官方 [llama.cpp](https://github.com/ggml-org/llama.cpp) 推理程序。无需付费 API、密钥或新的模型账号。约 2.5GB 的权重仅供后台处理，不发送给阅读者、不打进网站和源码压缩包；GitHub Actions 缓存下载文件。

模型与运行程序的版本、来源和 SHA-256 固定在 `scripts/translation-model.json`；下载后校验，安全解压。后台只把公开标题和摘要传给本机回环地址运行的模型。原文、日期、链接保持可查，中文整理另存，带来源哈希、版本和时间。输入内容按资料处理，不执行其中的指令；输出检查编号对齐、中文、数字、产品名和部分不受支持的未来计划。自动检查不能保证翻译没有语义偏差，可随时对照原文。

定时与手动任务每次最多整理 24 条、约 10 分钟；代码推送先验证模型，只补齐最多8条、约90秒的新稿后发布，历史重译另在后台分批进行。按批次保存，失败的单条不会挡住其他条。已有旧机译会逐步替换，页面保留实际状态和原文。翻译范围是标题与来源摘要，**不等于外链全文已翻译，也不冒充全文精读或产品实测**。已有通俗解说和原创流程图保留；详情另有网页中文阅读入口，外站可用性取决于网络。

本机后台运行需要 Python 3.12，以及 Apple Silicon macOS 或 Linux x64。Windows 上阅读网页和修改源码无需模型；批量模型整理可交给 GitHub Actions。默认自动更新使用公开仓库标准 runner，不使用付费模型或大型 runner。

```sh
python scripts/collect.py
python scripts/discover.py
python scripts/translation.py --limit 24 --seconds 600
```

GitHub API 在 Actions 中使用本次任务的短期 `GH_TOKEN`；本机可使用已经授权的官方 GitHub CLI。不要把密钥、模型缓存或个人收藏提交到仓库。许可说明见 `THIRD_PARTY_NOTICES.md`。

## 修改页面与本地预览

只改页面时不用启动模型。在源码目录运行：

```sh
python -m http.server 8080 --bind 127.0.0.1 --directory site
```

浏览器打开 http://127.0.0.1:8080 即可修改和预览。日常阅读仍使用上面的公网网址。

## 在你自己的免费托管账号部署

1. 把源码放入你拥有的公开 GitHub 仓库，默认分支 `main`。
2. 仓库 Settings → Pages → Source 选择 GitHub Actions。
3. Actions →“更新新闻并发布网站”→ Run workflow。
4. 等任务成功，打开该仓库实际提供的 Pages URL。页面用相对路径，兼容项目子路径，无需购买域名或服务器。

阅读不依赖部署账号保持登录。公开仓库的标准 Actions 和 Pages 可以使用免费方案；限额与定时任务策略以 GitHub 当时规则为准。定时任务长期未运行时需要站长查看 Actions；不能保证平台永不漏跑。

发布使用 `scripts/deploy_pages.py`，通过官方 REST artifact 列表和 Pages 部署接口读取当前任务的上传文件，避免此前原生 deploy-pages 在此仓库错误返回空 artifact 的问题。只使用当次 `GITHUB_TOKEN` 和 OIDC，不保存凭据，等待返回成功才结束发布。

## 验证与目录

```sh
python -m unittest discover -s tests -v
python scripts/check_translation_model.py
node --check site/app.js
node --check site/studio.js
node tests/frontend.test.mjs
node tests/trail.test.mjs
node tests/scroll.test.mjs
```

`tests/frontend.test.mjs` 是 Happy DOM 的交互逻辑回归，需 Node.js 和 `work/domqa/node_modules/happy-dom`（本次验证使用 21.0.4）。可用 `npm install --prefix work/domqa --no-save happy-dom@21.0.4` 安装。它检查主题、点击反馈层、拖动、排序、筛选、详情与收藏，以及开发日志分组、待中文稿提示和旧版本保留；拖尾检查覆盖无 Canvas、轻柔／标准／关闭模式、页头与弹窗层级、停止移动后的清理；滚动检查覆盖进度、入场、返回顶部和不拦截原生滚轮，**不能替代真实浏览器的视觉和触摸体验检查**。模型检查会启动实际模型，样例不会加入公开新闻库。

- `site/`：发布的 HTML、样式、脚本、新闻和资源 JSON。`content.js` 负责新闻／工具记录分组和用途说明；`scroll.js` 负责阅读进度、入场与返回顶部。
- `scripts/core.py`、`collect.py`：RSS/Atom 采集、日期、去重与滚动保留。
- `scripts/discover.py`：公开模型／软件目录采集与失败保留。
- `scripts/editor.py`、`translation.py`：免费文字模型整理与缓存。
- `scripts/editorial-zh.json`：少量按来源摘要校订的中文稿，只匹配完全相同的来源哈希。
- `.github/workflows/news.yml`：定时采集、保存数据、发布。
- `tests/`：原文保留、错误输出隔离、资源失败保留与交互检查。

源码包不包含 `.git`、账号、密钥、模型权重和临时工作目录；可以带到其他电脑继续设计，也可以迁移到支持静态网页的托管平台。

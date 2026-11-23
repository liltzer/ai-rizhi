# AI 日知 · GitHub 公网站

手机、Windows 和 Mac 使用同一个公开网站。普通阅读不需要 GitHub 或 GPT 登录。

网站地址：https://liltzer.github.io/ai-rizhi/

源码与运行记录：https://github.com/liltzer/ai-rizhi

Windows 可双击本目录的「打开AI日知.url」；手机在浏览器打开网站地址，可添加到主屏幕。阅读无需安装本项目或保持家中电脑开机。

网页由 GitHub Pages 提供，新闻由 GitHub Actions 每小时第7和37分钟采集。定时任务可能因平台排队而延迟，不能承诺准点；页面始终显示最近成功采集时间，超过一小时会标注滞后。公开仓库60天无活动可能被平台停用定时任务，需要站长重新启用。

## 部署

1. 将本项目放入你拥有的 **公开 GitHub 仓库**，默认分支为 main。只发布源码与公开新闻，不含个人收藏、密码或密钥。
2. 仓库 Settings → Pages → Source 选 GitHub Actions。
3. Actions →「更新新闻并发布网站」→ Run workflow 执行首次采集与部署。
4. 等待任务成功，用实际返回的 Pages URL 验证。默认是 GitHub 提供的 github.io 地址，不需要购买域名或服务器。

GitHub 的标准公共 Actions runner 和公开仓库 Pages 可使用免费方案。此项目不使用大型 runner、私有仓库、付费模型或自动升级套餐。

## 运行和更新

- 网站无需你的电脑常开。离开家后手机仍可以用同一个网址访问，实际连通性取决于当地网络对 GitHub Pages 的访问。
- 页面按钮「读取最新内容」重读后台已发布的数据，不声称会现场抓取新闻。
- 站长需要立即采集时，在 Actions 中手动运行工作流；普通访客不能远程修改公共新闻。
- 每次运行读取来源仍提供的记录，按URL去重，保留三个月。即使来源全失败，仍发布已有新闻与失败状态，并将本次任务标为失败。
- 采集失败时下一次计划继续尝试；GitHub 本身停用或未执行计划时无法自我唤醒，页面会通过滞后提示反映出来。
- 运行记录可在仓库 Actions 中查看。不能把“任务配置完成”说成“未来永不漏跑”。

## 内容

默认以中文展示新闻标题和来源摘要，支持一键切换原文。后台通过 Google 免费网页翻译入口处理公开 RSS 标题、摘要，不调用付费 API，不需要读者登录 GPT 或安装插件。与付费 Cloud Translation API 不同，这个网页入口不提供可用性承诺；限流或失败会留在待翻译列表，下次更新继续。已有译文存入公开 JSON，阅读时不会实时请求翻译服务。

每条译文带源文本哈希、引擎、修订号与翻译时间；源标题、摘要、日期及链接保留。翻译只覆盖 RSS 标题和摘要，不包含外链全文，也不冒充深度解说。产品名与术语做有限校正，机译仍可能有偏差。已有中文解说与原创流程图继续保留。

公开数据在 site/library.json；收藏仅在当前浏览器保存，可导出 JSON 迁移，不跨设备自动同步。

## 阅读界面

- 晴空、夜航、森林三种主题保存在当前浏览器，下次打开自动恢复。
- 卡片分栏自动适配手机和电脑；列表分批加载，搜索同时匹配中文译文与原文。
- 轻量点击波纹、卡片悬浮和收藏反馈；遵循系统“减少动态效果”设置。
- 详情可切换中文／来源原文，带常用 AI 术语解释；往期日期筛选和备份格式兼容原版。

## 翻译后台

工作流先采集，再补译，最后保存并发布；每次翻译最多约 10 分钟，首次积压较多时分次处理。每批保存进度，限流或网络失败不会覆盖原文和已完成的译文，不会阻止新闻内容发布。前端明确显示待翻译和来源状态。使用 Python 标准库即可运行，不需要下载模型或放入 API 密钥。

```sh
python scripts/translation.py --seconds 600
```

## 验证

```sh
python -m unittest discover -s tests -v
python scripts/collect.py
```

Python 3.12标准库即可运行采集脚本；阅读网页不需要安装 Python。源码或新闻备份可重新部署到其他账号或其他托管平台。

## 文件

- .github/workflows/news.yml：采集、持久化与Pages发布。
- scripts/collect.py：从已有JSON恢复、采集、去重、滚动保留、生成公开JSON。
- scripts/core.py：RSS/Atom读取与内部SQLite处理，临时数据库不上传。
- site/：实际发布到公网的内容，站点使用相对路径兼容项目网址。
- tests/：失败保留、去重、备份与不可信链接检查。

外部资料：[GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages)、[定时任务限制](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule)。

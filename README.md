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

默认以中文展示新闻标题和来源摘要，支持一键切换原文。后台使用离线 AI 神经翻译模型补译外文标题与摘要，不需要阅读者安装插件或登录 GPT。译文存入公开 JSON，阅读时不必等待翻译服务。

每条译文带源文本哈希、引擎、修订号与翻译时间；源标题、摘要、日期及链接保留。翻译范围为 RSS 标题和摘要，不包含外链全文，也不冒充深度解说。产品名与术语做有限校正，机译仍可能有偏差。详情另提供“用中文阅读这篇原文”入口（跳转网页翻译服务），便于继续看完整网页。已有中文解说与原创流程图保留。

公开数据在 site/library.json；收藏仅在当前浏览器保存，可导出 JSON 迁移，不跨设备自动同步。

## 阅读界面

- 晴空、夜航、森林三种主题保存在当前浏览器，下次打开自动恢复。
- 卡片分栏自动适配手机和电脑；列表分批加载，搜索同时匹配中文译文与原文。
- 轻量点击波纹、卡片悬浮和收藏反馈；遵循系统“减少动态效果”设置。
- 详情可切换中文／来源原文，带常用 AI 术语解释；往期日期筛选和备份格式兼容原版。

## 翻译后台

工作流先采集，再补译，最后保存并发布；每次翻译最多约 10 分钟，首次积压较多时分次处理。每批保存进度，模型准备或运行失败时保留原文和已完成译文，仍发布新闻及失败状态。前端显示实际完成数量和待翻译内容。

使用 Meta 的 NLLB-200 distilled 600M 模型，CTranslate2 int8 CPU 推理；约 600MB 的模型只在后台运行，Actions cache 缓存模型，不进入前端。下载文件版本和 SHA-256 固定在 scripts/translation-model.json；加载前校验。不需要模型服务账号、API 密钥或公司的常开电脑。

本机补译（Python 3.12，推荐隔离环境）：

```sh
python -m pip install -r scripts/requirements-translation.txt
python scripts/translation.py --seconds 600
```

模型信息与许可：

- 原模型：[Meta NLLB-200 distilled 600M](https://huggingface.co/facebook/nllb-200-distilled-600M)。
- 转换权重：[JustFrederik / NLLB CTranslate2 int8](https://huggingface.co/JustFrederik/nllb-200-distilled-600M-ct2-int8)，固定提交 `302d78f00e6fdb50a1064059df7c392b735e9d05`。本项目增加分批缓存和术语校正。
- 模型许可为 CC-BY-NC-4.0，本配置面向个人非商业新闻阅读。商业化前应换用许可适合的模型或服务。程序代码与模型许可分开，不将权重混入代码包。
- 少量早期译文来自 Google 网页机译，已有合格缓存保留。`--engine web` 仅为手动备选；该网页入口可能限流，不是有可用性承诺的 Cloud Translation 付费 API。默认自动更新使用离线模型。

## 发布

仓库已观察到 deploy-pages 的 Results SDK 在文件上传后返回空列表，现使用 scripts/deploy_pages.py，通过官方 REST artifact 列表和 Pages 部署接口发布。只使用当前任务的短期 GITHUB_TOKEN 和 OIDC，不保存或输出凭据；等待部署真正成功才标记发布完成。

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

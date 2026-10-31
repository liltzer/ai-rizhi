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

来源在 sources.json 中设置。默认提供来源标题、摘要、日期和原文链接。已有的中文说明与原创流程图随历史备份保留。没有自动调用付费模型，不编造每条新闻的深度解释。

公开数据保存在 site/library.json，包含公开文章和采集状态。收藏仅在当前浏览器中保存，可导出JSON迁移；暂不跨设备自动同步收藏。

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

# 第三方来源与许可

- Qwen3-4B GGUF：由 Qwen 官方模型仓库提供，Apache-2.0。本项目固定版本和权重哈希，首次运行从官方 Hugging Face 下载，不在源码或前端中分发模型权重。https://huggingface.co/Qwen/Qwen3-4B-GGUF
- llama.cpp：ggml-org 官方项目，MIT；后台从官方 GitHub Release 下载固定版本，校验 SHA-256，原发布包所附许可文件保留在缓存目录。https://github.com/ggml-org/llama.cpp
- 运行期不加载 Hugging Face 仓库提供的 Python 自定义代码；本项目只加载 GGUF 权重。
- 新闻标题、来源摘要、项目元数据和原文链接来自各公开来源，其内容和商标权归各权利人所有。AI 整理可能有误，不替代原文。
- 开源发现中的软件与模型有各自许可。公开代码、公开权重、可商用、无条件使用是不同概念；请以项目许可证或模型卡为准，目录不替项目授予许可。
- Happy DOM 仅用于本机开发逻辑验证，不进入前端或部署包。https://github.com/capricorn86/happy-dom

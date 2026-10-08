# Hyperliquid Docs

Hyperliquid 官方文档的非官方本地存档，保留英文原文和章节结构，方便在 GitHub 浏览或下载后查阅。

- 官方来源：<https://hyperliquid.gitbook.io/hyperliquid-docs>
- 下载时间：2026 年 10 月 9 日（Asia/Shanghai）
- 内容：149 个 Markdown 页面，20 个图片或附件文件
- 覆盖：About Hyperliquid、Onboarding、HyperCore、HyperEVM、Trading、HIPs、Validators、开发者/API/节点文档、Builder Tools、Support
- 完整导航：[文档目录](SUMMARY.md)
- 下载记录、来源地址和 SHA-256 校验值：[manifest.json](manifest.json)

## 常用入口

| 内容 | 文档 |
| --- | --- |
| 项目介绍 | [About Hyperliquid](docs/about-hyperliquid.md) |
| 开始使用 | [Onboarding](docs/onboarding.md) |
| 交易机制 | [Trading](docs/trading.md) |
| API | [API](docs/for-developers/api.md) |
| HyperEVM 开发 | [HyperEVM](docs/for-developers/hyperevm.md) |
| Builder Tools | [Read Me](docs/builder-tools/read-me-builder-tools.md) |
| 常见问题 | [Support Guide](docs/support/read-me-support-guide.md) |

## 本地更新

需要 Python 3.9 或更新版本，无需额外安装依赖。在仓库根目录运行：

```sh
python3 scripts/download_docs.py
```

脚本读取官方 sitemap 和 `llms.txt`，下载 Markdown 及 GitBook 托管的图片和附件，并将已知文档链接转换为仓库内的相对路径。示例代码保持原样；其他外部链接仍然指向原网站。脚本直接访问官方文档服务器。

本仓库是下载时的快照，没有配置自动定时更新。官方文档中的 GitBook 专有标签保留原样，部分提示框和交互组件在 GitHub 的显示可能与官网不同。

## 来源与权利

文档和媒体的权利归各自原作者所有。本仓库为非官方存档，与 Hyperliquid 无隶属关系，也不代表官方背书。最新内容请以官方文档为准。详见 [NOTICE.md](NOTICE.md)。

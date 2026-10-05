# xmind-creater

面向 Codex 和 Claude Code 的离线 Markdown 转 XMind 思维导图技能。Windows x64 安装包内置精简版 Python 运行时，不需要安装 Node.js、npm，也不依赖原始的 video2txt 项目。

## 安装

下载并解压 `markdown-xmind-offline-win-x64.zip`，然后在解压后的 `mindmap-skill` 目录中运行：

```powershell
.\install.cmd --agent both
```

如果只需要安装到一个智能体，可使用 `--agent codex` 或 `--agent claude`：

- Codex：调用 `$markdown-xmind-offline`
- Claude Code：调用 `/markdown-xmind-offline`

在 macOS、Linux 和 Windows ARM64 上，请复制 `mindmap-skill` 目录，并在已安装 Python 3.8 或更高版本的环境中运行：

```bash
python3 install.py --agent both
```

只有 Windows x64 安装包提供内置 Python 运行时。

## 不使用智能体直接转换

先创建一个 UTF-8 编码的 Markdown 大纲，然后运行：

```powershell
.\mindmap.cmd audit outline.md
.\mindmap.cmd convert outline.md output.xmind --strict
.\mindmap.cmd validate output.xmind
```

更多选项请参阅[技能使用说明](mindmap-skill/README.md)。

## 说明

- 转换器不会对原始长文本进行摘要，也不包含 AI 模型。
- ZIP 格式校验不能替代在 XMind 中打开文件进行视觉检查。
- 工作目录中的三个供应商 ZIP 包和基于源文件生成的示例输出已通过 Git 忽略，不会提交到仓库。
- 便携版 Python 运行时的许可证位于 `mindmap-skill/runtime/win-x64/LICENSE.txt`。

本仓库遵循根目录中的 [Apache 2.0 许可证](LICENSE) 发布；内置 Python 运行时同时保留其自身的许可证声明。

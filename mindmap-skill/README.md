# 离线 Markdown → XMind Agent Skill

从 `video2txt/tools/xmind/md2xmind.js` 的 Markdown 大纲转换流程拆出；不需要原项目、Node.js、npm、XMind 软件或联网。内置 Windows x64 Python 3.11 精简运行时（许可证见 `runtime/win-x64/LICENSE.txt`），Windows x64 不需要另装 Python。macOS、Linux 和 Windows ARM64 仍需要本机 Python 3.8+；本包没有提供这些平台的运行时。

## 安装

将整个 `mindmap-skill` 文件夹（包括 `runtime`）复制到目标电脑；也可复制项目根目录的 `markdown-xmind-offline-win-x64.zip` 并完整解压。Windows x64 在解压后的 `mindmap-skill` 文件夹中运行以下命令，同时安装到 Codex 与 Claude Code，无需网络与管理员权限：

```powershell
.\install.cmd --agent both
```

其他系统用 `python3 install.py --agent both`。仅安装一端可用 `--agent codex`（默认）或 `--agent claude`：

| Agent | 默认个人安装位置 | 对话中显式调用 |
| --- | --- | --- |
| Codex | `~/.agents/skills/markdown-xmind-offline` | `$markdown-xmind-offline` |
| Claude Code | `~/.claude/skills/markdown-xmind-offline` | `/markdown-xmind-offline` |

单端安装时可传 `--skills-dir PATH`；双端安装时分别使用 `--codex-skills-dir PATH` 和 `--claude-skills-dir PATH`。安装器不会覆盖已有同名目录，安装失败前会检查两个目的地。重启或刷新 Agent 的 skill 列表。两种 Agent 自动调用时均依据 `SKILL.md` 描述。Agent 本身的运行/模型服务不由此包提供，**离线**仅指安装及 Markdown→XMind 本地转换，不代表 AI 对话无需网络。

## 独立使用

```powershell
.\mindmap.cmd audit outline.md
.\mindmap.cmd convert outline.md output.xmind --strict --structure logic-right
.\mindmap.cmd validate output.xmind
```

其他系统将 `mindmap.cmd` 替换为 `python3 scripts/mindmap.py`。安装后可在安装目录运行同一命令。此工具只负责从结构化大纲生成导图；处理原始长文需 agent 或人工先整理大纲，离线运行时不自带 AI 模型。

需要从长文或多份素材制作导图时，先按 [内容质量指南](references/quality.md) 提炼出可追溯的 Markdown 大纲，再运行 `python scripts/mindmap.py audit outline.md` 检查可能被忽略的正文、标题跳级、重复/过长节点和过密分支。审计输出为 JSON；修正正文遗漏后可使用 `convert ... --strict` 阻止静默丢失内容。宽度和长度提示只供人工判断，不会擅自删减事实。脚本不调用 AI；语义提炼由运行该 skill 的 agent 根据源材料完成。

输入文件为 UTF-8 Markdown；支持 `#` 到 `######` 标题、`-`/`*`/`+`/有序列表及空格缩进的子列表。只解析结构化大纲，不把普通段落自动改写成摘要。可用布局：`logic-right`（默认）、`logic-left`、`map-right`、`map-left`、`org-down`、`org-up`、`tree-right`、`tree-left`。

产物是包含 `content.json`、`metadata.json` 和 `manifest.json` 的 XMind ZIP 文件。校验检查归档与主题树结构，仍不能代替 XMind 应用中的兼容性及视觉检查。生成时会先写临时文件并校验，再原子替换目标文件。本包不联网、不进行音视频转写或 PPT 生成。

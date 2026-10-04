# xmind-creater

An offline Markdown-to-XMind agent skill for Codex and Claude Code. The Windows x64 package includes a minimal Python runtime and does not require Node.js, npm, or the original video2txt project.

## Install

Download and extract `markdown-xmind-offline-win-x64.zip`, then run inside the extracted `mindmap-skill` folder:

```powershell
.\install.cmd --agent both
```

Use `--agent codex` or `--agent claude` to install for just one agent. In Codex, invoke `$markdown-xmind-offline`; in Claude Code, invoke `/markdown-xmind-offline`.

On macOS, Linux, and Windows ARM64, copy `mindmap-skill` and run `python3 install.py --agent both` with Python 3.8+ installed. Only Windows x64 has a bundled runtime.

To use without an agent, create a UTF-8 Markdown outline and run:

```powershell
.\mindmap.cmd audit outline.md
.\mindmap.cmd convert outline.md output.xmind --strict
.\mindmap.cmd validate output.xmind
```

See [the skill guide](mindmap-skill/README.md) for more options. The converter does not summarize raw prose or include an AI model. Its ZIP validation does not replace opening the result in XMind for visual inspection.

The three vendor ZIPs and source-derived example outputs in this working directory are excluded from Git. The portable Python distribution's license is included in `mindmap-skill/runtime/win-x64/LICENSE.txt`.

The repository is distributed under the root [Apache 2.0 license](LICENSE). The bundled Python runtime retains its own license notice.

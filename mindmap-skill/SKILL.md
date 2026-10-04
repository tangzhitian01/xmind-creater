---
name: markdown-xmind-offline
description: Draft, audit, and generate an offline XMind mind map from local text or a Markdown outline. Use for evidence-based mind maps, not media transcription or slide creation.
---

# Markdown to XMind (Offline)

Use the bundled standard-library converter. No network access, XMind installation, Node.js, or video2txt files are needed. Windows x64 includes a Python 3.11 runtime; other platforms require an installed Python 3.8+.

1. If the input is prose or several sources, draft a UTF-8 Markdown outline first. Follow [the drafting and review guide](references/quality.md) for source fidelity, branch structure, concise labels, and supported layouts. The script does not invent or summarize content.
2. Resolve this skill's directory from the current `SKILL.md`. Use absolute input and output paths so the caller's working directory does not change their meaning. On Windows x64 run `<skill-dir>/mindmap.cmd audit INPUT.md`; elsewhere run `python3 <skill-dir>/scripts/mindmap.py audit INPUT.md`. Resolve all unmapped-text errors and review density, duplicate, and heading warnings in context.
3. On Windows x64 run `<skill-dir>/mindmap.cmd convert INPUT.md OUTPUT.xmind --strict [--structure logic-right]`, or the corresponding Python command elsewhere. The output parent directory is created automatically.
4. Run `<skill-dir>/mindmap.cmd validate OUTPUT.xmind` (or its Python equivalent). Compare the map against the input; check appearance in a local XMind viewer when available. Report the exact output path and any limitations. Keep the original material and working outline.

Headings (`#` through `######`) and nested bullet/numbered lists form the tree. A single top-level heading becomes the center topic; multiple top-level headings become its children under the input filename. The default layout is `logic-right`; `logic-left`, `map-right`, `map-left`, `org-down`, `org-up`, `tree-right`, and `tree-left` are also supported. Audit warnings are heuristics, not automatic rewriting rules.

To install on another computer without internet, copy this entire `mindmap-skill` folder including `runtime`. Run `install.cmd --agent both` on Windows x64 or `python3 install.py --agent both` elsewhere to install for Codex and Claude Code. Use `--agent codex` or `--agent claude` for one host. See `README.md` for locations and platform details.

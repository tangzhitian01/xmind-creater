# Mind-map drafting and review

Apply this when turning source material into a Markdown outline. The converter does not summarize prose. Do not run online ProcessOn calls or copy vendor-specific theme JSON into an offline XMind map.

## Draft from evidence

- Identify the reader's objective: learning, comparison, decisions, action items, or root-cause analysis. Give the map one clear center topic.
- Use the source's explicit headings as the starting skeleton. For a presentation, order major branches by the intended narrative (such as context, problem, approach, evidence, decision), not by the order files happened to be received. Do not force a presentation framework onto a book, meeting, or technical map.
- Reduce leaf paragraphs to short, single-idea statements. Preserve essential numbers, names, dates, units, conditions, and uncertainty exactly. Never convert one measure or deadline into another without evidence.
- Group related ideas before rendering. Distinguish causes, facts, proposals, risks, and next steps rather than mixing them as interchangeable siblings. Merge genuine duplicates; do not merge different claims merely because they look alike.
- For claims derived from source material, keep a source-to-node ledger alongside the working outline when accuracy matters (source filename/section or quoted span, node path, and any unresolved question). This ledger is a separate local file, not an unsupported XMind annotation. Mark additions not supported by the source as proposals or questions. Do not fabricate references.
- Follow the source language unless the user asks for another. Preserve technical terms; flag uncertain translations and disputed claims for verification.

## Organize for a screen

- Use `#` for the center topic, `##` for major branches, deeper headings for categories, and lists for details. Keep heading levels continuous. When depth exceeds six headings, continue with nested lists.
- Keep labels compact and meaningful; one idea per node. Prefer 3–7 children per branch as a review heuristic, not a content cap. Split a very dense map into separate maps only when the user agrees or the source naturally has independent topics.
- Choose XMind layout based on semantics: `map-right` for broad concept maps, `logic-right` for ordered reasoning, `org-down` for hierarchy, `tree-right` for work breakdown. These are supported XMind layouts; a fishbone, timeline, or table from a ProcessOn workflow cannot be represented faithfully by merely renaming an XMind layout. If those specialized forms are essential, state the limitation rather than silently substituting.
- Do not add decorative emoji, stock images, or claims solely to fill space. Prefer a small number of distinguishable major branches over styling every node.

## Review before delivery

Run `python scripts/mindmap.py audit outline.md`. Fix all `UNMAPPED_TEXT` errors: they indicate content that the converter would otherwise discard. Review other warnings in context; a warning is not permission to delete important material.

Then run `python scripts/mindmap.py convert outline.md result.xmind --strict` and `python scripts/mindmap.py validate result.xmind`. Compare the root, branch order, key leaf claims, and any source ledger against the input. A valid ZIP is not proof of visual quality; inspect in a local XMind application when available. Keep the outline and source ledger next to the output for later edits.

#!/usr/bin/env python3
"""Offline Markdown outline to modern XMind archive converter."""

import argparse
import json
import os
import re
import sys
import tempfile
import uuid
import zipfile
from collections import Counter
from pathlib import Path

STRUCTURES = {
    "logic-right": "org.xmind.ui.logic.right",
    "logic-left": "org.xmind.ui.logic.left",
    "map-right": "org.xmind.ui.map.right",
    "map-left": "org.xmind.ui.map.left",
    "org-down": "org.xmind.ui.org-chart.down",
    "org-up": "org.xmind.ui.org-chart.up",
    "tree-right": "org.xmind.ui.tree.right",
    "tree-left": "org.xmind.ui.tree.left",
}
HEADING = re.compile(r"^ {0,3}(#{1,6})\s+(.+?)\s*$")
ITEM = re.compile(r"^(\s*)(?:[-*+]|\d+[.)])\s+(.+?)\s*$")
FENCE = re.compile(r"^\s*(`{3,}|~{3,})")


def clean(text):
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"(?<!\w)(?:\*\*|__)(.+?)(?:\*\*|__)(?!\w)", r"\1", text)
    text = re.sub(r"(?<!\w)[*~](.+?)[*~](?!\w)", r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    return re.sub(r"\s+", " ", text).strip()


def analyze_outline(text, fallback):
    root = {"title": fallback, "children": []}
    headings = [(0, root)]
    root_kinds = []
    items = []
    current = root
    findings = []
    fence = None
    last_heading_depth = 0
    for line_number, line in enumerate(text.splitlines(), 1):
        fence_match = FENCE.match(line)
        if fence_match:
            marker = fence_match[1]
            if fence is None:
                fence = marker
            elif (marker[0] == fence[0] and len(marker) >= len(fence)
                  and not line[fence_match.end():].strip()):
                fence = None
            continue
        if fence or not line.strip():
            continue
        match = HEADING.match(line)
        if match:
            depth, title = len(match[1]), clean(match[2])
            if not title:
                continue
            if not last_heading_depth and depth > 1:
                findings.append({"level": "warning", "code": "MISSING_ROOT_HEADING",
                                 "line": line_number, "message": "First heading is not level one"})
            if last_heading_depth and depth > last_heading_depth + 1:
                findings.append({"level": "warning", "code": "HEADING_GAP",
                                 "line": line_number, "message": "Heading level jumps over a level"})
            last_heading_depth = depth
            while len(headings) > 1 and headings[-1][0] >= depth:
                headings.pop()
            node = {"title": title, "children": []}
            parent = headings[-1][1]
            parent["children"].append(node)
            if parent is root:
                root_kinds.append("heading")
            headings.append((depth, node))
            current = node
            items = []
            continue
        match = ITEM.match(line)
        if match:
            title = clean(match[2])
            if not title:
                continue
            indent = len(match[1].expandtabs(4))
            while items and items[-1][0] >= indent:
                items.pop()
            parent = items[-1][1] if items else current
            node = {"title": title, "children": []}
            parent["children"].append(node)
            if parent is root:
                root_kinds.append("item")
            items.append((indent, node))
            continue
        if line.strip() not in ("---", "***", "___") and not line.lstrip().startswith("<!--"):
            findings.append({"level": "error", "code": "UNMAPPED_TEXT",
                             "line": line_number, "message": "Text is not an outline node and will be omitted"})

    if fence is not None:
        findings.append({"level": "error", "code": "UNCLOSED_FENCE", "line": None,
                         "message": "Unclosed fenced code block"})
    top = root["children"]
    if not top:
        raise ValueError("No Markdown headings or list items found")
    if len(top) > 1 and "heading" in root_kinds:
        findings.append({"level": "warning", "code": "MULTIPLE_ROOTS",
                         "line": None, "message": "Several top-level topics use the filename as center"})
    outline = top[0] if len(top) == 1 and root_kinds == ["heading"] else root
    nodes = 0
    max_depth = 0
    stack = [(outline, 0)]
    while stack:
        node, depth = stack.pop()
        nodes += 1
        max_depth = max(max_depth, depth)
        limit = 60 if depth == 0 else 36 if node["children"] else 80
        if len(node["title"]) > limit:
            findings.append({"level": "warning", "code": "LONG_LABEL", "line": None,
                             "message": "Long node label: " + node["title"][:50]})
        children = node["children"]
        if len(children) > 7:
            findings.append({"level": "warning", "code": "WIDE_BRANCH", "line": None,
                             "message": "More than seven direct children: " + node["title"][:50]})
        counts = Counter(re.sub(r"\s+", "", child["title"]).casefold() for child in children)
        for child in children:
            key = re.sub(r"\s+", "", child["title"]).casefold()
            if counts[key] > 1:
                findings.append({"level": "warning", "code": "DUPLICATE_SIBLING",
                                 "line": None, "message": "Repeated sibling: " + child["title"][:50]})
                counts[key] = 0
        stack.extend((child, depth + 1) for child in reversed(children))
    if nodes > 200:
        findings.append({"level": "warning", "code": "DENSE_MAP", "line": None,
                         "message": "Map exceeds 200 topics; consider splitting it"})
    return {"outline": outline, "findings": findings,
            "statistics": {"topics": nodes, "max_depth": max_depth}}


def parse_outline(text, fallback):
    return analyze_outline(text, fallback)["outline"]


def xmind_topic(node):
    result = {"id": str(uuid.uuid4()), "title": node["title"]}
    if node["children"]:
        result["children"] = {"attached": [xmind_topic(child) for child in node["children"]]}
    return result


def inspect(source):
    return analyze_outline(source.read_text(encoding="utf-8-sig"), source.stem)


def convert(source, target, structure, strict=False):
    if structure not in STRUCTURES:
        raise ValueError("Unsupported structure: " + structure)
    report = inspect(source)
    errors = [finding for finding in report["findings"] if finding["level"] == "error"]
    if strict and errors:
        raise ValueError("{} outline error(s); run audit before converting".format(len(errors)))
    for finding in report["findings"]:
        print("{level} {code} (line {line}): {message}".format(**finding), file=sys.stderr)
    outline = report["outline"]
    root = xmind_topic(outline)
    root["structureClass"] = STRUCTURES[structure]
    content = [{"id": str(uuid.uuid4()), "title": outline["title"], "rootTopic": root}]
    manifest = {"file-entries": {"content.json": {}, "metadata.json": {}}}
    if source.resolve() == target.resolve():
        raise ValueError("Input and output must differ")
    target.parent.mkdir(parents=True, exist_ok=True)
    staged = None
    try:
        with tempfile.NamedTemporaryFile(dir=target.parent, prefix=".mindmap-",
                                         suffix=".xmind", delete=False) as temp:
            staged = Path(temp.name)
        with zipfile.ZipFile(staged, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("content.json", json.dumps(content, ensure_ascii=False))
            archive.writestr("metadata.json", "{}")
            archive.writestr("manifest.json", json.dumps(manifest))
        validate(staged)
        os.replace(staged, target)
    finally:
        if staged is not None:
            staged.unlink(missing_ok=True)


def validate(target):
    with zipfile.ZipFile(target) as archive:
        if archive.testzip() is not None:
            raise ValueError("Corrupt ZIP entry")
        required = {"content.json", "metadata.json", "manifest.json"}
        if not required.issubset(archive.namelist()):
            raise ValueError("Missing XMind archive entries")
        content = json.loads(archive.read("content.json"))
        manifest = json.loads(archive.read("manifest.json"))
        if not isinstance(manifest, dict) or not isinstance(manifest.get("file-entries"), dict):
            raise ValueError("Invalid XMind manifest")
        if not {"content.json", "metadata.json"}.issubset(manifest["file-entries"]):
            raise ValueError("Invalid XMind manifest")
        if not isinstance(content, list) or not content:
            raise ValueError("Missing XMind sheet")
        seen = set()
        first_root = None
        for sheet in content:
            if not isinstance(sheet, dict) or not isinstance(sheet.get("title"), str):
                raise ValueError("Invalid XMind sheet")
            sheet_id = sheet.get("id")
            if not isinstance(sheet_id, str) or not sheet_id or sheet_id in seen:
                raise ValueError("Missing or duplicate sheet ID")
            seen.add(sheet_id)
            root = sheet.get("rootTopic")
            if not isinstance(root, dict):
                raise ValueError("Missing root topic")
            if root.get("structureClass") not in STRUCTURES.values():
                raise ValueError("Unsupported root structure")
            if first_root is None:
                first_root = root
            stack = [root]
            while stack:
                topic = stack.pop()
                if not isinstance(topic, dict):
                    raise ValueError("Invalid topic")
                identifier = topic.get("id")
                title = topic.get("title")
                if (not isinstance(identifier, str) or not identifier or identifier in seen
                        or not isinstance(title, str) or not title.strip()):
                    raise ValueError("Missing or duplicate topic ID or title")
                seen.add(identifier)
                if "children" in topic:
                    children = topic["children"]
                    if (not isinstance(children, dict)
                            or not isinstance(children.get("attached"), list)
                            or not children["attached"]):
                        raise ValueError("Invalid topic children")
                    stack.extend(children["attached"])
    return first_root


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    make = commands.add_parser("convert")
    make.add_argument("input", type=Path)
    make.add_argument("output", type=Path)
    make.add_argument("--structure", choices=STRUCTURES, default="logic-right")
    make.add_argument("--strict", action="store_true", help="Reject input containing unmapped text")
    check = commands.add_parser("validate")
    check.add_argument("input", type=Path)
    audit = commands.add_parser("audit", help="Report outline quality and any omitted text")
    audit.add_argument("input", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "convert":
            convert(args.input, args.output, args.structure, args.strict)
            print(args.output.resolve())
        elif args.command == "validate":
            root = validate(args.input)
            print("valid: " + root["title"])
        else:
            report = inspect(args.input)
            print(json.dumps({"statistics": report["statistics"],
                              "findings": report["findings"]}, ensure_ascii=False, indent=2))
            if any(item["level"] == "error" for item in report["findings"]):
                return 1
    except (OSError, UnicodeError, ValueError, KeyError, zipfile.BadZipFile) as exc:
        parser.exit(1, "error: " + str(exc) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())

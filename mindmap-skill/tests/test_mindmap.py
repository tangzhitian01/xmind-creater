import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "mindmap.py"
spec = importlib.util.spec_from_file_location("mindmap", SCRIPT)
mindmap = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mindmap)


class MindmapTests(unittest.TestCase):
    def test_chinese_hierarchy_and_structure(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "输入.md"
            target = Path(temp) / "nested" / "结果.xmind"
            source.write_text("# 主题\n## 分支一\n- 要点甲\n- 要点乙\n  - 子要点\n## 分支二\n- 要点丙\n", encoding="utf-8")
            mindmap.convert(source, target, "tree-left")
            with zipfile.ZipFile(target) as archive:
                root = json.loads(archive.read("content.json"))[0]["rootTopic"]
            self.assertEqual(root["title"], "主题")
            self.assertEqual(root["structureClass"], "org.xmind.ui.tree.left")
            branches = root["children"]["attached"]
            self.assertEqual([item["title"] for item in branches], ["分支一", "分支二"])
            points = branches[0]["children"]["attached"]
            self.assertEqual([item["title"] for item in points], ["要点甲", "要点乙"])
            self.assertEqual(points[1]["children"]["attached"][0]["title"], "子要点")
            self.assertEqual(mindmap.validate(target)["title"], "主题")

    def test_multiple_roots_and_empty_input(self):
        root = mindmap.parse_outline("# A\n# B\n", "outline")
        self.assertEqual(root["title"], "outline")
        self.assertEqual([node["title"] for node in root["children"]], ["A", "B"])
        root = mindmap.parse_outline("- One\n- Two\n", "outline")
        self.assertEqual(root["title"], "outline")
        self.assertEqual([node["title"] for node in root["children"]], ["One", "Two"])
        with self.assertRaises(ValueError):
            mindmap.parse_outline("just prose\n", "outline")

    def test_bad_archive(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "broken.xmind"
            with zipfile.ZipFile(target, "w") as archive:
                archive.writestr("content.json", "[]")
            with self.assertRaises(ValueError):
                mindmap.validate(target)

    def test_rejects_malformed_and_duplicate_topics(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "invalid.xmind"
            root = {"id": "root", "title": "Root",
                    "structureClass": mindmap.STRUCTURES["logic-right"],
                    "children": {"attached": "not-a-list"}}
            def write_archive():
                with zipfile.ZipFile(target, "w") as archive:
                    archive.writestr("content.json", json.dumps([
                        {"id": "sheet", "title": "Root", "rootTopic": root}
                    ]))
                    archive.writestr("metadata.json", "{}")
                    archive.writestr("manifest.json", json.dumps({
                        "file-entries": {"content.json": {}, "metadata.json": {}}
                    }))
            write_archive()
            with self.assertRaisesRegex(ValueError, "children"):
                mindmap.validate(target)
            root["children"] = {"attached": [{"id": "root", "title": "Duplicate"}]}
            write_archive()
            with self.assertRaisesRegex(ValueError, "duplicate topic"):
                mindmap.validate(target)

    def test_preserves_literal_underscores_and_code(self):
        self.assertEqual(mindmap.clean("A_B and `my_value`"), "A_B and my_value")
        self.assertEqual(mindmap.clean("**Bold** and __strong__"), "Bold and strong")

    def test_audit_finds_content_loss_and_structure_issues(self):
        text = "# Center\n### Deep\nA factual paragraph.\n- Same\n- Same\n"
        report = mindmap.analyze_outline(text, "input")
        codes = {item["code"] for item in report["findings"]}
        self.assertEqual(report["statistics"]["topics"], 4)
        self.assertTrue({"HEADING_GAP", "UNMAPPED_TEXT", "DUPLICATE_SIBLING"} <= codes)
        self.assertEqual(next(item["line"] for item in report["findings"]
                              if item["code"] == "UNMAPPED_TEXT"), 3)

    def test_fenced_code_not_treated_as_outline(self):
        text = "# Center\n```md\n# Not a branch\n```python\n- Not a leaf\n```\n- Real leaf\n"
        report = mindmap.analyze_outline(text, "input")
        self.assertEqual(report["findings"], [])
        self.assertEqual([node["title"] for node in report["outline"]["children"]], ["Real leaf"])
        self.assertIn("UNCLOSED_FENCE", {item["code"] for item in
                      mindmap.analyze_outline("# Center\n```\ntext\n", "input")["findings"]})
        self.assertIn("MISSING_ROOT_HEADING", {item["code"] for item in
                      mindmap.analyze_outline("## Subheading\n", "input")["findings"]})

    def test_strict_conversion_preserves_existing_output(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "outline.md"
            target = Path(temp) / "result.xmind"
            source.write_text("# Center\nImportant prose.\n", encoding="utf-8")
            target.write_bytes(b"existing")
            with self.assertRaisesRegex(ValueError, "outline error"):
                mindmap.convert(source, target, "logic-right", strict=True)
            self.assertEqual(target.read_bytes(), b"existing")

    def test_failed_validation_preserves_output_and_removes_staging(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "outline.md"
            target = Path(temp) / "result.xmind"
            source.write_text("# Center\n- Detail\n", encoding="utf-8")
            target.write_bytes(b"existing")
            with mock.patch.object(mindmap, "validate", side_effect=ValueError("invalid")):
                with self.assertRaisesRegex(ValueError, "invalid"):
                    mindmap.convert(source, target, "logic-right")
            self.assertEqual(target.read_bytes(), b"existing")
            self.assertEqual(list(Path(temp).glob(".mindmap-*")), [])

    def test_offline_install_and_run(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            skills = root / "skills"
            installer = SCRIPT.parents[1] / "install.py"
            subprocess.run(
                [sys.executable, str(installer), "--skills-dir", str(skills)],
                check=True, capture_output=True, text=True,
            )
            installed = skills / "markdown-xmind-offline"
            self.assertTrue((installed / "SKILL.md").is_file())
            input_file = root / "outline.md"
            output_file = root / "output.xmind"
            input_file.write_text("# Center\n- Detail\n", encoding="utf-8")
            subprocess.run(
                [sys.executable, str(installed / "scripts" / "mindmap.py"),
                 "convert", str(input_file), str(output_file)],
                check=True, capture_output=True, text=True,
            )
            self.assertEqual(mindmap.validate(output_file)["title"], "Center")

    def test_install_for_both_agents_and_refuse_partial_install(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            installer = SCRIPT.parents[1] / "install.py"
            codex_dir = root / "codex-skills"
            claude_dir = root / "claude-skills"
            command = [sys.executable, str(installer), "--agent", "both",
                       "--codex-skills-dir", str(codex_dir),
                       "--claude-skills-dir", str(claude_dir)]
            subprocess.run(command, check=True, capture_output=True, text=True)
            for skills in (codex_dir, claude_dir):
                installed = skills / "markdown-xmind-offline"
                self.assertTrue((installed / "SKILL.md").is_file())
                self.assertTrue((installed / "scripts" / "mindmap.py").is_file())
            with tempfile.TemporaryDirectory() as another:
                other_codex = Path(another) / "codex"
                attempt = subprocess.run(
                    [sys.executable, str(installer), "--agent", "both",
                     "--codex-skills-dir", str(other_codex),
                     "--claude-skills-dir", str(claude_dir)],
                    capture_output=True, text=True,
                )
                self.assertNotEqual(attempt.returncode, 0)
                self.assertFalse((other_codex / "markdown-xmind-offline").exists())

    def test_install_for_claude_only(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            env = dict(os.environ, HOME=str(root), USERPROFILE=str(root))
            installer = SCRIPT.parents[1] / "install.py"
            subprocess.run([sys.executable, str(installer), "--agent", "claude"],
                           env=env, check=True, capture_output=True, text=True)
            self.assertTrue((root / ".claude" / "skills" /
                             "markdown-xmind-offline" / "SKILL.md").is_file())
            self.assertFalse((root / ".agents").exists())

    @unittest.skipUnless(os.name == "nt", "Bundled runtime is Windows x64")
    def test_bundled_python_installs_and_runs_without_system_python_on_path(self):
        package = SCRIPT.parents[1]
        runtime = package / "runtime" / "win-x64" / "python.exe"
        self.assertTrue(runtime.is_file(), "Bundled Python runtime is missing")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            skills = root / "skills"
            env = dict(os.environ, PATH=os.path.join(os.environ["SystemRoot"], "System32"),
                       PYTHONPATH="", PYTHONHOME="")
            subprocess.run(
                [str(package / "install.cmd"), "--skills-dir", str(skills)],
                check=True, capture_output=True, env=env,
            )
            installed = skills / "markdown-xmind-offline"
            self.assertTrue((installed / "runtime" / "win-x64" / "python.exe").is_file())
            source = root / "中文_outline.md"
            target = root / "result.xmind"
            source.write_text("# 中文_标题\n- A_B\n", encoding="utf-8")
            subprocess.run(
                [str(installed / "mindmap.cmd"), "convert",
                 str(source), str(target), "--strict"],
                check=True, capture_output=True, env=env,
            )
            subprocess.run(
                [str(installed / "mindmap.cmd"), "validate", str(target)],
                check=True, capture_output=True, env=env,
            )
            self.assertEqual(mindmap.validate(target)["title"], "中文_标题")


if __name__ == "__main__":
    unittest.main()

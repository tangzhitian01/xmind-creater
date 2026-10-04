#!/usr/bin/env python3
"""Install the bundled skill without downloading dependencies."""

import argparse
import os
import shutil
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agent", choices=("codex", "claude", "both"), default="codex",
                        help="Agent to install for (default: codex)")
    parser.add_argument("--skills-dir", type=Path,
                        help="Override the skills directory for one agent")
    parser.add_argument("--codex-skills-dir", type=Path,
                        help="Override the Codex skills directory")
    parser.add_argument("--claude-skills-dir", type=Path,
                        help="Override the Claude Code skills directory")
    args = parser.parse_args()
    source = Path(__file__).resolve().parent
    if args.agent == "both" and args.skills_dir is not None:
        parser.error("--skills-dir requires --agent codex or --agent claude")
    if args.agent == "codex" and args.claude_skills_dir is not None:
        parser.error("--claude-skills-dir requires --agent claude or --agent both")
    if args.agent == "claude" and args.codex_skills_dir is not None:
        parser.error("--codex-skills-dir requires --agent codex or --agent both")

    locations = {
        "codex": args.codex_skills_dir or args.skills_dir or Path.home() / ".agents" / "skills",
        "claude": args.claude_skills_dir or args.skills_dir or Path.home() / ".claude" / "skills",
    }
    selected = ("codex", "claude") if args.agent == "both" else (args.agent,)
    destinations = [(agent, (locations[agent] / "markdown-xmind-offline").resolve())
                    for agent in selected]
    if len({destination for _, destination in destinations}) != len(destinations):
        parser.error("Codex and Claude Code destination paths must be different")
    for agent, destination in destinations:
        if destination.exists():
            parser.error("{} destination already exists; move or remove it yourself: {}".format(
                agent, destination))
        if destination == source or source in destination.parents:
            parser.error("Cannot install inside the source package: " + str(destination))

    installed = []
    try:
        for agent, destination in destinations:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(source, destination, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
            installed.append(destination)
            print("{}: {}".format(agent, destination))
    except OSError:
        for destination in installed:
            shutil.rmtree(destination)
        raise


if __name__ == "__main__":
    main()

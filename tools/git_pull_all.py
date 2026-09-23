#!/usr/bin/env python3
"""
Git pull helper — opens a separate macOS Terminal window for each K-Line repo
and runs `git pull origin <branch>` there.

Repos:
  - kline_app      -> master
  - kline-admin    -> master
  - kline-backend  -> master (reference backend)

Usage:
  python3 tools/git_pull_all.py
"""

import shlex
import subprocess
import sys
from pathlib import Path


# Resolve the workspace from this script so it works from any directory.
WORKSPACE = Path(__file__).resolve().parents[1]

# (repo directory, remote branch)
REPOS = [
    (WORKSPACE / "kline_app", "master"),
    (WORKSPACE / "kline-admin", "master"),
    (WORKSPACE / "kline-backend", "master"),
]


def applescript_quote(text: str) -> str:
    """Escape text for an AppleScript double-quoted string literal."""
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


def open_terminal_pull(repo_dir: Path, branch: str) -> None:
    """Open Terminal and pull one repository without blocking this script."""
    shell_cmd = (
        f"cd {shlex.quote(str(repo_dir))} && "
        f"echo '==> git pull origin {branch} in {repo_dir.name}' && "
        f"git pull origin {shlex.quote(branch)}"
    )
    apple_script = (
        'tell application "Terminal"\n'
        "    activate\n"
        "    ignoring application responses\n"
        f"        do script {applescript_quote(shell_cmd)}\n"
        "    end ignoring\n"
        "end tell\n"
        "return\n"
    )
    subprocess.run(
        ["osascript", "-e", apple_script],
        check=True,
        timeout=30,
    )


def main() -> int:
    invalid_repos = [repo_dir for repo_dir, _ in REPOS if not (repo_dir / ".git").is_dir()]
    if invalid_repos:
        for repo_dir in invalid_repos:
            print(
                f"[git_pull_all] missing or invalid repo: {repo_dir}",
                file=sys.stderr,
            )
        return 1

    for repo_dir, branch in REPOS:
        print(
            f"[git_pull_all] opening Terminal for {repo_dir} "
            f"(origin {branch})"
        )
        try:
            open_terminal_pull(repo_dir, branch)
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as error:
            print(
                f"[git_pull_all] could not open Terminal for {repo_dir}: {error}",
                file=sys.stderr,
            )
            return 1

    print("[git_pull_all] done — check each Terminal window for pull results.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

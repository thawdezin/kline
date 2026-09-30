#!/usr/bin/env python3
"""
Git pull helper - updates every K-Line sub-repo from its own remote.

Cross-platform behaviour:
  - macOS           : opens a Terminal window per repo (original behaviour).
  - Windows / Linux : pulls directly in-process and prints a clear report.

Repos:
  - kline_app      -> master
  - kline-admin    -> master
  - kline-backend  -> master (reference backend)

Usage:
  python3 tools/git_pull_all.py          # auto-detects platform
  python3 tools/git_pull_all.py --direct # force in-process pull (even on macOS)
  python3 tools/git_pull_all.py --open   # force Terminal windows (macOS only)

Design notes (why this is not a bare `git pull` loop):
  - `--no-rebase --ff-only` so a diverged repo fails loudly instead of
    opening a merge editor or writing an unreviewed merge commit.
  - Every repo is visited even when an earlier one fails (broken remote,
    missing SSH key, missing checkout) - failures are summarised at the end
    and turn into exit code 1 instead of aborting the run.
  - The working tree is inspected first: this workspace keeps uncommitted
    work and a pull that would clobber it must be visible, not silent.
  - A fetch runs before the pull so a stale remote-tracking ref cannot make
    `--ff-only` refuse a pull that is actually a fast-forward.
  - All output is ASCII and flushed per line, because Python buffers stdout
    while git writes straight to the fd (otherwise the headers interleave
    after the git output) and a cp1252 console chokes on em dashes.
"""

import argparse
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

# Statuses used in the final report.
UPDATED = "updated"
UP_TO_DATE = "up-to-date"
DIRTY_ONLY = "no remote changes"
FAILED = "FAILED"


def log(message: str) -> None:
    """Print a line immediately so it stays in order with git's own output."""
    print(message, flush=True)


def applescript_quote(text: str) -> str:
    """Escape text for an AppleScript double-quoted string literal."""
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


def open_terminal_pull(repo_dir: Path, branch: str) -> None:
    """Open Terminal and pull one repository without blocking this script."""
    shell_cmd = (
        f"cd {shlex.quote(str(repo_dir))} && "
        f"echo '==> git pull origin {branch} in {repo_dir.name}' && "
        f"git pull --no-rebase --ff-only origin {shlex.quote(branch)}"
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


def prepare_repo(repo_dir: Path) -> None:
    """Apply platform-specific repo config before pulling."""
    # On Windows, Git defaults to MAX_PATH; the Codex checkpoint refs under
    # .git/refs/codex/turn-diffs can exceed it and make `git fetch` fail with
    # "did not send all necessary objects". Enable long paths pre-emptively.
    if sys.platform == "win32":
        subprocess.run(
            ["git", "config", "core.longpaths", "true"],
            cwd=repo_dir,
            check=False,
        )


def git(repo_dir: Path, *args: str) -> subprocess.CompletedProcess:
    """Run one git command in a repo, capturing text output for reporting."""
    return subprocess.run(
        ["git", "-C", str(repo_dir), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def dirty_summary(repo_dir: Path) -> str:
    """Compact description of uncommitted work, or '' when the tree is clean."""
    status = git(repo_dir, "status", "--porcelain")
    if status.returncode != 0:
        return ""
    lines = [line for line in status.stdout.splitlines() if line.strip()]
    if not lines:
        return ""
    tracked = sum(1 for line in lines if not line.startswith("??"))
    untracked = len(lines) - tracked
    return f"{tracked} modified, {untracked} untracked file(s)"


def first_error_line(output: str) -> str:
    """Pick the useful line out of git's multi-line failure message.

    Git prints e.g.
        Warning: Identity file ... not accessible
        root@host: Permission denied (publickey).
        fatal: Could not read from remote repository.

        Please make sure you have the correct access rights
        and the repository exists.
    Taking the last line yields the useless advice text, so prefer the
    `fatal:`/`error:` line, then the last line that is not advice.
    """
    lines = [line.strip() for line in (output or "").splitlines() if line.strip()]
    if not lines:
        return "unknown error"
    for line in reversed(lines):
        if line.lower().startswith(("fatal:", "error:")):
            return line
    advice_prefixes = ("please make sure", "and the repository exists")
    useful = [l for l in lines if not l.lower().startswith(advice_prefixes)]
    return useful[-1] if useful else lines[-1]


def direct_pull(repo_dir: Path, branch: str) -> tuple:
    """Pull one repository in-process.

    Returns (status, detail). Never raises for a git failure: a broken remote
    or a missing key must not stop the remaining repos from being updated.
    """
    prepare_repo(repo_dir)

    dirty = dirty_summary(repo_dir)

    # Fetch first so we can report what is actually about to change, and so a
    # stale remote-tracking ref cannot make --ff-only refuse a valid pull.
    fetch = git(repo_dir, "fetch", "origin", branch)
    if fetch.returncode != 0:
        return FAILED, first_error_line(fetch.stderr or fetch.stdout)

    counts = git(repo_dir, "rev-list", "--left-right", "--count", f"HEAD...origin/{branch}")
    ahead = behind = None
    if counts.returncode == 0 and counts.stdout.strip():
        parts = counts.stdout.split()
        if len(parts) == 2:
            ahead, behind = int(parts[0]), int(parts[1])

    if ahead:
        # The remote has nothing to offer and a pull would create a merge
        # commit; refuse rather than rewrite the user's local history.
        return FAILED, f"local branch is {ahead} commit(s) ahead of origin/{branch}; not pulling"

    if behind == 0 or behind is None:
        return (DIRTY_ONLY if dirty else UP_TO_DATE), (dirty or "")

    pull = git(repo_dir, "pull", "--no-rebase", "--ff-only", "origin", branch)
    if pull.returncode != 0:
        return FAILED, first_error_line(pull.stderr or pull.stdout)

    changes = git(repo_dir, "diff", "--stat", "HEAD@{1}..HEAD")
    files = 0
    if changes.returncode == 0 and changes.stdout.strip():
        files = len([l for l in changes.stdout.splitlines() if l.strip()]) - 1

    detail = f"{behind} commit(s), {max(files, 0)} file(s)"
    if dirty:
        detail += f"; local edits present ({dirty})"
    return UPDATED, detail


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Pull every K-Line sub-repo from its own remote."
    )
    parser.add_argument(
        "--direct",
        action="store_true",
        help="force in-process pull on every platform (no Terminal windows)",
    )
    parser.add_argument(
        "--open",
        action="store_true",
        help="force the macOS Terminal-window flow (macOS only)",
    )
    args = parser.parse_args()

    use_terminal = sys.platform == "darwin" and not args.direct
    if args.open:
        if sys.platform != "darwin":
            print(
                "[git_pull_all] --open is macOS-only; falling back to --direct.",
                file=sys.stderr,
            )
        use_terminal = sys.platform == "darwin"

    if use_terminal:
        missing = [rd for rd, _ in REPOS if not (rd / ".git").is_dir()]
        if missing:
            for rd in missing:
                print(f"[git_pull_all] missing or invalid repo: {rd}", file=sys.stderr)
            return 1
        for repo_dir, branch in REPOS:
            log(f"[git_pull_all] opening Terminal for {repo_dir} (origin/{branch})")
            try:
                open_terminal_pull(repo_dir, branch)
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as error:
                print(
                    f"[git_pull_all] could not open Terminal for {repo_dir}: {error}",
                    file=sys.stderr,
                )
                return 1
        log("[git_pull_all] done - check each Terminal window for pull results.")
        return 0

    # Direct (in-process) pull path.
    results = []  # list of (name, status, detail)
    for repo_dir, branch in REPOS:
        log(f"\n===== {repo_dir.name} (origin/{branch}) =====")
        # A missing checkout must not abort the run: the other repos can still
        # be updated, and the final report names exactly what is absent.
        if not (repo_dir / ".git").is_dir():
            status, detail = FAILED, "missing or invalid repo (checkout absent)"
        else:
            status, detail = direct_pull(repo_dir, branch)
        results.append((repo_dir.name, status, detail))
        if status == FAILED:
            print(
                f"[git_pull_all] {repo_dir.name}: {detail}",
                file=sys.stderr,
                flush=True,
            )

    log("\n===== summary =====")
    width = max(len(name) for name, _, _ in results)
    for name, status, detail in results:
        suffix = f" - {detail}" if detail else ""
        log(f"  {name.ljust(width)}  {status}{suffix}")

    failed = [name for name, status, _ in results if status == FAILED]
    if failed:
        print(
            f"\n[git_pull_all] done - {len(failed)} of {len(REPOS)} repo(s) failed: "
            + ", ".join(failed),
            file=sys.stderr,
        )
        return 1
    log(f"\n[git_pull_all] done - all {len(REPOS)} repos up to date.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
# K-Line Workspace — Clone Guide

This workspace is a **monorepo of independent repositories**. The root repo
(`kline`) holds only workspace-level documentation and tooling. The three
project folders are separate Git repositories with their own history and
remotes — they are listed in the root `.gitignore` and are **not** part of
the root repo.

## Repositories

| Folder | Purpose | Repo |
|---|---|---|
| `kline_app/` | Flutter chat client (Android / iOS / macOS / Linux / Windows) | `kline-app.git` (self-hosted) |
| `kline-admin/` | Admin console (web frontend + Go admin API) | `kline-admin.git` (self-hosted) |
| `kline-backend/` | Go chat backend (reference & study) | `kline-backend.git` (self-hosted) |

Sub-repo remotes (self-hosted Git server over SSH):

- `ssh://root@43.133.107.23/home/git/kline/kline-app.git`
- `ssh://root@43.133.107.23/home/git/kline/kline-admin.git`
- `ssh://root@43.133.107.23/home/git/kline/kline-backend.git`

## Clone everything

```bash
# 1) Clone the workspace root (GitHub)
git clone https://github.com/thawdezin/kline.git
cd kline

# 2) Clone the three project repos into it
git clone ssh://root@43.133.107.23/home/git/kline/kline-app.git kline_app
git clone ssh://root@43.133.107.23/home/git/kline/kline-admin.git kline-admin
git clone ssh://root@43.133.107.23/home/git/kline/kline-backend.git kline-backend
```

> SSH access to `43.133.107.23` requires a valid SSH key for the `root`
> user. If you cannot use SSH, ask the repo owner for HTTPS or bundle
> access.

## One-shot helper

After the initial clone of the root repo, `tools/git_pull_all.py` updates
all three sub-repos at once:

```bash
python3 tools/git_pull_all.py
```

## Notes

- Each sub-repo keeps its own `origin`; pushing from inside a sub-repo
  pushes only that project. The root repo pushes workspace docs to GitHub
  (`origin` = `https://github.com/thawdezin/kline.git`).
- Never delete a sub-repo's `.git` folder — that would discard its
  independent history.
- Because the folders are in the root `.gitignore`, `git status` in the
  root repo stays clean even with all three projects checked out.

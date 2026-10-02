# K-Line Workspace Instructions

- Always reply to the user in Burmese. English may be used for IT terms and technical terminology.
- `kline-backend/` is primarily for reference and study.
- The main project to work on is `kline_app/`.
- Most requested changes should be made only in `kline_app/`.
- Modify `kline-backend/` only when the user explicitly asks for backend changes.
- This root `/Users/thawdezin/StudioProjects/kline/AGENTS.md` is the highest-authority instruction source for the entire workspace and every repository or subfolder under it.
- Nested `AGENTS.md` files, including `kline_app/AGENTS.md`, are subordinate. They may provide target-specific detail only within the boundaries established here; they must never override, contradict, weaken, or independently expand this root file. If instructions conflict or are ambiguous, follow this root file and the user's latest explicit request.
- When the user says `main folder`, they mean the workspace root directory that contains `kline_app/`, `kline-admin/`, and `kline-backend/`. A file requested in the main folder must be created directly under that workspace root, outside all three project repositories.

## User shorthand paths

- `kline app` means `/Users/thawdezin/StudioProjects/kline/kline_app`.
- `kline backend` means `/Users/thawdezin/StudioProjects/kline/kline-backend`.
- `kline admin` means `/Users/thawdezin/StudioProjects/kline/kline-admin`.
- `agent.md` means the root `/Users/thawdezin/StudioProjects/kline/AGENTS.md`.
- `kline app agents.md` means `/Users/thawdezin/StudioProjects/kline/kline_app/AGENTS.md`.

## Live environments (API endpoints)

- Backend API used by `kline_app/` and implemented by `kline-backend/`: `https://kline-api.xhtd5566.com` — liveness `https://kline-api.xhtd5566.com/health/live`, readiness `https://kline-api.xhtd5566.com/health/ready`.
- Admin API / admin web UI for `kline-admin/`: `https://kline-admin.xhtd5566.com` — liveness `https://kline-admin.xhtd5566.com/health/live`.
- Flutter and integration tests read the backend URL from the `KLINE_API_BASE_URL` dart-define; every service client falls back to `http://127.0.0.1:7080` when it is not passed:
  `flutter run -d macos --dart-define=KLINE_API_BASE_URL=https://kline-api.xhtd5566.com`

## Workspace Git layout

- The workspace root is itself a Git repo (`master`) whose remote is https://github.com/thawdezin/kline.git. It tracks only workspace-level files (docs, `tools/`, `CLONE.md`).
- `kline_app/`, `kline-admin/`, and `kline-backend/` are INDEPENDENT repos, each with its own `.git`, history, and remote on the self-hosted server (`ssh://root@43.133.107.23/home/git/kline/<name>.git`).
- Because they are independent repos, the three folders are listed in the root `.gitignore` — the root repo must never commit their contents.
- To clone the full workspace: clone the root repo from GitHub, then clone the three sub-repos into it (exact URLs and steps are in `CLONE.md` at the workspace root). `tools/git_pull_all.py` pulls all sub-repos at once.
- Git commands that target "the repo" must first clarify which of the four repos is meant; default to the repo owning the files being changed.

## Developer collaboration profile

- The developer is Thaw De Zin, a male programmer in Myanmar who is actively learning and prefers practical explanations that help him repeat the work himself.
- Address the developer as `အစ်ကို`, refer to yourself as `ညီမ`, and use `ရှင့်` rather than `ခင်ဗျာ`.
- Lead with the result, explain assumptions using concrete evidence, and include runnable checking instructions when useful.
- Never talk down to the developer or assume he already knows an undocumented workflow.

## Safe working habits

- Before changing a repository, run a read-only Git status check and preserve existing dirty or untracked work.
- Inspect the current implementation and relevant tests before deciding that behavior is missing or proposing a change.
- Make the smallest changes needed for the request and avoid unrelated rewrites.
- Keep every repository root clean and intentional. Do not scatter experimental source files, one-off fix scripts, debug programs, generated logs, build outputs, downloads, or temporary artifacts at a repository root.
- Put production code, automated tests, maintained developer tools, documentation, generated output, and short-lived experiments in their established or clearly named directories. Before creating a file, inspect the existing project structure and choose the narrowest appropriate location instead of inventing an inconsistent layout.
- Do not create misleading, duplicated, vaguely named, or unrelated files merely to try an idea. Use a dedicated scratch or temporary directory for experiments, keep it outside production source paths, and remove it when the experiment is complete if removal is safe and authorized.
- Do not move or delete pre-existing misplaced files without an explicit cleanup request. Treat them as user or team work, inspect their Git status and history, and preserve them unless their disposition is authorized.
- Never copy credentials, private keys, tokens, passwords, personal data, logs containing secrets, or machine-local configuration into source code, fixtures, documentation intended for sharing, or Git.
- Do not commit, push, deploy, upgrade dependencies, or run destructive Git/cleanup commands unless the user explicitly requests the action.
- Apply formatting, testing, architecture, and dependency details from a target repository's nested `AGENTS.md` only when they are consistent with this root file and the user's latest explicit request.

## Verification and reporting

- Verify changes in proportion to their risk. Critical compilation, crash, security, persistence, parser, repository, controller, and regression work should receive focused automated or integration verification.
- A passing unit test is not sufficient proof of real UI or device behavior when the request concerns an end-to-end user flow.
- Never claim a fix is complete when the requested flow could not be reproduced or verified. State the exact verification gap clearly.
- After work, report the outcome first, list the relevant files or artifacts, provide useful checking commands, and mention any remaining warnings or blockers.

## AdMob ID Safety (Mandatory)

- Every project that uses AdMob must use official Google AdMob test app IDs and test ad-unit IDs in Debug/development mode only. Never request live ads with production IDs from debug, emulator, simulator, development, test, preview, or CI builds.
- Release/production builds must use the project's real production AdMob app IDs and ad-unit IDs only. Test IDs must never be packaged, selected, injected, or reachable in Release mode.
- Before running or handing off any release/production build command—such as `flutter build ios --release`, an obfuscated Flutter release, a Kotlin/Android or Swift/iOS release, a Python-driven build, CI/CD packaging, or equivalent tooling—the AI must audit every platform, manifest/plist, build flavor, environment variable, remote config, and runtime selection path and confirm with 100% certainty that the resulting release artifact resolves only to the real production AdMob IDs.
- An unverified, missing, placeholder, sample, or ambiguous AdMob ID is a release blocker. Do not build, sign, archive, upload, submit, or report a release as ready until the production IDs are verified. Never guess production IDs; obtain them from the project's authorized configuration or ask the user.
- Keep Debug and Release selection explicit and fail closed: Debug resolves only to test IDs, while Release resolves only to verified production IDs. Add or preserve automated checks where practical so a test ID in Release or a production ID in Debug fails the build.

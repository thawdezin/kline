# K-Line Setup Guide — Step by Step (No questions needed)

This guide is written for team members who do not know programming yet.
Every command is copy → paste. Follow the steps in order, do not skip any.

**Success criterion:** the K-Line desktop app window opens on your own computer (OS)
and the login screen is visible — setup is done.

> **Verified:** every step below was run and checked on Windows 11
> (protoc, Rust build, Android cross-build, all the way to `flutter run -d windows`).
> The macOS / Linux commands follow the official docs plus this project's real
> requirements — they could not be executed on this machine (Windows). If anything
> fails there, report it as described in Section 9.

---

## 0. Before you start

| Item | Requirement |
|---|---|
| RAM | **At least 16 GB** (Android build uses 8 GB for Gradle) |
| Disk space | **30 GB free** (Visual Studio ~8 GB, Android Studio + SDK ~12 GB, Flutter ~3 GB) |
| Internet | Required (Flutter SDK, Rust crates, GitHub downloads) |
| OS | Windows 11 / macOS / Linux (pick one) |
| Account | GitHub account (to clone the root repo) |

> On Windows use **PowerShell** (not Command Prompt). On macOS/Linux use the Terminal.

---

## 1. Install software per OS (do only one section)

### A. Windows 11 (PowerShell — admin not required)

```powershell
# 1) Git
winget install --id Git.Git -e --source winget

# 2) Visual Studio 2022 (with the C++ workload Flutter needs for Windows desktop)
winget install --id Microsoft.VisualStudio.2022.Community -e --source winget --override "--add Microsoft.VisualStudio.Workload.NativeDesktop --passive --norestart"

# 3) Rust (to build the K-Line encryption library)
winget install --id Rustlang.Rustup -e --source winget

# 4) protoc (required by the Rust build — without it the build fails)
winget install --id Google.Protobuf -e --source winget

# 5) Android Studio (only if you will run on an Android phone; not needed for desktop)
winget install --id Google.AndroidStudio -e --source winget
```

> After each install, **close and reopen** PowerShell so PATH is refreshed.

Flutter has no official winget package, so install it with git:

```powershell
git clone -b stable https://github.com/flutter/flutter.git C:\dev\flutter
[Environment]::SetEnvironmentVariable("Path", [Environment]::GetEnvironmentVariable("Path","User") + ";C:\dev\flutter\bin", "User")
```

**Close and reopen** PowerShell, then continue. The first run downloads the Dart SDK
by itself (this can take a while):

```powershell
flutter --version
flutter doctor
```

**Expected `flutter doctor` output (for running on Windows desktop):**

```
[√] Flutter (Channel stable, ...)
[√] Windows Version
[√] Visual Studio - develop Windows apps
[√] Connected device
[√] Network resources
```

If `Visual Studio - develop Windows apps` is not `[√]` → scroll down to Troubleshooting.
`Android toolchain` showing `[!]` does **not** block desktop runs — it matters only for Android.

### B. macOS

```bash
# 1) Full Xcode (install "Xcode" from the App Store first)
sudo xcode-select -s /Applications/Xcode.app/Contents/Developer
sudo xcodebuild -license accept

# 2) Command Line Tools (if Xcode did not install them)
xcode-select --install

# 3) Homebrew (if you do not have it)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 4) protoc + CocoaPods (for Flutter iOS/macOS plugins)
brew install protobuf
sudo gem install cocoapods

# 5) Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
source "$HOME/.cargo/env"

# 6) Flutter
git clone -b stable https://github.com/flutter/flutter.git ~/development/flutter
echo 'export PATH="$HOME/development/flutter/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# 7) verify
flutter --version
flutter doctor
```

> To run on an Android phone, install Android Studio from https://developer.android.com/studio
> and add NDK `29.0.14206865` in the SDK Manager.
> The same commands work on Apple Silicon (M1/M2/M3) and Intel.

### C. Linux (Ubuntu / Debian)

```bash
sudo apt update
sudo apt install -y git curl unzip xz-utils zip clang cmake ninja-build \
  pkg-config libgtk-3-dev liblzma-dev protobuf-compiler

# Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
source "$HOME/.cargo/env"

# Flutter
git clone -b stable https://github.com/flutter/flutter.git ~/development/flutter
echo 'export PATH="$HOME/development/flutter/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# verify
flutter --version
flutter doctor
```

> To run on an Android phone, download and extract the Android Studio tar.gz
> (https://developer.android.com/studio) and add NDK `29.0.14206865` in the SDK Manager.
> On Fedora/Arch install the same set with your package manager:
> `protobuf-compiler`, `gtk3-devel`, `clang`, `cmake`, `ninja` (essentially identical).

---

## 2. Clone the source code

**One-time SSH key setup** (needed to access the self-hosted git server):

```powershell
# Windows (PowerShell)
ssh-keygen -t ed25519 -f $env:USERPROFILE\.ssh\id_ed25519 -N '""'
type $env:USERPROFILE\.ssh\id_ed25519.pub
```

> If you already have a key and see `Overwrite (y/n)?`, press `n` — keep the existing key
> (a new key would have to be registered on the server again). Send the whole text from
> the `.pub` file.

```bash
# macOS / Linux
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519 -N ''
cat ~/.ssh/id_ed25519.pub
```

After running `ssh-keygen`, send the printed `ssh-ed25519 AAAA... user@machine` line to
**the repo owner**. Once the key is registered you can continue
(the Step 3 clone commands fail until then).

**Get the source code** (into the workspace root — adjust the path to your machine):

```powershell
# Windows
cd C:\dev
git clone https://github.com/thawdezin/kline.git
cd kline
git clone ssh://root@43.133.107.23/home/git/kline/kline-app.git kline_app
```

```bash
# macOS / Linux
cd ~/development
git clone https://github.com/thawdezin/kline.git
cd kline
git clone ssh://root@43.133.107.23/home/git/kline/kline-app.git kline_app
```

- On the first SSH connection, if asked `Are you sure you want to continue connecting (yes/no)?` type **`yes`**.
- **`kline_app` is the one you must have** to run the desktop app — without it there is no app.
- `kline-admin` (admin web) and `kline-backend` (Go API, for study) are not needed now — add them later if required:

```bash
git clone ssh://root@43.133.107.23/home/git/kline/kline-admin.git kline-admin
git clone ssh://root@43.133.107.23/home/git/kline/kline-backend.git kline-backend
python3 tools/git_pull_all.py   # later updates (only when all three exist)
```

Details are in `CLONE.md`. **Never delete `kline_app/.git`** (that destroys all history).

---

## 3. Build the K-Line encryption (Rust) library — **required before running**

On startup the app loads the `kline_signal` native library (Signal encryption FFI).
If you do not build it first, the app window opens and then crashes / fails to start.
(Build artifacts are not in git — every machine builds its own.)

```powershell
# Windows (PowerShell)
cd C:\dev\kline\kline_app\native\kline_signal
cargo build --release
cd ..\..
```

```bash
# macOS / Linux
cd ~/development/kline/kline_app/native/kline_signal
cargo build --release
cd ../../..
```

- The first run downloads and compiles crates from the network; it can take **5–15 minutes**.
- Afterwards `native/kline_signal/target/release/` must contain
  `kline_signal.dll` (Windows) / `libkline_signal.dylib` (macOS) / `libkline_signal.so` (Linux).
- If you get `Could not find protoc` → go to Troubleshooting (this appears when the protoc
  install in Section 1 was skipped).

---

## 4. Run the desktop app (the success step)

**Always run from inside the `kline_app` folder** (the library path depends on it):

```powershell
# Windows
cd C:\dev\kline\kline_app
flutter pub get
flutter run -d windows
```

```bash
# macOS
cd ~/development/kline/kline_app
flutter pub get
flutter run -d macos
```

```bash
# Linux
cd ~/development/kline/kline_app
flutter pub get
flutter config --enable-linux-desktop
flutter run -d linux
```

**What success looks like:** a window titled `K-Line` opens and the login screen appears — **done.**
To stop, press `Ctrl + C` in the terminal (closing the app window directly also works).

### 5. FINAL CHECK (verify it yourself)

| # | Command | Expected result |
|---|---|---|
| 1 | `flutter doctor` | `Visual Studio` / `Flutter` show `[√]` |
| 2 | `Test-Path native\kline_signal\target\release\kline_signal.dll` (Windows, run inside `kline_app`) | `True` |
| 3 | `flutter run -d windows` | K-Line window + login screen |
| 4 | In the log output | API calls succeed (live backend `https://kline-api.xhtd5566.com`) |

> The app connects directly to the live backend (hard-coded in the code) — no local server needed.
> Registration/login problems are not setup problems — report them as described in Section 9.

---

## 6. Run on Android Studio / a phone (optional)

Android needs one extra step compared to desktop — **if `libkline_signal.so` is not
cross-built for the phone, the app fails at startup** (it is not committed to git):

**(1) Install the NDK** — Android Studio → `Settings → Languages & Frameworks → Android SDK → SDK Tools`
→ `NDK (Side by side)` → tick **`29.0.14206865`** → Apply.
(This version is pinned by the project — do not change it.)

**(2) Build + copy the `.so`:**

```powershell
# Windows (PowerShell)
$ndk = "$env:LOCALAPPDATA\Android\Sdk\ndk\29.0.14206865\toolchains\llvm\prebuilt\windows-x86_64\bin"
$env:PATH = "$ndk;$env:PATH"
$env:CARGO_TARGET_AARCH64_LINUX_ANDROID_LINKER = "$ndk\aarch64-linux-android29-clang.cmd"
cd C:\dev\kline\kline_app\native\kline_signal
rustup target add aarch64-linux-android
cargo build --release --target aarch64-linux-android
New-Item -ItemType Directory -Force ..\..\android\app\src\main\jniLibs\arm64-v8a | Out-Null
Copy-Item target\aarch64-linux-android\release\libkline_signal.so ..\..\android\app\src\main\jniLibs\arm64-v8a\ -Force
cd ..\..
```

```bash
# macOS / Linux (adjust ANDROID_HOME if your SDK lives elsewhere)
export ANDROID_HOME="$HOME/Library/Android/sdk"        # Linux: $HOME/Android/Sdk
NDK_BIN=$(ls -d "$ANDROID_HOME/ndk/29.0.14206865/toolchains/llvm/prebuilt/"*)/bin
export PATH="$NDK_BIN:$PATH"
export CARGO_TARGET_AARCH64_LINUX_ANDROID_LINKER="$NDK_BIN/aarch64-linux-android29-clang"
cd ~/development/kline/kline_app/native/kline_signal
rustup target add aarch64-linux-android
cargo build --release --target aarch64-linux-android
mkdir -p ../../android/app/src/main/jniLibs/arm64-v8a
cp target/aarch64-linux-android/release/libkline_signal.so ../../android/app/src/main/jniLibs/arm64-v8a/
cd ../../..
```

> If your SDK is not at `C:\Users\<name>\AppData\Local\Android\Sdk`, check `sdk.dir`
> in `kline_app/android/local.properties`.
> If you skip putting NDK `clang` on PATH you get `failed to find tool "clang.exe"`.

**(3) Run it** — either way works:

```powershell
# Option 1 — from the terminal (phone connected with USB debugging on)
cd C:\dev\kline\kline_app
flutter devices
flutter run -d <device-id>
```

```
Option 2 — Android Studio:
File → Open → pick kline_app/android → wait for Gradle sync → press Run ▶ at the top
(the phone must appear in the device list)
```

- The build works without `google-services.json` (gradle checks whether it exists) — not needed for now.
- `flutter clean` / `git clean` also deletes the `.so` in `jniLibs` → **repeat step (2)**.

---

## 7. Rules to follow from `AGENTS.md` (root `AGENTS.md` + `kline_app/AGENTS.md`)

1. **The main project is `kline_app/`** — `kline-backend/` is reference/study only. Most changes belong in `kline_app/`.
2. **Live endpoints** — the app has the API `https://kline-api.xhtd5566.com` hard-coded (nothing to change during setup). Admin web = `https://kline-admin.xhtd5566.com`. To test against your own local backend pass `--dart-define=KLINE_API_BASE_URL=http://127.0.0.1:7080` (without it, clients fall back to `http://127.0.0.1:7080`).
3. **Git layout** — workspace root repo (GitHub) + 3 sub-repos (self-hosted); **all 4 are independent repos**. The sub-repos are listed in the root `.gitignore` — root `git status` must stay clean. Never delete `kline_app/.git`.
4. **Never commit / push without permission** — finish the work, then report. Before running commands, check `git status` and `git diff` and do not touch other people's unfinished work.
5. **Quality gates (when changing code)** — run `dart format` → `flutter analyze --no-pub` → `flutter test` before calling the work done. Do not hide test failures.
6. **Versions that must not change** — Gradle wrapper `9.4.1` and Android NDK `29.0.14206865` (kline_app/AGENTS.md).
7. **Never commit** secrets/keys/tokens, `android/local.properties`, `.dart_tool`, build output, or configs containing your machine's paths.
8. **Keep repo roots clean** — no experiment scripts, logs, or downloads at the repo root (use a scratch/proper folder). Do not delete other people's pre-existing misplaced files without an explicit cleanup request.
9. **UI/code convention** — the Flutter app is GetX only: views are `StatelessWidget`/`GetView` (no `StatefulWidget`, no `setState`), state lives in `GetxController` + `Obx`, features live under `lib/app/modules/<feature>/`.
10. **How to report** — outcome first, list of changed files, how to check it, and any remaining warnings/blockers stated honestly (never call unfinished work "done").

---

## 8. Troubleshooting (most common)

| Problem / error | Fix |
|---|---|
| `'flutter' is not recognized` | **Close and reopen** PowerShell/Terminal. If still failing, add the Flutter `bin` folder path to PATH |
| `flutter doctor` shows `Visual Studio` `[✗]` | Open the VS installer → add "Desktop development with C++": `winget upgrade --id Microsoft.VisualStudio.2022.Community --override "--add Microsoft.VisualStudio.Workload.NativeDesktop --passive --norestart"` |
| cargo: `Could not find protoc` / `Protobufs in src are valid: ... NotFound` | Windows: `winget install --id Google.Protobuf -e` then restart the terminal. macOS: `brew install protobuf`. Linux: `sudo apt install protobuf-compiler` |
| App fails at startup / `Unable to load dynamic library` / `kline_signal.dll` not found | You skipped `cargo build --release` in Section 3 — build inside `kline_app/native/kline_signal`. Also **run `flutter run` from the `kline_app` folder** |
| Android build: `failed to find tool "clang.exe"` / `linker not found` | The env settings from Section 6 (2) (`PATH`, `CARGO_TARGET_AARCH64_LINUX_ANDROID_LINKER`) are not set — set them exactly as shown, then build |
| App crashes on the phone / `dlopen failed: library not found` | The `.so` was not copied to `android/app/src/main/jniLibs/arm64-v8a/` — redo Section 6 (2) |
| `host key verification failed` (SSH clone) | Type `yes` on the first connection. Otherwise check whether your public key was registered by the repo owner |
| `Permission denied (publickey)` | Your SSH key is not on the server yet — send it as in Section 2 |
| Gradle `OutOfMemoryError` / very slow build | Needs 16 GB RAM. `android/gradle.properties` already has `-Xmx8G` — close other apps if RAM is low |
| Android Studio: `SDK not found` / `sdk.dir` error | The SDK is not installed yet — install platform + NDK via SDK Manager and check `sdk.dir` in `android/local.properties` |
| App runs but network/API errors | Open `https://kline-api.xhtd5566.com/health/live` in a browser (should return 200). Check proxy/VPN settings |
| CocoaPods error on iOS/macOS builds | macOS: `sudo gem install cocoapods` and check `pod --version` |
| `flutter test` failures | Possibly network tests needing the local backend (`127.0.0.1:7080`) — not a setup problem; mention it in your report |

---

## 9. What to do next / how to report

When setup is done, run these commands and send the results as screenshot or text:

```powershell
flutter doctor -v
git -C kline_app log --oneline -5
git -C kline_app status
```

Your report should contain:
1. OS + version (e.g. Windows 11 22H2)
2. Full `flutter doctor -v` output
3. Which step succeeded (e.g. "K-Line window opened")
4. If there is an error: the full error text + the command that produced it

For further questions or problems, report the way root `AGENTS.md` asks: result first,
list of files, check commands, remaining blockers.

---

### Other docs to read

- `CLONE.md` — details on cloning/pulling all 4 repos
- `AGENTS.md` (root) — all main workspace rules
- `kline_app/AGENTS.md` — code style, quality gates, version pins
- `KLINE_PROJECT_HANDBOOK_MM.md` — project details (Burmese)
- `SETUP` Burmese version: `KLINE_SETUP_MM.md`
- `kline_app/doc/` — design/architecture docs (EN/ZH)

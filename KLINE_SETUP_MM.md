# K-Line Setup Guide — အဆင့်ဆင့် (မေးခွန်းမလို)

ဒီ guide ကို programming သိပ်မသိသေးတဲ့ team member တွေအတွက် ရေးထားတာပါ။ command တွေအားလုံးကို copy → paste ရုံပါပဲ။
အဆင့်တွေကို အစဉ်လိုက် လုပ်ပါ၊ ကြားက မချန်ပါနဲ့။

**အောင်မြင်မှု သတ်မှတ်ချက် (success criterion):** မိမိ ကွန်ပျူတာ (OS) ပေါ်မှာ K-Line desktop app ရဲ့ window ပွင့်ပြီး login screen မြင်ရရင် — setup ပြီးပါပြီ။

> **Verified:** Windows 11 အတွက် အောက်ပါ အဆင့်အားလုံးကို ညီမ ကိုယ်တိုင် run ပြီး အောင်မြင်ကြောင်း စစ်ဆေးထားပါတယ် (protoc, Rust build, Android cross-build, `flutter run -d windows` အထိ)။
> macOS / Linux အတွက် command တွေက official docs + ဒီ project ရဲ့ တကယ့် requirement တွေအတိုင်း ရေးထားတာ — ဒီစက် (Windows) မှာ မစမ်းနိုင်သေးဘူး။ ပြဿနာတက်ရင် အဆင့် ၉ ကို ကြည့်ပါ။

---

## 0. ကြိုတင်ပြင်ဆင်ရန်

| အချက် | လိုအပ်ချက် |
|---|---|
| RAM | **16 GB အနည်းဆုံး** (Android build က Gradle 8 GB memory သုံးတယ်) |
| Disk space | **30 GB လွတ်** (Visual Studio ~8 GB, Android Studio + SDK ~12 GB, Flutter ~3 GB) |
| Internet | ရှိရမယ် (Flutter SDK, Rust crates, GitHub ကနေ download လုပ်ရမယ်) |
| OS | Windows 11 / macOS / Linux (တစ်ခုကိုသာ ရွေးပါ) |
| Account | GitHub account (root repo clone ရန်) |

> Windows မှာ PowerShell သုံးပါ (Command Prompt မဟုတ်)။ macOS/Linux မှာ Terminal သုံးပါ။

---

## 1. OS အလိုက် software install (တစ်ခုကိုသာ လုပ်ပါ)

### A. Windows 11 (PowerShell — admin မဟုတ်လည်း ရတယ်)

```powershell
# 1) Git
winget install --id Git.Git -e --source winget

# 2) Visual Studio 2022 (Flutter Windows desktop အတွက် C++ workload နဲ့)
winget install --id Microsoft.VisualStudio.2022.Community -e --source winget --override "--add Microsoft.VisualStudio.Workload.NativeDesktop --passive --norestart"

# 3) Rust (K-Line encryption library ကို build ဖို့)
winget install --id Rustlang.Rustup -e --source winget

# 4) protoc (Rust build မှာ မဖြစ်မနေ လိုတယ် — မပါရင် build fail)
winget install --id Google.Protobuf -e --source winget

# 5) Android Studio (Android phone မှာ run ချင်မှ လို; desktop run အတွက် မလို)
winget install --id Google.AndroidStudio -e --source winget
```

> တစ်ခုခု install ပြီးရင် PowerShell ကို **ပိတ်ပြီး ပြန်ဖွင့်ပါ** (PATH ပြောင်းဖို့)။

Flutter — winget မှာ official package မရှိလို့ git နဲ့ install ရတယ်:

```powershell
git clone -b stable https://github.com/flutter/flutter.git C:\dev\flutter
[Environment]::SetEnvironmentVariable("Path", [Environment]::GetEnvironmentVariable("Path","User") + ";C:\dev\flutter\bin", "User")
```

PowerShell **ပိတ်ပြီး ပြန်ဖွင့်**ပြီးမှ ဆက်လုပ်ပါ။ ပထမဆုံး run မှာ Flutter က Dart SDK ကို ကိုယ်တိုင် download လုပ်တယ် (ကြာနိုင်တယ်):

```powershell
flutter --version
flutter doctor
```

**`flutter doctor` ရလဒ် expected (Windows desktop run အတွက်):**

```
[√] Flutter (Channel stable, ...)
[√] Windows Version
[√] Visual Studio - develop Windows apps
[√] Connected device
[√] Network resources
```

`Visual Studio - develop Windows apps` က `[√]` မဟုတ်ရင် → ဆင်းပြီး (Troubleshooting) ကို ကြည့်ပါ။
`Android toolchain` `[!]` ဖြစ်နေတာ desktop run ကို မတားဘူး — Android section အတွက်ပဲ။

### B. macOS

```bash
# 1) Xcode full version (App Store မှာ "Xcode" install ပြီးရင်)
sudo xcode-select -s /Applications/Xcode.app/Contents/Developer
sudo xcodebuild -license accept

# 2) Command Line Tools (Xcode ထဲမပါရင်)
xcode-select --install

# 3) Homebrew (မရှိသေးရင်)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 4) protoc + CocoaPods (Flutter iOS/macOS plugin တွေအတွက်)
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

> Android phone run လိုရင် Android Studio ကို https://developer.android.com/studio ကနေ install ပြီး SDK Manager ထဲမှာ NDK `29.0.14206865` ကို ထည့်ပါ။
> Apple Silicon (M1/M2/M3) နဲ့ Intel နှစ်ခုစလုံးအတွက် command တူတယ်။

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

> Android phone run လိုရင် Android Studio tar.gz (https://developer.android.com/studio) ကို download ထုတ်ပြီး SDK Manager ထဲမှာ NDK `29.0.14206865` ထည့်ပါ။
> Fedora/Arch ဆိုရင် package manager နဲ့ `protobuf-compiler`, `gtk3-devel`, `clang`, `cmake`, `ninja` တွေ ထည့်ပါ (အဓိက တူတယ်)။

---

## 2. Source code clone

**SSH key တစ်ခါတည်း ပြင်ဆင်ရန်** (self-hosted git server ကို access ဖို့):

```powershell
# Windows (PowerShell)
ssh-keygen -t ed25519 -f $env:USERPROFILE\.ssh\id_ed25519 -N '""'
type $env:USERPROFILE\.ssh\id_ed25519.pub
```

> key ရှိပြီးသားဆို `Overwrite (y/n)?` ပေါ်ရင် `n` ရိုက်ပါ — ရှိပြီးသား key ကို ဆက်သုံးရမယ် (အသစ်ဖန်တီးရင် server ထဲ ပြောင်းထည့်ရမည်)။ key ကို `.pub` file ထဲက text အပြည့် ပို့ပါ။

```bash
# macOS / Linux
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519 -N ''
cat ~/.ssh/id_ed25519.pub
```

`ssh-keygen` ကို run ပြီးရင် ထွက်လာတဲ့ `ssh-ed25519 AAAA... user@machine` တန်းကို **repo owner (အစ်ကို) ဆီ ပို့ပါ**။ key တင်ပြီးတာနဲ့ အောက်ဆက်လုပ်လို့ရပါပြီ (key မတင်ရသေးရင် အဆင့် 3 clone command တွေ fail ဖြစ်မယ်)။

**Source code ယူရန်** (workspace root ကို ခေါ်ပါ — နေရာပေါ်မူတည်ပြီး ကွဲနိုင်တယ်):

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

- ပထမဆုံး SSH connection မှာ `Are you sure you want to continue connecting (yes/no)?` ဆိုရင် **`yes`** ရိုက်ပါ။
- **`kline_app` ဆိုတာ desktop app run ဖို့ လိုအပ်ဆုံး** — ဒါမပါရင် app မရနိုင်ဘူး။
- `kline-admin` (admin web) နဲ့ `kline-backend` (Go API, လေ့လာရန်) က အခုမလို — လိုအပ်မှ ထပ်ထည့်ပါ:

```bash
git clone ssh://root@43.133.107.23/home/git/kline/kline-admin.git kline-admin
git clone ssh://root@43.133.107.23/home/git/kline/kline-backend.git kline-backend
python3 tools/git_pull_all.py   # နောက်ပိုင်း update ယူရန် (သုံးခုလုံးရှိမှ)
```

အသေးစိတ်က `CLONE.md` မှာ။ **`kline_app/.git` ကို ဘယ်တော့မှ မဖျက်ပါနဲ့** (history အကုန်ပျက်မယ်)။

---

## 3. K-Line encryption (Rust) library build — **run မတိုင်ခင် မဖြစ်မနေ**

App က startup မှာ `kline_signal` native library ကို load တယ် (Signal encryption FFI)။
Build မလုပ်ရသေးရင် app window ပွင့်ပြီး crash / startup fail ဖြစ်မယ်။ (build artifact တွေကို git ထဲ မထားဘူး — ကိုယ့်စက်မှာ ကိုယ် build ရတယ်)

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

- ပထမဆုံးအကြိမ်က network ကနေ crates တွေ download + compile လုပ်ရတာ **5–15 မိနစ်** ကြာနိုင်တယ်။
- ပြီးရင် `native/kline_signal/target/release/` ထဲမှာ `kline_signal.dll` (Windows) / `libkline_signal.dylib` (macOS) / `libkline_signal.so` (Linux) ရှိရမယ်။
- `Could not find protoc` error တက်ရင် → ဆင်းပြီး Troubleshooting ကို ကြည့်ပါ (Section 1 က protoc install ကို လွတ်သွားရင် ဒီ error ပေါ်တယ်)။

---

## 4. Desktop app run (အောင်မြင်မှု အဆင့်)

**အမြဲတမ်း `kline_app` folder ထဲကနေ run ပါ** (library path က folder ပေါ် မူတည်တယ်):

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

**အောင်မြင်မှု ပုံ:** `K-Line` ဆိုတဲ့ window ပွင့်ပြီး login screen ပေါ်လာရင် — **ပြီးပါပြီ။**
ရပ်ချင်ရင် terminal ထဲမှာ `Ctrl + C` နှိပ်ပါ (app window ကို တိုက်ရိုက် ပိတ်လည်း ရတယ်)။

### 5. FINAL CHECK (ကိုယ့်ဘာသာ အတည်ပြုရန်)

| # | Command | ရလဒ် |
|---|---|---|
| 1 | `flutter doctor` | `Visual Studio` / `Flutter` `[√]` |
| 2 | `Test-Path native\kline_signal\target\release\kline_signal.dll` (Windows, `kline_app` ထဲမှာ run) | `True` |
| 3 | `flutter run -d windows` | K-Line window + login screen |
| 4 | ထွက်လာတဲ့ log ထဲမှာ | `[INFO] ... connected` / API call တွေ အဆင်ပြေ (live backend `https://kline-api.xhtd5566.com`) |

> App က live backend ကို တိုက်ရိုက် ချိတ်ထားတယ် (code ထဲ hard-code) — local server ထောင်စရာ မလိုဘူး။
> Account ဖွင့်ခြင်း/login ပြဿနာ ကျရင် setup ပြဿနာမဟုတ်ဘူး — Section 9 အတိုင်း အစီရင်ခံပါ။

---

## 6. Android Studio / phone မှာ run (optional)

Android run က desktop run ထက် အဆင့်တစ်ခု ထပ်လိုတယ် — **phone အတွက် `libkline_signal.so` ကို cross-build ပြီး မထည့်ရသေးရင် app startup မှာ fail ဖြစ်မယ်** (ဂျစ်တ်ထဲမှာ မပါဘူး):

**(1) NDK ထည့်ရန်** — Android Studio → `Settings → Languages & Frameworks → Android SDK → SDK Tools` → `NDK (Side by side)` → **`29.0.14206865`** ကို tick → Apply။ (ဒီ version ကို project မှာ pin ထားတယ် — မပြောင်းပါနဲ့)

**(2) `.so` build + copy:**

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
# macOS / Linux (SDK နေရာ မတူရင် ANDROID_HOME ပြောင်းပါ)
export ANDROID_HOME="$HOME/Library/Android/sdk"        # Linux ဆို: $HOME/Android/Sdk
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

> SDK က `C:\Users\<name>\AppData\Local\Android\Sdk` မှာ မရှိရင် `kline_app/android/local.properties` ထဲက `sdk.dir` ကို ကြည့်ပါ။
> NDK ထဲက `clang` ကို PATH ထည့်ရတာ မထည့်ရင် `failed to find tool "clang.exe"` error တက်တယ်။

**(3) run ရန်** — နှစ်နည်းလုံး ရတယ်:

```powershell
# နည်း ၁ — terminal ကနေ (USB debugging ဖွင့်ထားတဲ့ ဖုန်း ချိတ်ပြီး)
cd C:\dev\kline\kline_app
flutter devices
flutter run -d <device-id>
```

```
နည်း ၂ — Android Studio:
File → Open → kline_app/android ကို ရွေး → Gradle sync စောင့် → အပေါ်က Run ▶ နှိပ်
(ဖုန်းကို device list ထဲ ပေါ်နေရမယ်)
```

- `google-services.json` မထည့်လည်း build ရတယ် (gradle က ရှိ/မရှိ စစ်ထားတယ်) — အခုအတွက် လိုမလို။
- `flutter clean` / `git clean` လုပ်ရင် `jniLibs` ထဲက `.so` ပါ ပျက်နိုင်တယ် → **(2) ကို ပြန်လုပ်ပါ**။

---

## 7. `AGENTS.md` ကနေ လိုက်နာရမယ့် အချက်များ (workspace root `AGENTS.md` + `kline_app/AGENTS.md`)

1. **အဓိက project က `kline_app/`** — `kline-backend/` က reference/လေ့လာရန်သာ။ ပြောင်းလဲမှု အများစုက `kline_app/` ထဲမှာပဲ။
2. **Live endpoints** — app က API `https://kline-api.xhtd5566.com` ကို hard-code ထားတယ် (setup ထဲမှာ ပြောင်းစရာ မလို)။ Admin web = `https://kline-admin.xhtd5566.com`။ ကိုယ့် local backend နဲ့ စမ်းချင်ရင် `--dart-define=KLINE_API_BASE_URL=http://127.0.0.1:7080` ထည့်ရတယ် (မထည့်ရင် client တွေ `http://127.0.0.1:7080` ကို fallback ပြန်သုံးတယ်)။
3. **Git layout** — workspace root repo (GitHub) + sub-repo ၃ ခု (self-hosted)၊ **၄ ခုလုံး သီးခြား repo**။ sub-repo တွေက root `.gitignore` ထဲမှာ — root `git status` က clean ဖြစ်နေရမယ်။ `kline_app/.git` မဖျက်ရ။
4. **commit / push ကို ခွင့်ပြုချက်မပါဘဲ မလုပ်ရ** — work ပြီးမှ report ပေးပါ။ (ညီမ ပါ) command တွေ run မတိုင်ခင် `git status` နဲ့ `git diff` ကြည့်ပြီး သူများရဲ့ မပြီးသေးတဲ့ work ကို မထိပါနဲ့။
5. **Quality gates (code ပြင်ရင်)** — `dart format` → `flutter analyze --no-pub` → `flutter test` run ပြီးမှ ပြီးတယ်လို့ ပြောရ။ test fail တွေကို မဝှက်ရ။
6. **မပြောင်းရသော versions** — Gradle wrapper `9.4.1` နဲ့ Android NDK `29.0.14206865` (kline_app/AGENTS.md)။
7. **commit ထဲ မထည့်ရသောအရာများ** — secret/key/token, `android/local.properties`, `.dart_tool`, build output, ကိုယ့်စက်ရဲ့ path ပါတဲ့ config။
8. **repo root ကို clean ထားရ** — experiment script, log, download တွေ root မှာ မထားနဲ့ (scratch folder / proper folder ထဲမှာ)။ သူများရဲ့ ရှိပြီးသား မသင့်တဲ့ file တွေကို cleanup request မပါဘဲ မဖျက်ရ။
9. **UI/code convention** — Flutter app က GetX ပဲ: view တွေက `StatelessWidget`/`GetView` (StatefulWidget, `setState` မသုံးရ), state က `GetxController` + `Obx`၊ module တွေက `lib/app/modules/<feature>/` အောက်။
10. **report ပုံ** — ရလဒ်အရင်၊ ပြင်ထားတဲ့ file တွွ၊ စစ်ဆေးနည်း command, ကျန်တဲ့ warning/blocker တွေကို အမှန်တရားအတိုင်း ပြော (မပြီးတာကို "ပြီးပြီ" မပြောရ)။

---

## 8. Troubleshooting (အမေးများဆုံး)

| ပြဿနာ / error | ဖြေရှင်းနည်း |
|---|---|
| `'flutter' is not recognized` | PowerShell/Terminal **ပိတ်ပြီး ပြန်ဖွင့်**ပါ။ မရရင် Flutter `bin` folder path ကို PATH ထဲ ထည့်ပါ |
| `flutter doctor` မှာ `Visual Studio` `[✗]` | VS installer ပြန်ဖွင့် → "Desktop development with C++" workload ထည့်ပါ: `winget upgrade --id Microsoft.VisualStudio.2022.Community --override "--add Microsoft.VisualStudio.Workload.NativeDesktop --passive --norestart"` |
| cargo က `Could not find protoc` / `Protobufs in src are valid: ... NotFound` | Windows: `winget install --id Google.Protobuf -e` → terminal ပိတ်ပြီးပြန်ဖွင့်။ macOS: `brew install protobuf`။ Linux: `sudo apt install protobuf-compiler` |
| app ဖွင့်ရင် startup fail / `Unable to load dynamic library` / `kline_signal.dll` ရှာမတွေ့ | Section 3 `cargo build --release` မလုပ်ရသေးလို့ — `kline_app/native/kline_signal` ထဲမှာ build ပါ။ **`flutter run` ကို `kline_app` folder ထဲကနေ** run ပါ |
| Android build မှာ `failed to find tool "clang.exe"` / `linker not found` | Section 6 (2) က env ၄ ခု (`PATH`, `CARGO_TARGET_AARCH64_LINUX_ANDROID_LINKER`) မသတ်မှတ်ထားလို့ — command အတိုင်း set ပြီးမှ build |
| phone မှာ app ဖွင့်ရင် crash / `dlopen failed: library not found` | `.so` ကို `android/app/src/main/jniLibs/arm64-v8a/` ထဲ copy မထားလို့ — Section 6 (2) ပြန်လုပ်ပါ |
| `host key verification failed` (SSH clone) | ပထမဆုံး connection မှာ `yes` ထည့်ပါ။ မရရင် key public part ကို repo owner ဆီ တင်ပြီးပြီလား စစ်ပါ |
| `Permission denied (publickey)` | SSH key ကို server ထဲ မတင်ရသေးသေး — Section 2 အတိုင်း key ပို့ပါ |
| Gradle `OutOfMemoryError` / build အရမ်းကြာ | RAM 16 GB ရှိရမယ်။ `android/gradle.properties` ထဲ `-Xmx8G` ရှိပြီးသား — RAM နည်းရင် အခြား app တွေ ပိတ်ပါ |
| Android Studio မှာ `SDK not found` / `sdk.dir` error | Android Studio က SDK install မပြီးသေးလို့ — SDK Manager ကနေ platform + NDK ထည့်ပြီး `android/local.properties` ထဲ `sdk.dir` ရှိမရှိ စစ်ပါ |
| app run ပေမယ့် network error / API မရောက် | `https://kline-api.xhtd5566.com/health/live` ကို browser မှာ ဖွင့်ကြည့်ပါ (200 ရမယ်)။ proxy/VPN ရှိရင် စစ်ပါ |
| iOS/macOS build မှာ CocoaPods error | macOS: `sudo gem install cocoapods` + `pod --version` စစ်ပါ |
| `flutter test` တွေ fail | local backend (`127.0.0.1:7080`) မထောင်ရသေးလို့ network test fail ဖြစ်နိုင် — setup ပြဿနာ မဟုတ်ဘူး၊ report မှာ ဖော်ပြပါ |

---

## 9. ပြီးရင် ဘာလုပ်မလဲ / အစီရင်ခံပုံ

Setup ပြီးရင် အောက်ပါ command တွေ run ပြီး result ကို screenshot / text နဲ့ report ပို့ပါ:

```powershell
flutter doctor -v
git -C kline_app log --oneline -5
git -C kline_app status
```

Report မှာ ပါသင့်တာ:
1. OS + version (ဥပမာ Windows 11 22H2)
2. `flutter doctor -v` output (အပြည့်)
3. success ဖြစ်တဲ့ step (ဥပမာ "K-Line window ပွင့်တယ်")
4. error ရှိရင် error text အပြည့် + ဘယ် command ကနေ ထွက်တယ်

ထပ်မံသိချင်/ပြဿနာရှိရင် root `AGENTS.md` ထဲက နည်းလမ်းအတိုင်း အစီရင်ခံပါ — ရလဒ်အရင်၊ file စာရင်း၊ check command၊ ကျန် blocker တွေ။

---

### ကိုးကားစရာ အခြား docs

- `KLINE_SETUP.md` — English version (same steps, same commands)
- `CLONE.md` — repo ၄ ခု clone/pull အသေးစိတ်
- `AGENTS.md` (root) — workspace ရဲ့ အဓိက rule အားလုံး
- `kline_app/AGENTS.md` — code style, quality gate, version pin
- `KLINE_PROJECT_HANDBOOK_MM.md` — project အကြောင်း အသေးစိတ်
- `kline_app/doc/` — design/architecture docs (EN/ZH)

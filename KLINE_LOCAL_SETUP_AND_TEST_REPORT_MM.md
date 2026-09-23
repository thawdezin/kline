# K-Line Local Setup နှင့် ဖုန်းနှစ်လုံး Test Report

နောက်ဆုံးပြင်ဆင်ချိန် — 2026-09-14 (Asia/Bangkok)

## အကျဉ်းချုပ်

ဒီ Mac account အောက်မှာပဲ `kline-admin`, `kline-backend`, `kline_app` Android test အတွက်လိုအပ်တဲ့ local stack ကို Docker မသုံးဘဲ run နိုင်အောင် ပြင်ဆင်ထားသည်။ Project သုံးခုအပြင်ဘက်က `.kline-runtime/` ထဲတွင် အသစ်ထည့်ထားသည့် server binaries, Rust toolchain, Protobuf compiler, data, logs နှင့် scripts အားလုံးကို စုထားသည်။ Mac account ဖျက်လျှင် ဒီ runtime လည်း အတူပျက်မည်။ System-wide installation အသစ် မလုပ်ထားပါ။

## တောင်းဆိုချက် ၆ ချက်၏ အခြေအနေ

1. **လိုအပ်သည့် software များ install — ပြီးစီး။** Docker မသုံးဘဲ account/project-local runtime ပြင်ဆင်ထားသည်။
2. **`kline-admin` run — အောင်မြင်။** Web UI `http://127.0.0.1:55173`, Admin API `http://127.0.0.1:57081`။ Login, users endpoint, ad/channel/broadcast create နှင့် Vite production build စမ်းပြီးပြီ။
3. **`kline-backend` run — အောင်မြင်။** API `http://127.0.0.1:57080`, migrations 0001–0011, PostgreSQL, Redis, NATS JetStream, MinIO အားလုံးချိတ်ဆက်ပြီး run နေသည်။
4. **`kline_app` နောက်ဆုံး commit ၄ ခုကို Redmi 7 + TECNO KM6 ဖြင့်စမ်း — အားလုံးအောင်မြင်။** Account/device binding, content delivery, Signal prekey/session bootstrap, bidirectional encrypted plaintext recovery, delivery/read receipt နှင့် recipient process-restart offline recovery အားလုံးအောင်မြင်သည်။
5. **လိုအပ်သော backend ပြင်ဆင်မှု — မရှိ။** Backend က offline envelope ကို ciphertext အဖြစ်မှန်ကန်စွာသိမ်းထားပြီး client decrypt/persist/ACK ပြီးသည်အထိ durable ထိန်းထားသည်။ Persistent Signal state ကို `kline_app` တစ်ခုတည်းတွင် ထည့်ပြီးဖြေရှင်းထားသည်။
6. **Code push — မလုပ်ထား။** Commit/push မရှိ။ ခွင့်ပြုချက်ရပြီးနောက် တွေ့သည့် app blockers နှင့် regression tests ကို `kline_app` ထဲတွင်သာ ပြင်ထားသည်။ `kline-admin` နှင့် `kline-backend` source မပြင်ထား။

## Rust ဘာကြောင့်လိုသနည်း

Rust သည် `kline-backend` သို့မဟုတ် `kline-admin` ကို run ရန် **မလိုပါ**။ ထိုနှစ်ခုသည် Go/Node.js application များဖြစ်သည်။ Rust ကို Redmi 7 ရဲ့ Android arm64 architecture အတွက် `kline_signal` native encryption library (`libkline_signal.so`) build လုပ်ရန်သာ ထည့်ထားသည်။ Flutter app က Signal protocol encryption ကို Dart တစ်ခုတည်းနဲ့ မလုပ်ဘဲ FFI မှတစ်ဆင့် ဒီ native library ကိုခေါ်သုံးသည်။

တည်ဆောက်ပြီးသား Android library ကို `.kline-runtime/artifacts/libkline_signal.so` တွင်သိမ်းထားသည်။ APK ထဲသို့ build အချိန်တွင် ယာယီ copy လုပ်ပြီး build ပြီးသည်နှင့် repo ထဲက binary copy ကို ဖယ်ထားသည်။

## Install/အသုံးပြုထားသည့် software နှင့် packages

### ဒီအလုပ်အတွက် အသစ်ထည့်ထားပြီး account-local ဖြစ်သည့်အရာများ

| Software | Version | နေရာ | အသုံးပြုပုံ |
|---|---:|---|---|
| NATS Server | 2.14.6 | `.kline-runtime/bin/` | Async commands/results, JetStream |
| MinIO Server | 2026 source snapshot, `7aac2a2c5b7c` | `.kline-runtime/bin/` | Encrypted attachment object storage |
| MinIO Client (`mc`) | 2025 source snapshot, `77f82e18b540` | `.kline-runtime/bin/` | Bucket create/check |
| Rust stable minimal | 1.98.1 | `.kline-runtime/rustup/`, `.kline-runtime/cargo/` | Android Signal native library build |
| Rust target | `aarch64-linux-android` | `.kline-runtime/rustup/` | Redmi 7 arm64 target |
| Protobuf compiler | 36.1 | `.kline-runtime/protoc/` | Rust/libsignal protobuf build |
| `kline-backend` binary | current workspace source | `.kline-runtime/bin/` | Backend API |
| `kline-admin-api` binary | current workspace source | `.kline-runtime/bin/` | Admin API |

MinIO/NATS/Protobuf အတွက် source/download caches ကို build ပြီးနောက် storage ချွေတာရန် ဖျက်ထားသည်။ Binary နှင့်လိုအပ်သော runtime သာကျန်သည်။

### Mac တွင် မူလရှိပြီး ပြန်သုံးထားသည့်အရာများ

| Software | Version | မှတ်ချက် |
|---|---:|---|
| Go | 1.26.6 arm64 | Backend/Admin/MinIO compile |
| Node.js | 24.4.0 | Admin frontend |
| npm | 11.4.2 | Admin dependencies/scripts |
| PostgreSQL | 14.18 | Local DB; docs က 15+ အကြံပြုသော်လည်း migration 0011 အထိ လက်တွေ့အောင်မြင် |
| Redis | 8.10.1 | Backend cache/presence |
| Flutter | 3.44.8 / Dart 3.12.2 | Android build/test |
| Android SDK/ADB/NDK | existing account-owned SDK, NDK 29.0.14206865 | Redmi build/install/debug |

Docker, Docker Desktop, Podman သို့မဟုတ် Colima မထည့်ထားပါ။ ဒီ stack အတွက် မလိုဘဲ storage ပိုစားမည့်အတွက် native local services ကိုသုံးထားသည်။

## Storage report

### ဒီအလုပ်က တိတိကျကျသီးသန့်သိမ်းထားသော runtime

`.kline-runtime/` စုစုပေါင်း — **961 MB**

| အပိုင်း | Size |
|---|---:|
| Rust toolchain | 575 MB |
| Server/app binaries | 307 MB |
| PostgreSQL/Redis/NATS/MinIO data | 52 MB |
| Cargo executables/config | 11 MB |
| Protobuf compiler | 9.5 MB |
| Android Signal artifact | 1.1 MB |
| Logs/scripts/runtime files | 100 KB အောက် |

Build မပြီးခင် `.kline-runtime` သည် **4.7 GB** အထိရှိခဲ့သည်။ Go/module/download/Rust source build caches များကို ဖယ်ပြီး **3.7 GB ခန့်** ပြန်လွတ်စေခဲ့သည်။ လက်ရှိ disk သည် 460 GiB အနက် 400 GiB သုံးပြီး 35 GiB available (93%) ဖြစ်သည်။ အလုပ်မစခင် snapshot တွင် 26 GiB available (95%) ဖြစ်ခဲ့သဖြင့် cleanup အပြီး disk availability မလျော့ဘဲ တိုးနေသည်။ APFS purgeable/cache behavior ကြောင့် ဒီ `df` ကိန်းကို install size အတိအကျအဖြစ် မယူသင့်ပါ။

Android debug APK — **227 MB** (`kline_app/build/app/outputs/flutter-apk/app-debug.apk`)။ ဒီဖိုင်သည် arm64 Signal library ပါဝင်သော project build output ဖြစ်ပြီး source မဟုတ်ပါ။

Account cache totals အဖြစ် `.gradle` 6.8 GB နှင့် `.pub-cache` 552 MB ရှိသည်။ ယင်း folders များသည် ဒီအလုပ်မတိုင်မီကလည်းရှိပြီး workspace အခြား Flutter/Gradle အလုပ်များနှင့်မျှဝေသုံးထားသောကြောင့် 7.35 GB အားလုံးကို ဒီအလုပ်က install လုပ်သည်ဟု မတွက်ရ။ ဒီ task တစ်ခုတည်းကြောင့်တိုးလာသည့် cache bytes ကို baseline မရှိသဖြင့် တိတိကျကျခွဲမရ။

## Ports နှင့် local services

| Service | Address |
|---|---|
| Admin web | `http://127.0.0.1:55173` |
| Admin API | `http://127.0.0.1:57081` |
| Backend API | `http://127.0.0.1:57080` |
| PostgreSQL | `127.0.0.1:55432` |
| Redis | `127.0.0.1:56379` |
| NATS | `127.0.0.1:54222` |
| NATS monitor | `127.0.0.1:58222` |
| MinIO API | `http://127.0.0.1:59000` |
| MinIO console | `http://127.0.0.1:59001` |

NATS persistent storage limit ကို 1 GB၊ memory limit ကို 128 MB ချထားသည်။ Development Redis သည် localhost ပေါ်မှာသာ bind လုပ်ပြီး password မထား။ Production အသုံးပြုရန်မဟုတ်။

## Run/stop/check commands

Workspace root မှ run ပါ။

```bash
./.kline-runtime/run-session.sh
```

ဒီ command ကို run ထားသည့် Terminal ကို မပိတ်ရ။ Status စစ်ရန်:

```bash
./.kline-runtime/status.sh
```

ရပ်ရန်:

```bash
./.kline-runtime/stop-all.sh
```

Local credentials နှင့် DB/MinIO config ကို `.kline-runtime/runtime.env` တွင်ထားသည်။ ယင်းသည် local development အတွက်သာဖြစ်ပြီး Git ထဲမထည့်ရ။ Admin username သည် `admin` ဖြစ်သည်။

ဖုန်း USB test မလုပ်မီ:

```bash
/Users/thawdezin/Android_SDK/SDK/platform-tools/adb -s ecaf2bb reverse tcp:57080 tcp:57080
/Users/thawdezin/Android_SDK/SDK/platform-tools/adb -s 1479137649002376 reverse tcp:57080 tcp:57080
```

## ဖုန်းနှစ်လုံးတွင် စမ်းသပ်ထားသည့်အချက်များ

- Device: Xiaomi Redmi 7, Android 10/API 29, arm64, serial `ecaf2bb`။
- Device: TECNO KM6, Android 15/API 35, arm64, serial `1479137649002376`။
- Android arm64 Signal library build အောင်မြင်။
- Debug APK build, streamed install, launch အောင်မြင်။
- Login screen နှင့် fixed registration fields render အောင်မြင်။
- Real installation ID ကို backend သို့ပို့ပြီး device binding record 1 ခုဖန်တီးထားသည်။
- Successful login audit 1 ခုရှိသည်။
- Signal prekey bundle နှင့် one-time-prekey record တင်နိုင်သည်။ ဒါကြောင့် FFI library load/session bootstrap အလုပ်လုပ်ကြောင်း server-side evidence ရှိသည်။
- Admin မှဖန်တီးသည့် `Redmi 7 Test Ad` နှင့် `K-Line Local News` ကို Redmi Messages screen တွင် မြင်ရသည်။ Scheduled broadcast ကို backend worker က publish လုပ်ပြီး client endpoint မှပြန်ပေးသည်။
- Test account နှစ်ခုကို သီးခြား installation ID/device ID ဖြင့် bind လုပ်ပြီး friendship accept အောင်မြင်သည်။
- Redmi မှ `AfterFixOne` ပို့ရာ TECNO တွင် plaintext မှန်ကန်စွာရောက်ပြီး sender ဘက် `Sent` ပြသည်။
- TECNO မှ `ReplyFromTecno` ပြန်ပို့ရာ Redmi တွင် plaintext မှန်ကန်စွာရောက်ပြီး အရင် message status `Read` သို့ပြောင်းသည်။
- Message request authorization bug ပြင်ပြီးနောက် ciphertext submit, realtime delivery, decrypt, local save, ACK နှင့် read receipt တစ်ဆက်တည်းအောင်မြင်သည်။

### Commit ၄ ခုအလိုက် verdict

| Commit | Feature | Verdict |
|---|---|---|
| `5591be5` | encrypted messaging prototype | **Pass (online).** ဖုန်းနှစ်လုံးကြား Signal-encrypted bidirectional roundtrip နှင့် plaintext recovery အောင်မြင် |
| `4786115` | reliable encrypted messaging | **Pass.** Online ACK/read၊ backend durable queue နှင့် recipient force-stop/restart နောက် queued whisper decrypt/persist/ACK အောင်မြင် |
| `fd87dce` | client content delivery | Admin → DB → backend worker/API → Redmi UI end-to-end အောင်မြင် |
| `fd038b3` | account/device installation binding | **Pass.** Redmi နှင့် TECNO နှစ်လုံးစလုံး၏ distinct installation metadata, binding, login audit အောင်မြင် |

## တွေ့ပြီးပြင်ထားသော `kline_app` bugs

Registration form မှာ username TextField ကို `email` controller နှင့်မှားချိတ်ထားပြီး `new password`/`confirm new password` fields မလိုအပ်ဘဲ ထပ်နေခဲ့သည်။ ဒီအခြေအနေမှာ email validation ဖြတ်သွားလျှင်တောင် register API ဆီ valid username မရောက်နိုင်။

ပြင်ထားသည်မှာ:

- Username field → `controller.username`
- Email field → `controller.email` နှင့် email keyboard
- ထပ်နေသည့် password field နှစ်ခုဖယ်
- Username, Email, Password, Confirm password တစ်ခုစီသာရှိကြောင်း widget regression test ထည့်

Backend source ပြင်ရန်မလိုခဲ့။

Encrypted message ပို့စဉ် `HttpException: HTTP headers are not mutable` ဖြစ်သော bug ကိုလည်း ပြင်ထားသည်။ Request body ရေးပြီးမှ Bearer authorization header ထည့်နေသော order မှားနေခြင်းဖြစ်သည်။ Authorization ကို body မရေးမီထည့်ပြီး၊ test တွင် `Authorization: Bearer test-token` ပါကြောင်း regression assertion ထည့်ထားသည်။

App startup တွင် realtime connection event ကို listener တပ်မပြီးမီ လွတ်သွားနိုင်သဖြင့် initial inbox sync ကို တိုက်ရိုက် `await sync()` ခေါ်အောင် ထည့်ထားသည်။ ဒါက decrypt လုပ်နိုင်သော pending envelope များကို 60-second poll မစောင့်ဘဲ startup မှာဆွဲယူစေသည်။

Signal identity key၊ registration ID၊ known remote identities၊ EC/PQ prekeys၊ Kyber reused-base-key protection နှင့် Double Ratchet sessions အားလုံးကို versioned native snapshot အဖြစ် serialize/restore လုပ်ထားသည်။ Flutter က snapshot ကို account + device ID ခွဲပြီး `flutter_secure_storage` ထဲ encrypt/protect လုပ်ကာ Signal state mutation တိုင်း network submit သို့မဟုတ် ACK မလုပ်မီ persist လုပ်သည်။

လက်တွေ့ restart test တွင် TECNO ကို force-stop လုပ်ထားစဉ် Redmi မှ `RestartRecoveredMessage` ပို့ခဲ့သည်။ Backend တွင် message `sequence=8`, `ciphertext_type=2` (established whisper), delivery cursor `6`, ACK မရှိသေးကြောင်း အရင်အတည်ပြုခဲ့သည်။ TECNO process ပြန်စပြီးနောက် initial sync က stored ratchet state restore လုပ်ကာ plaintext ကိုမှန်ကန်စွာပြပြီး `acknowledged_at=2026-09-14 16:53:44.768243+07` ဖြစ်လာသည်။

## Verification results

- `flutter analyze lib test` — pass, no issues.
- `flutter test` — 36 passed, 1 skipped. Skipped test သည် host platform native Signal integration test ဖြစ်သည်; Android device Signal evidence ကို သီးခြားစစ်ထားသည်။
- Root-level `flutter analyze` — generated `build/ios`/`build/macos` Firebase package examples ကို analyzer ကပါကောက်သဖြင့် 172 issues; app ရဲ့ `lib`/`test` source issues မဟုတ်။
- `kline-backend: go test ./...` — pass.
- `kline-admin/server: go test ./...` — compile/pass; test files မရှိ။
- `kline-admin: npm run build` — pass.
- Health endpoints, Admin login/users, MinIO bucket, content endpoints — pass.

## ကျန်ရှိသည့် warning/limitation

- ယခင် implementation မှပို့ခဲ့သော stale test message (`sequence=5`) သည် old in-memory identity ဖြင့် encrypt လုပ်ထားသောကြောင့် implementation အသစ်က recover မလုပ်နိုင်ပါ။ Upgrade မတိုင်မီ persistence မရှိခဲ့သော key ကို ပြန်ဖန်တီး၍မရခြင်းဖြစ်ပြီး implementation အသစ်ဖြင့်ဖန်တီးထားသော sessions/messages များတွင် restart recovery အောင်မြင်သည်။
- Persistent snapshot format ကို `KLS1` version tag ဖြင့်စထားသည်။ နောင် format ပြောင်းလျှင် migration သို့မဟုတ် deliberate key/session reset policy ထည့်ရန်လိုသည်။ Production အတွက် prekey replenishment/rotation၊ device revocation နှင့် safety-number UX တို့ကို ဆက်ဖြည့်သင့်သည်။
- Android build က Firebase/Workmanager plugins များ၏ Kotlin Gradle Plugin usage သည် နောင် Flutter version တွင် unsupported ဖြစ်နိုင်ကြောင်း warning ပေးသည်။ လက်ရှိ build ကိုမတား။
- Redmi 7 ပေါ် first debug startup သည် စက်အဟောင်း/Flutter debug extraction/secure storage ကြောင့် 15–20 seconds ဝန်းကျင်ကြာခဲ့သည်; crash မဖြစ်။
- Production အတွက် PostgreSQL 15+, Redis authentication, TLS, real SMTP, Firebase `google-services.json`, strong rotated credentials နှင့် restricted network binding ထပ်လိုသည်။

## အားလုံးဖယ်ရှားလိုလျှင်

အရင် services ရပ်ပြီး `.kline-runtime/` ကိုဖယ်ပါ။ ဒီ directory တစ်ခုဖယ်ခြင်းဖြင့် ဒီ task အတွက်သီးသန့်ထည့်ထားသည့် NATS, MinIO, Rust, Protobuf, compiled server binaries နှင့် local data/logs အားလုံးကိုဖယ်နိုင်သည်။ Shared `.gradle`, `.pub-cache`, external Flutter/Android SDK, Homebrew Go/PostgreSQL/Redis တို့ကို မဖျက်ပါနှင့်—အခြား project များလည်း သုံးနိုင်သည်။

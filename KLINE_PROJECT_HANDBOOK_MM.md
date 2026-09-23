# K-Line Project Master Handbook

> ရည်ရွယ်ချက် — ဒီဖိုင်တစ်ဖိုင်ကို အစမှအဆုံးဖတ်ပြီး `kline_app`, `kline-backend`, `kline-admin` သုံးခုလုံး ဘာအတွက်ရှိသည်၊ အချင်းချင်းဘယ်လိုချိတ်ထားသည်၊ လက်ရှိ code က ဘာလုပ်နိုင်သည်၊ ဘာမပြီးသေးသည်၊ ဆက်လက်ရေးသားရန် ဘာတွေသိထားရမည်ကို နားလည်စေရန် ဖြစ်သည်။
>
> Code နှင့် document စစ်ဆေးသည့်ရက် — 2026-09-14
>
> အရေးကြီးသော source-of-truth စည်းမျဉ်း — အဟောင်း requirement document နှင့် လက်ရှိ code မကိုက်လျှင် လက်ရှိ code ကို implementation truth အဖြစ်ယူပါ။ Requirement ကို မူလရည်ရွယ်ချက်နှင့် မပြီးသေးသည့် product scope အဖြစ်သုံးပါ။

---

## 1. တစ်မိနစ်အတွင်း Project တစ်ခုလုံးကို နားလည်ရန်

K-Line သည် Flutter client၊ Go chat backend နှင့် သီးခြား admin console ပါဝင်သော end-to-end encrypted messaging system prototype ဖြစ်သည်။

```text
┌──────────────────────────────┐
│ kline_app                    │
│ Flutter UI                   │
│ Local SQLite + Secure Store  │
│ Signal/Rust FFI              │
│ AES-GCM attachment crypto    │
└──────────────┬───────────────┘
               │ HTTP/Protobuf + SSE
               │ Bearer token
               ▼
┌──────────────────────────────┐
│ kline-backend :7080          │
│ Auth / Friends / Groups      │
│ Ciphertext delivery / ACK    │
│ Pre-keys / Attachments       │
│ Ads / Broadcast public API   │
└───────┬───────┬──────┬───────┘
        │       │      │
        ▼       ▼      ▼
 PostgreSQL   Redis   NATS JetStream
        │
        └──────────────► MinIO (encrypted files only)

┌──────────────────────────────┐
│ kline-admin                  │
│ Vite web UI                  │
│ Separate Go Admin API :7081  │
└──────────────┬───────────────┘
               │ same PostgreSQL database
               ▼
       Users / bans / ads /
       broadcasts / audit logs
```

အဓိက design rule သုံးခုရှိသည်။

1. Chat plaintext နှင့် attachment plaintext ကို backend မမြင်ရပါ။ Client က encrypt လုပ်ပြီး backend က ciphertext ကိုသာ သိမ်း၊ စီ၊ ပို့ရသည်။
2. SSE၊ APNs နှင့် FCM သည် wake-up/realtime hint များသာဖြစ်သည်။ Reliable delivery ရဲ့အခြေခံက PostgreSQL device inbox၊ monotonic delivery cursor၊ HTTP sync နှင့် durable-save ပြီးမှပို့သည့် ACK ဖြစ်သည်။
3. Admin API ကို public chat API ထဲမရောပါ။ Admin service သည် default အားဖြင့် localhost `127.0.0.1:7081` တွင် သီးခြားနားထောင်သည်။

---

## 2. Repository သုံးခု၏တာဝန်

### 2.1 `kline_app/`

အသုံးပြုသူကို တိုက်ရိုက်မြင်စေသော Flutter application ဖြစ်သည်။ UI, login, friends, direct/group chat, local storage, client-side encryption, encrypted attachments, notifications နှင့် content display ကိုတာဝန်ယူသည်။

အဓိက technology များမှာ Flutter/Dart, GetX, Protobuf, Rust FFI, `flutter_secure_storage`, SQLite, Firebase Messaging, WorkManager, foreground service, MediaKit နှင့် `cryptography` package ဖြစ်သည်။

### 2.2 `kline-backend/`

Go/Gin modular-monolith chat server ဖြစ်သည်။ Authentication, email verification, friends, groups, Signal public pre-key bundles, ciphertext submission, per-device inbox, sync, ACK/read receipts, presence, push wake-up, encrypted attachment authorization နှင့် public ads/broadcast APIs ကိုတာဝန်ယူသည်။

PostgreSQL ကို durable business/message state အတွက်၊ Redis ကို presence အတွက်၊ NATS JetStream ကို asynchronous commands/results အတွက်၊ MinIO ကို encrypted attachment object အတွက်သုံးသည်။

### 2.3 `kline-admin/`

Chat server နှင့်ခွဲထားသော administration system ဖြစ်သည်။

- Vite + vanilla JavaScript frontend
- Go/Gin admin API
- PostgreSQL shared database
- Admin authentication/session
- User search, ban/unban, force logout
- Ads and broadcast management
- Audit logs and runtime-log viewer

Admin မှာ React/Vue မသုံးထားပါ။ DOM template strings နှင့် browser `fetch` ကို တိုက်ရိုက်သုံးထားသော သေးငယ်သည့် SPA ဖြစ်သည်။

---

## 3. Document များကို ဘယ်လိုဖတ်ရမလဲ

### 3.1 `kline_app/doc/`

| Document | အဓိပ္ပာယ် |
|---|---|
| `E2EE_Chat_Requirements_zh.md` | 2026-09-09 မူလ requirement baseline; proposal နှင့် မဆုံးဖြတ်ရသေးတာများပါဝင်သည် |
| `E2EE_Chat_MultiAgent_Plan_zh.md` | Agent ခွဲပြီး milestone အလိုက် တည်ဆောက်ရန် စီမံချက်; runtime design မဟုတ် |
| `libsignal_flutter_bridge_zh.md` | Dart → C ABI → Rust → libsignal boundary နှင့် prototype test |
| `KLINE_SYSTEM_DESIGN_en.md`, `_zh.md` | 2026-09-10 architecture/handover; ဘာသာစကားနှစ်မျိုး |
| `2026-09-11_WORK_SUMMARY_zh.md` | ထိုနေ့အထိ လုပ်ခဲ့သည်ဟု မှတ်တမ်းတင်ထားသော historical summary |
| `2026-09-11_DEVELOPER_IMPLEMENTATION_GUIDE_zh.md` | reliable delivery, deployment, push နှင့် release rules |
| `2026-09-11_DEVELOPER_NOTES_en.md` | အပေါ်ကအကြောင်းအရာများ၏ English handover summary |
| `KLINE_EXPRESSION_PACK_FORMAT_en.md`, `_zh.md` | emoji/sticker pack manifest v1 specification |

### 3.2 `kline-backend/doc/`

`INSTALL.en.md` နှင့် `INSTALL.zh-CN.md` သည် အကြောင်းအရာတူသော production-oriented backend installation guides ဖြစ်သည်။ Linux, Go 1.25, PostgreSQL 15+, Redis 7+, NATS 2.10+ with JetStream, migrations, build, systemd နှင့် reverse proxy requirements ကိုရှင်းထားသည်။

### 3.3 Document drift ကို သတိထားရန်

အောက်ပါအချက်များသည် အချိန်ကာလမတူသည့် design များဖြစ်၍ တစ်ပြိုင်နက်မှန်သည်ဟု မယူရ။

- မူလ requirement မှာ downlink ကို WSS ဟုဆိုသော်လည်း လက်ရှိ code က SSE သုံးသည်။
- မူလ requirement မှာ MQ မရွေးရသေးသော်လည်း လက်ရှိ backend က NATS JetStream သုံးသည်။
- မူလ group proposal က Sender Keys ဖြစ်သော်လည်း လက်ရှိ Flutter session က member device တစ်ခုစီအတွက် pairwise Signal ciphertext ထုတ်သည်။
- အဟောင်း libsignal note က persistent session မပြီးသေးဟု သတိပေးထားသည်။ လက်ရှိ code တွင် stateful native client ရှိသော်လည်း production multi-device trust lifecycle အပြည့်အစုံကို မဆိုလိုသေးပါ။
- System design ထဲတွင် local history ရှိသည်ဟုလည်း၊ memory-only ဟုလည်း ရေးထားသော stale paragraph ရှိသည်။ လက်ရှိ code တွင် encrypted SQLite `ChatHistoryStore` အမှန်တကယ်ရှိသည်။
- Historical test result ကို current checkout အတွက် proof အဖြစ်မယူရ။ Test ကို ပြန် run ရမည်။

---

## 4. System အသက်ဝင်ပုံ — Startup မှ Chat ထိ

### 4.1 Flutter startup

Entry point သည် `kline_app/lib/main.dart` ဖြစ်သည်။

1. Flutter binding စတင်သည်။
2. Android foreground-task communication port စတင်သည်။
3. MediaKit စတင်သည်။
4. `LocalizationController` ကို permanent GetX service အဖြစ် register လုပ်သည်။
5. `AuthSessionService` ကို permanent service အဖြစ် register လုပ်သည်။
6. Secure storage မှ token ကို load လုပ်ပြီး `/api/v1/auth/me` ဖြင့်စစ်သည်။
7. Valid session ဖြစ်လျှင် `PrototypeSession` ကိုစတင်ပြီး `/` dashboard သို့သွားသည်။
8. Invalid/expired token ဖြစ်လျှင် local credential ဖယ်ပြီး `/auth` သို့သွားသည်။
9. `GetMaterialApp` မှ routes, translations နှင့် iOS blue `#007AFF` အခြေခံ theme ကို တပ်သည်။

Default API endpoint သည် compile-time Dart define ဖြစ်သည်။

```text
KLINE_API_BASE_URL=http://127.0.0.1:7080
```

Remote device/backend သုံးမည်ဆိုလျှင် build/run အချိန်မှာ `--dart-define` ပေးရသည်။

### 4.2 Backend startup

Entry point သည် `kline-backend/cmd/api/main.go`; orchestration သည် `internal/app/app.go` ဖြစ်သည်။

1. `.env` နှင့် process environment ကို load လုပ်သည်။ Process env က precedence ရသည်။
2. JSON rotating logging ကို configure လုပ်သည်။
3. Default အားဖြင့် memory message/pre-key/friend stores ပြင်ထားသည်။
4. `DATABASE_URL` ရှိလျှင် PostgreSQL ချိတ်ပြီး database stores ဖြင့်အစားထိုးသည်။
5. Redis ကို မဖြစ်မနေချိတ်သည်။ Redis မရလျှင် startup fail သည်။
6. NATS JetStream ကို မဖြစ်မနေချိတ်သည်။ NATS မရလျှင် startup fail သည်။
7. Async command worker နှင့် result bridge စတင်သည်။
8. PostgreSQL ရှိလျှင် content scheduler ကို 5-second ticker ဖြင့်စတင်သည်။
9. PostgreSQL + MinIO endpoint + access key + secret key အားလုံးရှိမှ attachment routes register လုပ်သည်။
10. Gin HTTP server ကို default `:7080` တွင်စတင်သည်။

`APP_ENV=production` ဖြစ်လျှင် `DATABASE_URL` မရှိတာကို config က လက်မခံပါ။ Development mode တွင် database မရှိရင် memory fallback ဖြစ်နိုင်သော်လည်း Redis နှင့် NATS က လိုနေဆဲဖြစ်သည်။

### 4.3 Admin startup

Admin frontend နှင့် admin API ကို သီးခြားစတင်ရသည်။

Frontend default API:

```text
http://127.0.0.1:7081/api/admin/v1
```

Admin Go server startup မှာ—

1. `.env` load လုပ်သည်။
2. `logs/admin.jsonl` နှင့် stdout သို့ JSON log ရေးသည်။
3. `DATABASE_URL`, `ADMIN_USERNAME`, `ADMIN_PASSWORD` ကို မဖြစ်မနေတောင်းသည်။
4. Admin schema စစ်/ဖန်တီးသည်။
5. Environment ထဲက admin password ကို bcrypt hash ပြန်ထုတ်ပြီး matching admin row ကို upsert လုပ်သည်။
6. Default `127.0.0.1:7081` တွင်နားထောင်သည်။
7. Default CORS origin သည် `http://127.0.0.1:5173` ဖြစ်သည်။

Admin password environment ကို server restart တိုင်း admin account hash အဖြစ် upsert လုပ်သဖြင့် deployment secret ပြောင်းလျှင် admin password လည်း ပြောင်းသွားသည်ကို သိထားရမည်။

---

## 5. `kline_app` ကို အသေးစိတ်လေ့လာခြင်း

### 5.1 Architecture rule

Project convention သည် GetX ဖြစ်သည်။

- Feature modules: `lib/app/modules/<feature>/`
- Module တစ်ခုအောက်မှာ `bindings/`, `controllers/`, `views/`
- Shared state/services/widgets ကို `lib/app/controllers`, `lib/app/services`, `lib/app/widgets` တွင်ထားသည်။
- View ကို `StatelessWidget` သို့ `GetView<T>` အဖြစ်ရေးသည်။
- Mutable UI state ကို controller Rx values ထဲထားပြီး `Obx` ဖြင့် render လုပ်သည်။
- Navigation ကို named GetX routes ဖြင့်လုပ်သည်။
- Generated Protobuf files ကို manual မပြင်ရ။

လက်ရှိ code တွင် module-style files နှင့် `screens/` ထဲ shared/large screens နှစ်မျိုးရောရှိသည်။ Feature အသစ်ရေးလျှင် nested `AGENTS.md` အတိုင်း Get CLI-style module ကိုရွေးသင့်သည်။

### 5.2 Routes

အဓိက named routes များမှာ—

```text
/                         dashboard
/auth                     login/register/reset/verification
/chat                     direct or group chat
/user-profile             user profile
/news                     news list
/news/detail              news detail
/search                   people search
/story                    story prototype
/notifications            notifications
/messages/new             new message
/messages/select-member   group member selection
/profile                  profile
/calls                    call-history screen
/qr-code                  QR screen
/profile/edit             edit profile
/profile/country          country picker
/settings/media           media library
/settings/block-list      block list
/settings/preferences     preferences
/settings/privacy         privacy copy
/settings/change-password password change
```

Route ရှိတာနှင့် feature production-ready ဖြစ်တာ မတူပါ။ Calls, stories, contacts, privacy copy နှင့် အချို့ settings/actions က UI prototype သာဖြစ်သည်။

### 5.3 Dashboard နှင့် navigation

`MainDashboardScreen` က messages, friends, explore နှင့် settings ဆိုင်ရာ screens/controllers ကိုစုစည်းသည်။ Dashboard state ကို `DashboardController` က Rx value ဖြင့်ထိန်းသည်။ Calls entry ကို design document အရ top-level မှ hide ထားသော်လည်း route/screen source က ရှိနေဆဲဖြစ်သည်။

### 5.4 Authentication

Authentication UI က state machine ဆန်သည်။ `AuthStep` တွင်—

- login
- phone
- register
- forgot
- verification

ရှိသည်။ Client က login/register payload တွင် installation/device context ကိုပေးသည်။ `DeviceIdentityService` က installation identity နဲ့ platform/manufacturer/model/OS/app version/build/locale/timezone ဆိုင်ရာ context ကိုစုသည်။

Token ကို `flutter_secure_storage` တွင်သိမ်းသည်။ Restore လုပ်ချိန်မှာ backend `/auth/me` ကိုခေါ်သည်။ Logout လုပ်လျှင် backend session revoke လုပ်ပြီး local token ဖယ်ကာ `PrototypeSession` lifecycle ကိုပိတ်သည်။

Verification flow မှာ—

1. `/auth/verification/request` ဖြင့် email+purpose ပို့သည်။
2. Code verify ပြီး verification token ရသည်။
3. Registration သို့ password reset မှာ ထို one-time grant token ကိုသုံးသည်။

### 5.5 `PrototypeSession` — client runtime hub

နာမည်တွင် Prototype ပါသော်လည်း လက်ရှိ app messaging runtime ၏ အချက်အချာဖြစ်သည်။ Start လုပ်ချိန်မှာ—

- `SocialApiClient`
- `KlineMessageApiClient`
- `SignalKeyServerClient`
- `StatefulSignalClient`
- `EncryptedAttachmentService`
- `FriendCache`
- `ChatHistoryStore`

တို့ကိုဖန်တီးသည်။

ပြီးလျှင်—

1. Friend cache နှင့် chat-history DB ဖွင့်သည်။
2. Crash/offline မှကျန်သော encrypted outbox requests ကို အစဉ်လိုက်ပြန်ပို့သည်။ ပထမ failure တွင် replay ရပ်သည်။
3. SSE ချိတ်သည်။
4. SSE reconnect အောင်မြင်တိုင်း sync လုပ်သည်။
5. App foreground ပြန်ရောက်တိုင်း sync လုပ်သည်။
6. Local notifications စတင်သည်။
7. Current user/device ကို social endpoint တွင် register/update လုပ်သည်။
8. Auth token ရှိလျှင် push/background wake-up setup လုပ်သည်။
9. Public Signal pre-key bundle ကို backend သို့တင်သည်။
10. Friends, requests, groups refresh လုပ်သည်။
11. Presence touch လုပ်သည်။
12. 60 seconds တစ်ကြိမ် fallback sync, 15 seconds တစ်ကြိမ် presence heartbeat စတင်သည်။

### 5.6 Direct message send

```text
ChatController creates a stable local message ID
→ local row is shown as pending
→ Signal session for friend is prepared from pre-key bundle if needed
→ ChatContent protobuf is serialized
→ libsignal encrypts it
→ full encrypted SubmitMessageRequest is saved in local outbox
→ POST /api/v1/messages
→ server returns sequence
→ same local row becomes accepted/sent
→ outbox row is removed
```

Network ပြတ်မသွားခင် stable message ID နှင့် request bytes ကိုသိမ်းထားသောကြောင့် restart ပြီးနောက် ciphertext အသစ်ထုတ်မည့်အစား request bytes အတိအကျ replay လုပ်နိုင်သည်။ Backend idempotency နှင့်ပေါင်းပြီး duplicate send ကိုကာကွယ်သည်။

### 5.7 Group message send

လက်ရှိ client က group members ကို backend မှယူပြီး မိမိမဟုတ်သော member device တစ်ခုစီအတွက် Signal encrypt သီးခြားလုပ်ကာ `RecipientCiphertext` list တစ်ခုတည်းဖြင့် submit လုပ်သည်။

ဒါသည် pairwise fan-out ဖြစ်ပြီး မူလ requirement မှာအကြံပြုထားသော Sender Keys မဟုတ်သေးပါ။ Group ကြီးလာလျှင် encrypt count နှင့် payload size သည် member-device count အလိုက်တိုးမည်။

### 5.8 Receive, cursor နှင့် ACK

Client က `/sync?device_id=...&after_cursor=...` ဖြင့် pending envelopes ယူသည်။ SSE မှ envelope ရောက်လာလျှင် cursor ဆက်တိုက်ဖြစ်မှ direct process လုပ်ပြီး gap ရှိလျှင် HTTP sync ကိုသုံးသည်။ Sync calls ကို `_syncTail` ပုံစံဖြင့် serialize လုပ်ထားသဖြင့် SSE, timer, resume, push တပြိုင်နက်ခေါ်သော်လည်း state မပြိုင်စေပါ။

Incoming processing အစဉ်သည်—

1. Sender device/account mapping ရှာသည်။
2. Ciphertext type `PreKey` သို့ `Whisper` အလိုက် decrypt လုပ်သည်။
3. `ChatContent` parse လုပ်သည်။
4. Attachment ရှိလျှင် authorize/download/hash verify/decrypt/persist လုပ်သည်။
5. Local SQLite history တွင် save လုပ်သည်။
6. Active conversation သို့ event ဖြန့်သည် သို့မဟုတ် notification ပြသည်။
7. အောင်မြင်မှ server ACK ပို့ပြီး cursor တိုးသည်။

Attachment download မအောင်မြင်လျှင် message ကို ACK မပို့ခြင်းက retry ပြန်ရနိုင်ရန် ရည်ရွယ်သည်။

### 5.9 Local database နှင့် encryption

`ChatHistoryStore` သည် application support directory ထဲ `kline_history.db` ကိုသုံးသည်။ Current schema version သည် 4 ဖြစ်သည်။

Tables:

- `chat_messages`: account + conversation + message key, encrypted payload, sort sequence
- `message_tombstones`: ဖျက်ပြီးသား message ပြန်မပေါ်စေရန်
- `message_outbox`: complete encrypted Protobuf submission ကို crash-safe replay လုပ်ရန်

Payloads ကို per-account AES-256-GCM key ဖြင့် encrypt လုပ်ပြီး key ကို secure storage တွင်ထားသည်။ Legacy plaintext rows ရှိလျှင် open အချိန်တွင် encrypt ပြောင်းသည်။

Ordering:

- Primary logical ordering: server/delivery sequence
- Tie breaker: local created time
- Duplicate identity: account + conversation + message key

Search က encrypted rows ကို decrypt လုပ်ပြီး Dart ဘက်တွင် lowercase substring filter လုပ်သည်။ ဒါကြောင့် server-side plaintext search မရှိသော်လည်း data အလွန်များလာလျှင် full scan performance ကို ပြန်စဉ်းစားရမည်။

### 5.10 Message contents နှင့် control events

`ChatContent` တွင် text, kind, timestamps, local sequence, attachment descriptor, reply descriptor နှင့် message event ပါဝင်နိုင်သည်။

Control events:

- delete
- edit
- reaction
- protocol တွင် future event types အတွက် reserved space

Event များလည်း Signal-encrypted content ဖြစ်ပြီး backend က အဓိပ္ပာယ်မဖတ်ဘဲ normal message ကဲ့သို့ order/deliver လုပ်သည်။

Delete-for-me သည် local SQLite row ကိုသာဖျက်သည်။ Delete-for-everyone သည် encrypted delete event ပို့သည်။ E2EE deletion က recipient သိမ်းပြီးသား copy, screenshot သို့ forward ကိုပြန်မဖျက်နိုင်ပါ။

### 5.11 Encrypted attachments

Attachment flow:

1. Image/video/voice ကို လိုအပ်သလို client-side compress လုပ်သည်။ Generic file ကို lossy rewrite မလုပ်ပါ။
2. Attachment တစ်ခုစီ random AES-256-GCM key နှင့် nonce သုံးသည်။
3. Ciphertext SHA-256 နှင့် size ကိုတွက်သည်။
4. Backend ထံ attachment record နှင့် presigned upload URL တောင်းသည်။
5. Ciphertext ကို MinIO သို့တင်သည်။
6. Complete endpoint ကိုခေါ်သည်။
7. Attachment ID, key, nonce, original metadata ကို Signal-encrypted `ChatContent` ထဲသာထည့်သည်။
8. Recipient က download URL အသစ်တောင်း၊ ciphertext ယူ၊ hash စစ်၊ AES-GCM decrypt လုပ်ပြီး app-private location တွင်သိမ်းသည်။
9. Downloaded confirmation ပို့သည်။ Target devices အားလုံးပြီးမှ object deletion ဖြစ်နိုင်သည်။

Key, nonce, original filename တို့ကို MinIO metadata သို့ plain business API ထဲမထည့်ရ။

### 5.12 Background delivery

iOS:

- Native method channel `com.kline.kline/apns`
- APNs token ကို backend သို့ register
- Wake-up ရလျှင် sync

Android:

- Firebase initialize လုပ်ပြီး FCM token ရလျှင် FCM သုံးသည်။
- Firebase/GMS/config မရလျှင် foreground service စတင်ပြီး own SSE ကိုထိန်းသည်။
- WorkManager 15-minute periodic task သည် consistency fallback သာဖြစ်သည်။ Instant delivery guarantee မဟုတ်ပါ။

Push data ကို `type=message_wakeup` လောက်သာထားသည်။ Current backend code တွင် generic Chinese notification text ပါသော်လည်း message content, sender, conversation metadata မပါ။

### 5.13 Friend cache နှင့် content

Friend list ကို local SQLite cache ထဲသိမ်းပြီး ETag ကို sync state တွင်ထားသည်။ Client က `If-None-Match` ပို့ပြီး backend `304` ပြန်ရင် cache ဆက်သုံးသည်။ Changed list ဖြစ်မှ transactionally replace လုပ်သည်။

Content APIs မှ active ads, broadcast channels နှင့် published messages ကိုယူပြီး message screen တွင်ပြသည်။ Remote images တွင် error fallback ထားရသည်။ Historical doc အရ current polling interval သည် 15 seconds ဖြစ်ပြီး နောက်ပိုင်း SSE content event + slower HTTP fallback သို့ပြောင်းရန်ရှိသည်။

### 5.14 Localization

Languages:

- English `en`
- Chinese `zh`
- Myanmar `my`
- Thai `th`
- Vietnamese `vi`

First launch တွင် OS language ကိုလိုက်ပြီး unsupported ဖြစ်လျှင် English သုံးသည်။ Manual selection ကို secure storage ထဲသိမ်းပြီး နောက်ပိုင်း launch တွင် OS language ထက်ဦးစားပေးသည်။ Visible string အသစ်ကို widget ထဲ hard-code မလုပ်ဘဲ `AppTranslations` ထည့်ရမည်။ လက်ရှိ prototype screens အချို့တွင် hard-coded English/Chinese ရှိနေသေးသည်ကို production cleanup လုပ်ရမည်။

### 5.15 Emoji/sticker pack

Manifest schema သည် `kline.expression-pack/v1` ဖြစ်သည်။

- Pack type တစ်ခုလျှင် `emoji` သို့ `sticker` တစ်မျိုးသာ
- 1–200 items
- Stable reverse-domain-style pack ID အကြံပြု
- Higher version က same ID pack ကိုအစားထိုး
- Third-party sticker သည် HTTPS `.webp`, `image/webp`, maximum 2 MiB
- Imported manifest က local Flutter asset ကို reference မလုပ်နိုင်
- Sticker ကို send မလုပ်မီ local WebP file အဖြစ်ယူပြီး normal encrypted attachment flow ဖြင့်ပို့
- Source CDN URL ကို chat message မဖော်ပြ

Bundled packs:

- `com.kline.emoji.default`
- `com.kline.stickers.blue-bird`

### 5.16 Client မှာ မပြီးသေး/သတိထားရမည့်အချက်များ

- Voice/video calling backend flow မရှိသေးပါ။
- Story/news/explore/privacy/contacts နှင့် setting actions အချို့သည် demo content/UI ဖြစ်သည်။
- Contact import, call history data, video thumbnails, streaming, resumable large files မပြီးသေးပါ။
- Group admin actions—remove member, assign admin, mute, leave, dissolve—အပြည့်အစုံမရှိသေးပါ။
- Trusted multi-device linking, safety-number verification, key rotation, revoked-device crypto lifecycle, encrypted backup/restore မပြီးသေးပါ။
- Remote demo image URLs ရှိနေသည်။ Production asset ownership, caching, upload, moderation, CSP ကိုလုပ်ရမည်။
- Native libsignal build artifacts နှင့် target-platform packaging ကို release pipeline တွင် သေချာစီမံရမည်။

---

## 6. `kline-backend` ကို အသေးစိတ်လေ့လာခြင်း

### 6.1 Folder map

```text
cmd/api/                    process entry
internal/app/               dependency wiring and lifecycle
internal/config/            environment configuration
internal/domain/            device/message domain types
internal/modules/auth/      auth contracts/service
internal/modules/friends/   friends and groups
internal/modules/delivery/  message lifecycle
internal/modules/devices/   pre-key store interface/memory store
internal/modules/presence/  presence abstraction
internal/modules/push/      APNs/FCM wake-up
internal/modules/verification/ email-code lifecycle
internal/modules/attachments/ encrypted attachment rules
internal/platform/database/ PostgreSQL implementations
internal/platform/memory/   development message store
internal/platform/realtime/ Redis presence
internal/platform/asyncflow/ NATS commands/results/SSE hub
internal/platform/objectstore/ MinIO adapter
internal/transport/httpapi/ Gin routes/middleware/handlers
api/proto/                  authoritative Protobuf source
gen/                        generated Go Protobuf; do not hand-edit
migrations/                 ordered PostgreSQL migrations
doc/                        install guides
```

### 6.2 HTTP API surface

Health:

```text
GET  /health/live
GET  /health/ready
```

Auth and verification:

```text
POST /api/v1/auth/verification/request
POST /api/v1/auth/verification/verify
POST /api/v1/auth/password/reset
POST /api/v1/auth/register
POST /api/v1/auth/login
GET  /api/v1/auth/me
POST /api/v1/auth/logout
POST /api/v1/auth/password
```

Social/groups:

```text
GET  /api/v1/users/search
PUT  /api/v1/prototype/users/:userID
POST /api/v1/friends/requests/:userID
GET  /api/v1/friends/requests
POST /api/v1/friends/requests/:userID/accept
GET  /api/v1/friends
POST /api/v1/groups
GET  /api/v1/groups
GET  /api/v1/groups/:groupID/members
```

Signal/public keys:

```text
PUT /api/v1/users/:userID/devices/:deviceID/prekeys
GET /api/v1/users/:userID/devices/:deviceID/prekey-bundle
```

Messaging:

```text
POST /api/v1/messages                 application/x-protobuf
GET  /api/v1/sync
POST /api/v1/messages/:id/ack         application/x-protobuf
POST /api/v1/messages/:id/read
GET  /api/v1/messages/:id/status
GET  /api/v1/events                   SSE
```

Presence/push:

```text
PUT /api/v1/presence/:deviceID
GET /api/v1/presence/:deviceID
PUT /api/v1/devices/:deviceID/push-token
```

Attachments — PostgreSQL + complete MinIO configuration ရှိမှ register လုပ်သည်:

```text
POST /api/v1/attachments
POST /api/v1/attachments/:id/complete
GET  /api/v1/attachments/:id/download
POST /api/v1/attachments/:id/downloaded
```

Public content — PostgreSQL ရှိမှ register လုပ်သည်:

```text
GET /api/v1/content/ads
GET /api/v1/content/channels
GET /api/v1/content/channels/:id/messages
```

Contract placeholders:

```text
GET /api/v1/devices       → 501
GET /api/v1/contacts      → 501
GET /api/v1/conversations → 501
```

Database-backed auth store ရှိလျှင် protected routes အားလုံး Bearer middleware အောက်ဝင်သည်။ Database မရှိသည့် development wiring တွင် auth store nil ဖြစ်ပြီး prototype routes က authentication middleware မတပ်နိုင်သည်။ ထို fallback ကို production security အဖြစ် မသုံးရ။

### 6.3 Async commands + SSE

Register, login, password change, friend request/accept စသည်တို့အတွက် flow:

```text
Client first opens /events
→ POST request contains X-Client-ID
→ API publishes command to NATS JetStream
→ JetStream ACK ရပြီး HTTP 202 + request_id ပြန်
→ command worker executes database operation
→ result subject မှ result publish
→ SSE hub routes by client/user/device topic
→ client matches request_id and completes its Future
```

`KLINE_COMMANDS` stream က commands ကို 7 days ထိ၊ `KLINE_RESULTS` က results ကို 1 day ထိထားရန် design လုပ်ထားသည်။ SSE ပြတ်သွားခြင်းသည် durable business command ရဲ့ state ပျောက်သွားတာ မဟုတ်သော်လည်း result recovery UX ကို သေချာစမ်းရမည်။

### 6.4 Reliable message storage

Server အတွက် ID နှစ်မျိုးကို မရောရ။

- Conversation sequence: conversation တစ်ခုအတွင်း display ordering
- Delivery cursor: recipient device တစ်ခု၏ inbox အားလုံးအတွက် sync ordering

Direct/group conversations အများအပြားကို device တစ်ခုက sync လုပ်သောအခါ conversation sequence တစ်ခုကို global cursor အဖြစ်သုံးလျှင် messages skip ဖြစ်နိုင်သည်။ ဒါကြောင့် device cursor ကိုသီးခြားထားသည်။

Submission အချိန်မှာ—

1. Stable `message_id` စစ်သည်။
2. Same ID already exists လျှင် original recipients/content နှင့် တူမတူစစ်သည်။
3. တူလျှင် original accepted result ပြန်ပေးသည်။
4. မတူလျှင် `409 Conflict` ပြန်သည်။
5. Conversation sequence တိုးသည်။
6. Encrypted message နှင့် recipient ciphertexts သိမ်းသည်။
7. Recipient device တစ်ခုစီအတွက် delivery cursor ထုတ်ပြီး inbox row သိမ်းသည်။
8. Transactional outbox event ထည့်သည်။
9. Commit ပြီးမှ realtime/push wake-up ပို့နိုင်သည်။

Device A ACK က device B ရဲ့ pending row ကိုမရှင်းရ။ Read receipt နှင့် delivery ACK ကိုလည်း မရောရ။

### 6.5 Protobuf contract

Authoritative file သည် `api/proto/kline/v1/messaging.proto` ဖြစ်သည်။ အကြမ်းဖျဉ်းအားဖြင့်—

- outer envelope: server လိုအပ်သည့် message/conversation/sender/recipient/cursor/ciphertext fields
- inner `ChatContent`: client သာဖတ်ရမည့် text, attachment, reply, event
- `RecipientCiphertext`: device တစ်ခုချင်းစီအတွက် ciphertext
- submit/sync/ack request-response messages
- attachment/reply/control-event messages

`.proto` ပြောင်းလျှင် Dart နှင့် Go generated code နှစ်ဘက်လုံး regenerate လုပ်ရမည်။ `gen/` နှင့် `lib/generated/` ကို manual edit မလုပ်ရ။ Field number ကို remove/reuse မလုပ်ဘဲ compatibility စည်းမျဉ်းလိုက်ရမည်။

### 6.6 Authentication and device binding

Password ကို bcrypt hash ဖြင့်သိမ်းသည်။ Session token အကြမ်းကို database မသိမ်းဘဲ hash ကိုသိမ်းသည်။ Current device context တွင် installation ID, platform, manufacturer, model, OS version, app version/build, locale, timezone ပါသည်။ Login audit တွင် source IP, user agent, result/failure reason ပါဝင်သည်။

Protected request တွင် backend က token မှ current account/device ကိုသတ်မှတ်ပြီး cross-device message submit/sync/ACK မဖြစ်စေရန် စစ်ရမည်။ `X-User-ID`, `X-Device-ID` ကို client ပြောသလိုပဲ ယုံခြင်းသည် production authorization မဟုတ်ပါ။

Admin ban က current auth sessions အားလုံးဖျက်သဖြင့် force logout ဖြစ်သည်။ New request authentication မှာ ban state ကို ဆက်လက်စစ်ရန်လိုသည်။

### 6.7 Email verification

Verification code lifecycle:

- Purpose: `register` သို့ `reset_password`
- Code: random 6 digits
- Challenge expiry: 10 minutes
- Resend throttle: 1 minute
- Maximum invalid attempts: 5
- Successful verify ပြီး grant token ထုတ်
- Grant expiry: 10 minutes
- Consume once only

SMTP config ရှိလျှင် outbound SMTP ပို့သည်။ မရှိသည့် development path မှာ `LogMailer` သုံးနိုင်ပြီး code ပါသော email body ကို development log တွင်ရေးသည်။ Production logs တွင် verification code မထွက်စေရန် SMTP configuration ကို မဖြစ်မနေမှန်အောင်ထားရမည်။ Challenges နှင့် grants သည် လက်ရှိ process memory ထဲသာဖြစ်သောကြောင့် backend restart, horizontal scaling နှင့် abuse protection အတွက် production persistent/shared store လိုသည်။

### 6.8 Presence

Presence ကို Redis TTL-based store ဖြင့်သုံးသည်။ Client က 15 seconds တစ်ကြိမ် touch လုပ်သည်။ Presence သည် message reliability မဟုတ်ပါ။ Redis key expiry က online/offline approximation ပေးသည်။

### 6.9 Push

Push-token registry သည် `sync.Map` process memory ထဲရှိသည်။ Backend restart ဖြစ်လျှင် registrations ပျောက်သည်။ Production မတိုင်ခင် PostgreSQL ထဲပြောင်းရမည်။

FCM/APNs က `message_wakeup` generic signal နှင့် generic notification စာသားသာပို့သည်။ Invalid-token removal, retry queue, throttling, metrics နှင့် alerts မပြည့်သေးပါ။

### 6.10 Attachments and MinIO

Backend သိမ်းသည်မှာ—

- attachment ID
- opaque object key
- uploader
- conversation
- ciphertext size
- ciphertext SHA-256
- lifecycle status
- expiry
- target devices and downloaded timestamps

Backend မသိမ်းသင့်တာ—

- AES key
- nonce as plaintext business metadata
- original plaintext file
- original filename unless encrypted inner content

MinIO credentials/endpoint မပြည့်လျှင် route ကိုမဖွင့်ဘဲ warning log ထုတ်သည်။ Plaintext upload အဖြစ် fallback မလုပ်ထားခြင်းသည် မှန်ကန်သော security boundary ဖြစ်သည်။

### 6.11 Content scheduling

PostgreSQL content store ရှိလျှင် scheduler က 5 seconds တစ်ကြိမ် due broadcasts ရှာပြီး NATS command publish လုပ်သည်။ Command processor က publish state ကို update လုပ်ပြီး online clients ကို async content event ဖြန့်နိုင်သည်။ Public API က active/current ads နှင့် published broadcasts ကိုသာဖတ်ပေးရသည်။

### 6.12 Logging

Backend က stdout နှင့် rotating JSONL log ကိုသုံးသည်။ Logs ထဲတွင် passwords, access tokens, plaintext messages, ciphertext နှင့် Signal key material မထည့်ရန် invariant ရှိသည်။ Ciphertext ကိုလည်း diagnostic log ထဲမရေးရခြင်းက volume နှင့် sensitive metadata exposure နှစ်ခုလုံးကိုလျှော့သည်။

### 6.13 Migrations 0001–0011

| Migration | ထည့်သည့်အရာ |
|---|---|
| `0001` | Signal device pre-key bundle နှင့် one-time pre-keys |
| `0002` | conversations, encrypted messages, per-device inbox/cursor, transactional outbox |
| `0003` | prototype users, friend requests, friendships |
| `0004` | ciphertext type: PreKey/Whisper |
| `0005` | username/email/password hash, auth sessions |
| `0006` | chat groups and group members/roles |
| `0007` | recipient-device-specific ciphertexts |
| `0008` | encrypted attachment records and recipients |
| `0009` | delivered/read receipt fields/index |
| `0010` | ads, broadcast channels/messages |
| `0011` | installation-bound user devices and login audit logs |

Migrations ကို numeric order ဖြင့် database မဖွင့်မီ run ရမည်။ Startup `Ensure*Schema` checks ရှိတာကို audited migrations အစားမယူရ။

### 6.14 Backend limitations

- Development memory fallback သည် durable မဟုတ်၊ secure production deployment မဟုတ်။
- `/devices`, `/contacts`, `/conversations` module list endpoints သည် `501` placeholders ဖြစ်သည်။
- Verification challenges/grants နှင့် push tokens သည် process-local memory ဖြစ်သည်။
- Production-grade multi-device authorization/revocation UX နှင့် trust verification မပြီးသေးသည်။
- Group authorization/key-version lifecycle သည် full production model မဟုတ်သေးသည်။
- Push retry/cleanup/metrics မပြည့်သေးသည်။
- Attachment expiry cleanup worker နှင့် operational reconciliation ကို ထပ်စစ်/ဖြည့်ရန်လိုသည်။
- Professional cryptographic/security audit မရှိသေးသည်။

---

## 7. `kline-admin` ကို အသေးစိတ်လေ့လာခြင်း

### 7.1 Frontend structure

```text
index.html
src/main.js       login, layout, users, audit, runtime logs
src/content.js    ads, channels, scheduled broadcasts
src/*.css         presentation
package.json      Vite scripts only
```

State သည် JavaScript object နှင့် `sessionStorage` ထဲ token တစ်ခုသာဖြစ်သည်။ Router library မရှိဘဲ `state.tab` ပြောင်းပြီး DOM ကိုပြန် render လုပ်သည်။

Output escaping အတွက် temporary DOM node ရဲ့ `textContent` → `innerHTML` နည်းဖြင့် `esc()` သုံးထားသည်။ User/database strings ကို template HTML ထဲထည့်မီ escape လုပ်ထားခြင်းက stored XSS risk ကိုလျှော့သည်။ URL ကို `<img src>` စသည့် attribute ထဲသုံးရာတွင် scheme/domain whitelist ကို backend/admin input validation တွင် ထပ်မံတင်းကြပ်သင့်သည်။

### 7.2 Admin authentication

```text
POST /api/admin/v1/login
```

Successful login မှ random 32-byte token ထုတ်ပြီး browser `sessionStorage` တွင်ထားသည်။ Server က SHA-256 token hash နှင့် 12-hour expiry ကို `admin_sessions` တွင်သိမ်းသည်။ Browser ပိတ်သောအခါ sessionStorage ပျောက်သော်လည်း server session row က expiry မတိုင်ခင်ရှိနေသည်။ Explicit logout UI သည် local token ကိုပဲဖယ်သည်; server-side admin-session revoke endpoint မရှိသေးသည်။

### 7.3 Admin API

```text
GET  /health/live
POST /api/admin/v1/login

GET  /api/admin/v1/users
POST /api/admin/v1/users/:id/ban
POST /api/admin/v1/users/:id/unban
POST /api/admin/v1/users/:id/force-logout

GET  /api/admin/v1/audit-logs
GET  /api/admin/v1/runtime-logs

GET  /api/admin/v1/ads
POST /api/admin/v1/ads
GET  /api/admin/v1/broadcast-channels
POST /api/admin/v1/broadcast-channels
GET  /api/admin/v1/broadcasts
POST /api/admin/v1/broadcasts
```

Ban operation က user ban fields update, auth sessions delete နှင့် audit insert ကို transaction တစ်ခုအတွင်းလုပ်သည်။ No-until ban ကို year 9999 အထိ သတ်မှတ်သည်။ Force logout က user auth sessions အားလုံးဖျက်သည်။

### 7.4 Runtime logs

Admin API က configured JSONL log files ကိုဖတ်ပြီး source, level, query, limit ဖြင့် filter လုပ်သည်။ UI က 100–1000 rows, 10-second auto refresh နှင့် NDJSON export ပေးသည်။

Security သတိပြုရန်—admin process ကို trusted operator environment ထဲသာထားရမည်။ `CHAT_BACKEND_LOG_PATH` ကို arbitrary/untrusted input ကမပြောင်းနိုင်စေရ။ Runtime log viewer သည် file content ကို admin ဆီပြသော privileged feature ဖြစ်သည်။

### 7.5 Ads and broadcasts

Admin မှ—

- image/video ad နှင့် active time window ဖန်တီးနိုင်သည်
- broadcast channel ဖန်တီးနိုင်သည်
- maximum UI textarea length 4000 ပါသော scheduled broadcast ဖန်တီးနိုင်သည်
- create actions ကို audit log ထည့်သည်

လက်ရှိ API မှာ create/list အဓိကရှိပြီး edit/delete/disable workflow အပြည့်အစုံမရှိသေးသည်။ Ad URL scheme/domain/media validation က title, time range, media type စစ်တာလောက်သာရှိ၍ production whitelist လိုသည်။

### 7.6 Admin limitations

- Automated tests မရှိသေးပါ; Go packages တွင် `[no test files]` ဖြစ်သည်။
- Frontend framework/router/form library မရှိသဖြင့် app ကြီးလာလျှင် maintainability ပြန်သုံးသပ်ရမည်။
- Client-side logout က server token revoke မလုပ်ပါ။
- CSRF model ကို Bearer token + restrictive CORS က တစ်စိတ်တစ်ပိုင်းလျှော့သော်လည်း XSS ဖြစ်လျှင် sessionStorage token ခိုးနိုင်သည်။ CSP နှင့် stronger frontend hardening လိုသည်။
- Pagination မပြည့်: users limit 200, broadcasts limit 500 စသည့် fixed query limits ဖြစ်သည်။
- Role-based admin authorization မရှိသလောက်ဖြစ်ပြီး authenticated admin အားလုံးသည် privileged routes ကိုခေါ်နိုင်သည်။ `role` column ရှိသော်လည်း route permission တွင်မသုံးသေးသည်။
- Admin schema ကို runtime `EnsureSchema` SQL string ဖြင့်ပြင်သည်။ Formal versioned admin migrations လိုသည်။

---

## 8. Database ownership ကို တစ်နေရာတည်းမှာမြင်ရန်

```text
prototype_users
├─ identity/profile/auth columns
├─ ban state (admin adds/manages)
├─ friend_requests / friendships
├─ group memberships
├─ auth_sessions
└─ user_devices / login_audit_logs

conversations
└─ encrypted_messages
   ├─ recipient-specific ciphertexts
   ├─ device_inbox
   ├─ delivery/read receipts
   └─ outbox_events

encrypted_attachments
└─ attachment_recipients

content_ads
broadcast_channels
└─ broadcast_messages

admin_users
├─ admin_sessions
└─ admin_audit_log
```

Chat backend နှင့် admin backend တို့သည် database တစ်ခု၏ tables ကို မတူသောတာဝန်ဖြင့်အသုံးပြုသည်။ Schema change လုပ်ရာတွင် repo နှစ်ခုလုံး၏ SQL assumptions ကိုစစ်ရမည်။ ဥပမာ `prototype_users`, content tables, auth sessions တို့ကို admin နှင့် chat backend နှစ်ဘက်လုံးထိနိုင်သည်။

---

## 9. End-to-end user flows

### 9.1 Register

```text
Flutter asks for email verification
→ backend creates in-memory challenge and sends SMTP mail
→ user submits code
→ backend returns one-time grant token
→ Flutter submits register command + device context + grant
→ NATS queues command
→ worker writes account/device/session
→ result returns via SSE request_id
→ Flutter stores bearer token securely
→ PrototypeSession starts
```

### 9.2 Login

```text
Flutter opens SSE
→ submits username/password/device context
→ NATS command worker checks bcrypt password
→ device installation is bound/audited
→ session token created; hash stored in PostgreSQL
→ result returned through SSE
→ raw token stored only in client secure storage
```

### 9.3 Friend and direct chat

```text
Search user
→ send friend request async command
→ recipient lists and accepts request
→ backend creates deterministic direct conversation relationship
→ clients fetch one another's device pre-key bundles
→ sender encrypts ChatContent per device
→ backend stores ciphertext/inbox
→ receiver syncs/decrypts/persists/ACKs
```

Business friendship permission နှင့် cryptographic Signal session သည် state နှစ်မျိုးဖြစ်သည်။ Friend ဖြစ်သွားတာတင်နဲ့ identity key trusted ဖြစ်သွားသည်ဟု မယူရ။

### 9.4 Group chat

```text
Owner creates group + initial members
→ backend creates group conversation and roles
→ client fetches member devices
→ current sender encrypts separately for each recipient device
→ one submit contains recipient ciphertext list
→ each device gets independent inbox cursor and ACK state
```

Member change/versioned cryptographic rekey strategy အပြည့်အစုံ မပြီးသေးသည်။ Removed member ရရှိပြီးသား plaintext/key ကို E2EE ဖြင့်ပြန်သိမ်းယူမရကြောင်း product behavior တွင် ရှင်းပြရမည်။

### 9.5 Offline/restart recovery

Sender side:

- Outgoing encrypted request ကို local encrypted outbox ထဲကြိုသိမ်း
- Restart တွင် exact request replay
- Stable message ID ဖြင့် backend deduplicate

Receiver side:

- Server per-device inbox တွင် expiry မတိုင်ခင် pending ciphertext ရှိ
- Receiver restart/online ပြန်ဖြစ်လျှင် `/sync`
- Local DB save ပြီးမှ ACK
- ACK ပျောက်လျှင် redelivery ရနိုင်သော်လည်း local key/cursor ဖြင့် duplicate UI မဖြစ်စေ

### 9.6 Admin ban

```text
Admin logs in
→ searches user
→ provides ban reason
→ admin API transaction updates ban state
→ deletes all user auth sessions
→ writes audit record
→ user's next authenticated request fails/re-login is controlled by auth rules
```

---

## 10. Configuration reference

### 10.1 Flutter

```text
--dart-define=KLINE_API_BASE_URL=http://SERVER:7080
```

Android FCM အတွက် `android/app/google-services.json` လိုနိုင်သည်။ မရှိလျှင် build/runtime က enhanced-online fallback သို့သွားရန် design လုပ်ထားသည်။ Server service-account JSON ကို client repository ထဲ မထည့်ရ။

### 10.2 Chat backend

```dotenv
APP_ENV=development|production
HTTP_ADDRESS=:7080
DATABASE_URL=postgres://...
REDIS_URL=redis://127.0.0.1:6379/0
NATS_URL=nats://127.0.0.1:4222

MINIO_ENDPOINT=127.0.0.1:9000
MINIO_BUCKET=kline-encrypted-attachments
MINIO_USE_TLS=false
MINIO_ACCESS_KEY=...
MINIO_SECRET_KEY=...

SMTP_ADDRESS=host:port
SMTP_USERNAME=...
SMTP_PASSWORD=...
SMTP_FROM=no-reply@example.com

FCM_PROJECT_ID=...
GOOGLE_APPLICATION_CREDENTIALS=/mounted/secret.json

APNS_KEY_PATH=/mounted/AuthKey_xxx.p8
APNS_KEY_ID=...
APNS_TEAM_ID=...
APNS_BUNDLE_ID=com.kline.kline
APNS_PRODUCTION=true|false
```

Repository ထဲက `.env.example` သည် full configuration မဟုတ်ဘဲ MinIO credentials, SMTP နှင့် push variables မပါသေးသည်။ ဒီ handbook list ကို code config နှင့် deployment docs ပေါင်းပြီးရေးထားသည်။ Secret values များကို Git မတင်ရ။

### 10.3 Admin API

```dotenv
DATABASE_URL=postgres://...
ADMIN_USERNAME=...
ADMIN_PASSWORD=...
HTTP_ADDRESS=127.0.0.1:7081
WEB_ORIGIN=http://127.0.0.1:5173
CHAT_BACKEND_LOG_PATH=/trusted/path/backend.jsonl
```

### 10.4 Admin frontend

```dotenv
VITE_API_BASE=http://127.0.0.1:7081/api/admin/v1
```

---

## 11. Local development runbook

### 11.1 Tool requirements

- Flutter compatible with Dart SDK constraint `^3.12.2`
- Rust stable toolchain for `native/kline_signal`
- Go 1.25
- Node/npm
- PostgreSQL 15+
- Redis 7+
- NATS Server 2.10+ with JetStream
- MinIO for attachments
- `protoc` and Dart/Go plugins when schema changes

### 11.2 Recommended startup order

```text
PostgreSQL
→ run migrations 0001 ... 0011
→ Redis
→ NATS JetStream
→ MinIO
→ kline-backend :7080
→ kline-admin API :7081
→ kline-admin Vite :5173
→ one or more Flutter clients
```

### 11.3 Backend

```bash
cd kline-backend
cp .env.example .env
# complete all required values
for file in migrations/*.sql; do
  psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f "$file"
done
go test ./...
go run ./cmd/api
```

Health checks:

```bash
curl http://127.0.0.1:7080/health/live
curl http://127.0.0.1:7080/health/ready
```

### 11.4 Admin

```bash
cd kline-admin
npm install
npm run dev
```

Separate terminal:

```bash
cd kline-admin/server
go test ./...
go run ./cmd/admin-api
```

`kline-admin/.env.example` မှာ frontend variable တစ်ခုပဲရှိသဖြင့် Go server environment ကို သီးခြားပေးရမည်။

### 11.5 Flutter

```bash
cd kline_app
flutter pub get
flutter analyze
flutter test
flutter run --dart-define=KLINE_API_BASE_URL=http://127.0.0.1:7080
```

Physical phone မှ `127.0.0.1` သည် phone ကိုယ်တိုင်ဖြစ်သည်။ Host computer LAN IP သို့ emulator-specific host address ကိုသုံးရမည်။ Backend HTTP ကို LAN ဖြင့်သုံးလျှင် mobile platform cleartext/network policies ကိုစစ်ရမည်; production မှာ HTTPS သာသုံးသင့်သည်။

### 11.6 Rust/libsignal

```bash
cd kline_app/native/kline_signal
cargo test
cargo build --release
cargo +stable test --test libsignal_prototype -- --nocapture
```

Native library ကို target platform က load နိုင်သည့် location/packaging ထဲထည့်ရမည်။ Android ABI တစ်ခုချင်း၊ iOS device/simulator slices, macOS/Windows/Linux library naming ကို သီးခြားစစ်ရမည်။ Build artifacts ကို Git မတင်ရ။

---

## 12. Verification status on 2026-09-14

ဒီ handbook ရေးစဉ် current checkout မှာ run ခဲ့သည့် read-only/build checks:

- `kline-backend`: `go test ./...` passed.
- `kline-admin`: `npm run build` passed with Vite 6.4.3.
- `kline-admin/server`: `go test ./...` passed, သို့သော် packages အားလုံး `[no test files]` ဖြစ်သည်။ Compile success သာအတည်ပြုသည်။
- `kline_app`: `flutter analyze && flutter test` ကိုစတင်ရာ Flutter SDK သည် workspace ပြင်ပ SDK cache တွင် engine files update လုပ်ရန်ကြိုးစားပြီး sandbox permission ဖြင့်ပိတ်သွားသည်။ Code/test failure အဖြစ် မသတ်မှတ်နိုင်သလို pass ဟုလည်း မဆိုနိုင်ပါ။ Normal developer terminal တွင် ပြန် run ရမည်။
- Repo သုံးခုလုံးမှာ စစ်ဆေးမစတင်မီ Git working tree clean ဖြစ်သည်။

Historical 2026-09-11 document မှာ Flutter tests 35 ခုနှင့် Go tests passed ဟုဆိုထားပြီး Android APK build က MediaKit binary download network error ဖြင့်ရပ်ခဲ့သည်။ ထို historical result ကို current release proof အဖြစ်မသုံးပါနှင့်။

---

## 13. Developer အဖြစ် အစ်ကို သိထားရမည့် ဘာသာရပ်များ

### 13.1 မဖြစ်မနေသိရမည့် core

1. Dart async/streams, isolates အခြေခံနှင့် Flutter widget lifecycle
2. GetX dependency injection, bindings, Rx state, `Obx`, named navigation
3. HTTP status semantics, Bearer authentication, SSE reconnect/recovery
4. Protobuf schema compatibility နှင့် generated-code workflow
5. PostgreSQL transactions, indexes, foreign keys, migrations, `SELECT ... FOR UPDATE`
6. Delivery semantics—at-least-once, idempotency, cursor, ACK, outbox pattern
7. Go contexts, interfaces, Gin middleware, pgx transactions
8. Redis TTL semantics
9. NATS JetStream retention, consumer ACK နှင့် device ACK တို့၏ကွာခြားချက်
10. Object storage/presigned URL နဲ့ authorization boundary

### 13.2 Security/crypto ပိုင်း

1. TLS နှင့် E2EE မတူခြင်း
2. Signal identity key, signed pre-key, one-time pre-key, session state
3. PreKey message နှင့် Whisper message
4. Multi-device trust/device revocation
5. Authenticated encryption—AES-GCM key/nonce reuse မဖြစ်ရ
6. Ciphertext integrity verification
7. Key storage—secure storage ထဲထားသင့်သောအရာ
8. Metadata leakage—E2EE ဖြစ်သော်လည်း server သိနိုင်သောအရာ
9. C ABI memory ownership, opaque handles, Rust FFI safety
10. Dependency license—libsignal AGPL-3.0-only distribution review

Crypto ကို ကိုယ်တိုင်တီထွင်ခြင်း၊ Base64 ကို encryption ဟုခေါ်ခြင်း၊ fixed AES key သုံးခြင်း၊ error မှာ plaintext fallback လုပ်ခြင်း လုံးဝမလုပ်ရ။

### 13.3 Mobile/release ပိုင်း

- Android FCM vs no-GMS fallback
- Foreground service notification obligations
- WorkManager timing limitations
- iOS APNs entitlement, signing, `.p8`, production/sandbox environment
- App lifecycle resume/background/force-stop behavior
- Platform secure storage behavior
- Native library packaging
- Real-device network routing and HTTPS certificates

### 13.4 Operations

- PostgreSQL backups/restore tests
- Redis/NATS/MinIO persistence and network isolation
- Nginx/Caddy SSE proxy buffering disabled
- Long SSE read timeout
- Secret mounting—not committing `.env`, APNs key, Firebase account JSON
- JSON log rotation, metrics and alerts
- Database-first migration rollout
- Backend rolling update, then clients/admin release

---

## 14. Change workflow

### Flutter change

1. `git status --short` စစ်ပြီး user changes မထိပါနှင့်။
2. Relevant controller/service/view နှင့် tests ကိုအရင်ဖတ်ပါ။
3. Mutable UI state ကို controller ထဲထားပါ။
4. Customer-visible strings ကို translations အားလုံးထည့်ပါ။
5. `dart format <changed-files>`
6. `flutter analyze`
7. `flutter test`
8. UI behavior ဆို real widget/device flow ကိုပါစစ်ပါ။

### Backend change

1. API/security behavior နှင့် database migration impact စစ်ပါ။
2. Schema ပြောင်းလျှင် migration အသစ်ထည့်ပါ; released migration အဓိပ္ပာယ်မပြောင်းပါနှင့်။
3. Protobuf ပြောင်းလျှင် authoritative `.proto` ကိုပြင်ပြီး Dart/Go regenerate လုပ်ပါ။
4. Idempotency, per-device isolation, auth ownership နှင့် ACK ordering tests ထည့်ပါ။
5. `gofmt` နှင့် `go test ./...` run ပါ။

### Admin change

1. Shared database assumptions ကို chat backend နှင့်တိုက်စစ်ပါ။
2. Privileged operation တိုင်း authentication, authorization, validation, audit ကိုစစ်ပါ။
3. User-controlled HTML/URL ကို escape/validate ပါ။
4. `npm run build`
5. `cd server && go test ./...`
6. Automated tests မရှိသေးသဖြင့် affected admin flow ကို browser + API integration ဖြင့်စမ်းပါ။

---

## 15. Production မတိုင်ခင် ဦးစားပေး checklist

### P0 — Security/correctness

- Real two-account/two-device Signal restart test ကို supported platforms အားလုံးတွင် pass စေပါ။
- Trusted device binding, identity change warning, revoke propagation ဆောက်ပါ။
- Protected endpoint အားလုံး token-derived user/device ownership သေချာစစ်ပါ။
- Process-memory verification grants နှင့် push tokens ကို shared durable storage သို့ရွှေ့ပါ။
- Admin RBAC, server-side logout/revoke, CSP နှင့် URL whitelist ထည့်ပါ။
- Formal security and libsignal license/distribution review ပြုလုပ်ပါ။

### P1 — Reliability

- Duplicate SSE, out-of-order, cursor gap, lost ACK, process crash, DB restart, NATS restart စမ်းပါ။
- Attachment upload interruption, tamper, expired URL, partial download, cleanup reconciliation စမ်းပါ။
- Database backup/restore နှင့် migrations rollback/forward operational plan ရေးပါ။
- Push invalid-token cleanup, retry, throttling, metrics, alerts ထည့်ပါ။

### P2 — Product completeness

- Group roles/member removal/leave/dissolve နှင့် cryptographic rekey semantics အတည်ပြုပါ။
- Device/conversation/contact placeholder APIs ဖြည့်ပါ သို့မဟုတ် product scope မှရှင်းလင်းစွာဖယ်ပါ။
- Demo news/story/privacy/remote images/actions ကို production content/flows ဖြင့်အစားထိုးပါ။
- Local full-text search performance နှင့် history migration/backup strategy အတည်ပြုပါ။
- Ads/broadcast edit, disable, delete, pagination, moderation ထည့်ပါ။

### P3 — Release matrix

- Alice, Bob, group client သုံးခု
- iPhone
- Android with GMS
- Android without GMS
- foreground/background/lock screen
- network loss/recovery
- forced app termination
- server restart
- offline recipient
- duplicate and reordered delivery
- device revoke/key change
- attachment upload/download interruption
- APNs sandbox/production
- FCM and enhanced-online fallback

---

## 16. Common misunderstandings

### “Protobuf သုံးထားတော့ secure ပြီလား?”

မဟုတ်ပါ။ Protobuf က binary serialization ဖြစ်သည်။ `ChatContent` ကို Signal ဖြင့် encrypt လုပ်ပြီးမှ server ထံပို့သောကြောင့် secure ဖြစ်သည်။

### “HTTPS ရှိတော့ E2EE မလိုဘူးလား?”

လိုသည်။ HTTPS က client↔server transport ကိုကာကွယ်သည်။ Server က plaintext မြင်နိုင်သေးသည်။ E2EE က authorized endpoint devices သာ plaintext ဖတ်နိုင်အောင်လုပ်သည်။

### “SSE ရောက်ပြီဆို delivered လား?”

မဟုတ်ပါ။ Device က decrypt လုပ်၊ attachment ပြီး၊ durable local save လုပ်ပြီး ACK ပို့မှ delivered ဟုယူရသည်။

### “NATS ACK က device ACK လား?”

မဟုတ်ပါ။ NATS ACK က backend worker က command/event ကို handle လုပ်ကြောင်းသာဆိုသည်။ User device က message သိမ်းပြီးကြောင်း မဆိုလိုပါ။

### “Phone ACK ပြီးရင် laptop inbox ဖျက်လို့ရလား?”

မရပါ။ Inbox နှင့် ACK သည် device တစ်ခုချင်းစီအတွက်ဖြစ်သည်။

### “Delete for everyone ဆို plaintext တကယ်ပျောက်သွားမလား?”

Authorized clients ကို encrypted deletion event ပို့ခြင်းသာဖြစ်သည်။ Recipient ယခင်က copy, screenshot, export, forward လုပ်ထားတာကိုပြန်မယူနိုင်ပါ။

### “Push notification က message transport လား?”

မဟုတ်ပါ။ Generic wake-up ဖြစ်ပြီး နောက်ဆုံးတွင် `/sync` ကသာ durable inbox ကိုယူသည်။

### “Admin နဲ့ chat backend ကို process တစ်ခုထဲပေါင်းရင် လွယ်မလား?”

Security boundary ပျက်နိုင်သည်။ Admin API က highly privileged ဖြစ်သဖြင့် separate listener, session, CORS, audit နှင့် network restriction ထားခြင်းက ရည်ရွယ်ချက်ရှိသည်။

---

## 17. နောက်ဆုံး mental model

K-Line ကို UI screens အစုတစ်ခုအဖြစ်မမြင်ဘဲ state machines သုံးခုအဖြစ်မြင်ပါ။

1. **Identity state machine** — register/login → device binding → token → revoke/logout
2. **Cryptographic state machine** — identity/pre-keys → session → encrypt/decrypt → persist state → key change/revoke
3. **Delivery state machine** — local pending → server accepted → device inbox → local durable save → ACK → read

Attachment, group, multi-device, push နှင့် edit/delete/reaction အားလုံးသည် ဒီ state machines အပေါ်ထပ်ဆင့်ထားခြင်းဖြစ်သည်။ Bug တစ်ခုကို debug လုပ်တိုင်း—

- ဘယ် identity/device အနေနဲ့လုပ်နေတာလဲ?
- Crypto state က ဘယ် version/session မှာလဲ?
- Message က local pending, server accepted, inbox pending, ACKed, read ထဲက ဘယ်အဆင့်မှာလဲ?
- Source of truth က local DB, PostgreSQL inbox, Redis presence, NATS event, MinIO object ထဲက ဘယ်ဟာလဲ?

ဟု ခွဲမေးပါ။ ဒီခွဲခြားမှုမှန်လျှင် K-Line ရဲ့ architecture, debugging နှင့် feature development အများစုကို မှန်ကန်စွာဆက်လုပ်နိုင်မည်။

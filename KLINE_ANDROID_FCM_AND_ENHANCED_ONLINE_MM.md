# K-Line Android FCM နှင့် Enhanced Online Mode အပြည့်အစုံ

နောက်ဆုံးစစ်ဆေး/ရေးသားချိန် — 2026-09-14 (Asia/Bangkok)

## အဖြေတို

K-Line တွင် Android notification/wakeup အတွက် **FCM (Firebase Cloud Messaging)** နှင့် **Enhanced Online Mode** နှစ်မျိုးလုံးကို code ထဲတွင် ထည့်ထားသည်။ ရွေးချယ်ပုံမှာ:

1. Android app စတင်သောအခါ FCM initialize/token register လုပ်ရန်အရင်ကြိုးစားသည်။
2. FCM token အောင်မြင်စွာရပြီး backend သို့ register လုပ်နိုင်လျှင် FCM mode သုံးသည်။
3. Firebase configuration မရှိခြင်း၊ Google Mobile Services (GMS) မရှိခြင်း သို့မဟုတ် token ရယူမရခြင်းဖြစ်လျှင် Enhanced Online foreground service ကို အလိုအလျောက်စတင်သည်။
4. Message reliability ၏အခြေခံမှာ FCM သို့မဟုတ် foreground service မဟုတ်ဘဲ backend durable inbox + delivery cursor + HTTPS `/api/v1/sync` ဖြစ်သည်။ Push/SSE သည် “message ရှိနေပြီ၊ sync လုပ်ပါ” ဟု client ကိုနိုးပေးသည့် hint ဖြစ်သည်။

**အရေးကြီးသော လက်ရှိအခြေအနေ:** `kline_app/android/app/google-services.json` မရှိသောကြောင့် ဒီ Mac မှ build ထားသော local APK တွင် production FCM မ configure ရသေးပါ။ Local backend runtime တွင်လည်း production `FCM_PROJECT_ID`/Firebase service-account configuration မထည့်ထားပါ။ ထို့ကြောင့် FCM code ရှိသော်လည်း real FCM end-to-end delivery ကို မစမ်းရသေးပါ။ Enhanced Online fallback code ကိုသုံးရန်ရည်ရွယ်ထားသော်လည်း ဒီစာရေးချိန် device runtime မှ foreground service running ဖြစ်နေကြောင်း သီးခြားအတည်ပြုမရသေးပါ။

## “တရုတ်ဖုန်းတွေအတွက်” ဆိုတာ ဘာကိုဆိုလိုသလဲ

Enhanced Online Mode သည် တရုတ်နိုင်ငံထုတ်ဖုန်းတိုင်းအတွက် မဖြစ်မနေသုံးရသော mode မဟုတ်ပါ။ အဓိကက **GMS/FCM ရှိ/မရှိ** ဖြစ်သည်။

- Mainland China ROM ပါသော Huawei၊ Xiaomi၊ Redmi၊ OPPO၊ vivo စသည့် Android ဖုန်းများတွင် Google Play Services မပါနိုင်သဖြင့် FCM token မရနိုင်သည်။ ဒီအခြေအနေအတွက် Enhanced Online fallback အသုံးဝင်သည်။
- Global ROM ပါသော Redmi/OPPO/vivo စသည်တို့တွင် Google Play Services ရှိလျှင် FCM သုံးနိုင်သည်။ ဖုန်းတံဆိပ်တရုတ်ဖြစ်ခြင်းတစ်ခုတည်းကြောင့် fallback မဝင်ပါ။
- Huawei Mobile Services (HMS) Push၊ Xiaomi Push၊ OPPO Push၊ vivo Push ကဲ့သို့ vendor push SDK များကို လက်ရှိ project တွင် မထည့်ထားပါ။
- Google services မရှိသော မည်သည့် Android device/ROM မဆို Enhanced Online Mode သို့ fallback ဝင်နိုင်သည်။ ဒါကြောင့် “Chinese-phone fallback” ထက် “FCM-unavailable Android fallback” ဟုခေါ်ခြင်းပိုတိကျသည်။

## ပါဝင်သော components

| Component | တာဝန် | လက်ရှိ file |
|---|---|---|
| `firebase_core` | Firebase initialize | `kline_app/pubspec.yaml` |
| `firebase_messaging` | FCM token၊ foreground/background push callbacks | `background_wakeup_service.dart` |
| `flutter_foreground_task` | Enhanced Online Android foreground service | `background_wakeup_service.dart` |
| `workmanager` | Android periodic fallback hint | `background_wakeup_service.dart` |
| `shared_preferences` | Pending wakeup boolean flag | `background_wakeup_service.dart` |
| App SSE client | App process running စဉ် realtime `message.envelope` events | `social_api_client.dart`, `prototype_session.dart` |
| Backend push service | FCM/APNs token registry နှင့် wakeup send | `kline-backend/internal/modules/push/service.go` |
| Durable inbox | Ciphertext သိမ်း၊ cursor/order/ACK/read ထိန်း | `kline-backend` message delivery modules |

## App startup မှာ ဘယ်လိုစတင်သလဲ

Authenticated `PrototypeSession.start()` က:

1. Main SSE connection ကို `social.connectEvents()` ဖြင့်ချိတ်သည်။
2. Local notification service ကို initialize လုပ်သည်။
3. Auth token ရှိလျှင် `BackgroundWakeupService` တည်ဆောက်သည်။
4. `initialize(...)` သို့ backend URL၊ user ID၊ device ID၊ auth token နှင့် push-token registration callback ပေးသည်။
5. Initialization ပြီးလျှင် pending wakeup flag ရှိ/မရှိ `consumePendingWakeup()` ဖြင့်စစ်ပြီး `sync()` ခေါ်သည်။
6. Signal keys upload၊ social refresh နှင့် initial inbox sync ဆက်လုပ်သည်။

ဒီ flow ကို `kline_app/lib/app/services/prototype/prototype_session.dart` တွင်တွေ့နိုင်သည်။

## FCM flow အသေးစိတ်

### 1. Build-time configuration

Android Gradle config က `android/app/google-services.json` ရှိမှသာ Google Services Gradle plugin ကို apply လုပ်သည်:

```kotlin
if (file("google-services.json").exists()) {
    apply(plugin = "com.google.gms.google-services")
}
```

ဒီ conditional ကြောင့် Firebase configuration မရှိသော developer build သည် build-time မှာမပျက်ဘဲ runtime တွင် Enhanced Online သို့ fallback ဝင်နိုင်သည်။ `google-services.json` သည် environment-specific configuration ဖြစ်ပြီး credentials/service-account private key မဟုတ်သော်လည်း project policy နှင့် deployment environment အလိုက် စီမံရမည်။ Firebase Admin service-account JSON/private key ကို Git ထဲ လုံးဝမတင်ရ။

### 2. Runtime initialization

Android ဖြစ်လျှင် app က အောက်ပါအစဉ်အတိုင်း ကြိုးစားသည်:

```text
Firebase.initializeApp()
  → background handler register
  → notification permission request
  → FirebaseMessaging.getToken()
  → backend PUT push-token
  → foreground onMessage listener
  → token-refresh listener
```

Token ရလျှင် app က:

```http
PUT /api/v1/devices/{deviceId}/push-token
Authorization: Bearer {authToken}
X-Device-ID: {deviceId}
Content-Type: application/json

{"provider":"fcm","token":"..."}
```

Backend က URL device ID နှင့် authenticated request ၏ `X-Device-ID` တူကြောင်းစစ်သည်။ Provider ကို `fcm` သို့မဟုတ် `apns` သာလက်ခံသည်။

### 3. Backend မှ FCM wakeup ပို့ပုံ

Encrypted message ကို durable storage ထဲ အရင်သိမ်းပြီးနောက် target device IDs အတွက် registered token ရှိလျှင် backend push service က Firebase Admin SDK ဖြင့် high-priority message ပို့သည်:

- Data: `type=message_wakeup`
- Visible title: `K-Line`
- Generic body: `你有一条新消息` (message အသစ်တစ်ခုရှိသည်)
- Android priority: `high`
- Collapse key: `kline_sync`

Payload ထဲ plaintext message၊ sender name၊ conversation ID၊ group name၊ attachment key စသည်တို့ မပါစေရ။ Push provider သည် encrypted-message metadata ကိုမသိသင့်ဘဲ wakeup hint သာရသင့်သည်။

### 4. App foreground/background behavior

- App foreground မှာ FCM `onMessage` ရပြီး `type=message_wakeup` ဖြစ်လျှင် `PrototypeSession.sync()` ကိုချက်ချင်းခေါ်သည်။
- App background isolate handler က network sync တိုက်ရိုက်မလုပ်ဘဲ SharedPreferences ထဲ `kline.push.pending_wakeup=true` ထားသည်။ App/session ပြန်စချိန် `consumePendingWakeup()` က flag ဖယ်ပြီး sync လုပ်သည်။
- FCM token ပြောင်းလဲလျှင် `onTokenRefresh` က backend သို့ token အသစ် register ပြန်လုပ်သည်။

## Enhanced Online Mode အသေးစိတ်

### ဘယ်အချိန် fallback ဝင်သလဲ

အောက်ပါအခြေအနေတစ်ခုခုဖြစ်လျှင် `fcmAvailable=false` ဖြစ်ပြီး `_startEnhancedOnline(...)` ခေါ်သည်:

- `Firebase.initializeApp()` မအောင်မြင်
- `google-services.json`/Firebase options မရှိ
- Google Play Services/FCM မရ
- Notification permission/token request အတွင်း exception ဖြစ်
- `getToken()` က null/empty ပြန်ပေး
- Token ကို backend register လုပ်ရာ exception ဖြစ်

### Foreground service ဘာလုပ်သလဲ

Android foreground service က authenticated HTTP connection ဖြင့်:

```text
GET {backend}/api/v1/events
Authorization: Bearer {authToken}

query:
  client_id=enhanced_{deviceId}
  user_id={userId}
  device_id={deviceId}
```

ဆိုသည့် SSE stream ကို ချိတ်ထားသည်။ `data:` line ထဲ `message.envelope` တွေ့လျှင်:

1. Pending-wakeup flag ထားသည်။
2. Foreground task မှ main Flutter isolate ဆီ `message_wakeup` event ပို့သည်။
3. Main isolate အသက်ရှင်နေလျှင် `sync()` ခေါ်သည်။
4. Foreground notification ကို “收到新消息，点按打开并同步” ဟု update လုပ်သည်။
5. Main isolate မရှိလျှင် နောက် app startup တွင် pending flag ကို consume လုပ်ပြီး sync သည်။

SSE ပြတ်လျှင် reconnect လုပ်ရန်ကြိုးစားသည်။ Connection exception ဖြစ်လျှင် 30 seconds နောက်ပြန်ကြိုးစားသည်။ `onRepeatEvent` ကို 60 seconds အဖြစ်ထားပြီး stream မရှိလျှင် reconnect လုပ်သည်။

### Android က ဘာကြောင့် persistent notification ပြရသလဲ

Background မှာကြာရှည် network connection ထိန်းရန် Android က foreground service ကိုသုံးခိုင်းပြီး user မြင်နိုင်သော ongoing notification လိုသည်။ Project က:

- Channel ID: `kline_enhanced_online`
- Channel name: `K-Line 增强在线`
- Service type: `remoteMessaging`
- Service ID: `4107`
- Notification: `K-Line 增强在线 / 正在保持安全消息连接`
- `autoRunOnBoot=true`
- `autoRunOnMyPackageReplaced=true`
- Wi-Fi lock allowed
- Wake lock disabled

ဟု configure လုပ်ထားသည်။ Android manifest တွင် `POST_NOTIFICATIONS`, `FOREGROUND_SERVICE`, `FOREGROUND_SERVICE_REMOTE_MESSAGING`, `RECEIVE_BOOT_COMPLETED`, `WAKE_LOCK` permissions ထည့်ထားသည်။

### Main SSE နှင့် Enhanced SSE နှစ်ခု ဘာကြောင့်ရှိသလဲ

- App foreground/main process ရှိချိန် `SocialApiClient` SSE က realtime event အပြည့်ကို app state ဆီပို့သည်။
- FCM မရသောအခါ Enhanced foreground-service SSE က process lifecycle ကိုကျော်၍ wakeup hint ရစေရန်ရည်ရွယ်သည်။
- နှစ်ခုလုံး event တူတူမြင်နိုင်သော်လည်း delivery cursor၊ local duplicate protection နှင့် ACK semantics ကြောင့် sync ကို idempotent ဖြစ်အောင်ဒီဇိုင်းဆွဲထားသည်။

## WorkManager fallback

App က device တစ်ခုစီအတွက် `kline-sync-{deviceId}` periodic task ကို register လုပ်ပြီး minimum frequency 15 minutes နှင့် network-connected constraint ထားသည်။

**လက်ရှိ code ၏အရေးကြီးသော gap:** WorkManager task က backend `/sync` ကို တကယ်မခေါ်သေးပါ။ `kline.push.pending_wakeup=true` flag သာထားသည်။ ဒါကြောင့် app မဖွင့်မချင်း actual message download မဖြစ်နိုင်ဘဲ “periodic consistency sync” ဟုအပြည့်အဝမသတ်မှတ်သင့်သေးပါ။ Production အတွက် background isolate ထဲ secure auth/session ကိုမှန်ကန်စွာ restore လုပ်ပြီး bounded HTTPS sync လုပ်နိုင်အောင် သို့မဟုတ် OS ခွင့်ပြုသော safe wake mechanism သို့ပြင်ရမည်။

## Reliability နှင့် security rules

```text
Sender
  → backend က ciphertext + recipient inbox row ကို durable save
  → FCM သို့မဟုတ် Enhanced SSE wakeup hint
  → recipient HTTPS /sync
  → client Signal decrypt
  → local encrypted/private history save
  → backend ACK
```

- FCM/SSE notification ရရုံဖြင့် ACK မပို့ရ။
- Decrypt နှင့် local persistence အောင်မြင်မှ ACK ပို့ရသည်။
- Wakeup ပျောက်သွားလျှင်လည်း next initial/manual/poll sync က backend durable inbox မှ ပြန်ရနိုင်သည်။
- Duplicate/reordered wakeups ဖြစ်နိုင်သည်။ Delivery cursor နှင့် message ID duplicate protection ကိုအားကိုးရသည်။
- Notification/push payload ထဲ plaintext မထည့်ရ။

## လက်ရှိ implementation limitations/risks

1. **Real FCM မ configure/test ရသေး** — local tree မှာ `google-services.json` မရှိ၊ local backend မှာ Firebase production credentials မရှိ။
2. **Push token registry က memory-only** — backend restart လျှင် registered FCM/APNs tokens ပျောက်မည်။ PostgreSQL သို့ပြောင်းရမည်။
3. **Enhanced foreground task auth token storage ကို security review လို** — `FlutterForegroundTask.saveData(key: 'auth_token', ...)` သုံးထားသည်။ ဒီ plugin storage သည် `flutter_secure_storage`/Android Keystore ကာကွယ်မှုနှင့်တူကြောင်း code မှအတည်မပြုနိုင်။ Production မတိုင်မီ token ကို Keystore-backed handoff သို့ပြောင်းရန်လိုသည်။
4. **WorkManager actual sync မလုပ်သေး** — pending flag ပဲထားသည်။
5. **Vendor push မရှိ** — Huawei HMS/Xiaomi/OPPO/vivo push services မထည့်ထားသောကြောင့် Enhanced service ကို OEM battery manager ကသတ်လျှင် instant delivery မအာမခံနိုင်။
6. **OEM battery restrictions** — Auto-start၊ background activity၊ battery optimization၊ notification permission ကို user ကခွင့်မပြုလျှင် foreground service ပြန်မတက်နိုင်။
7. **Reconnect behavior အားနည်းနိုင်** — normal SSE `onDone` မှ immediate reconnect ဖြစ်သောကြောင့် server/network failure ကြာလျှင် exponential backoff + jitter ထည့်သင့်သည်။
8. **Invalid token cleanup/metrics မရှိသေး** — FCM failure retry၊ invalid-token deletion၊ rate limiting၊ delivery telemetry/alerts ထပ်လိုသည်။
9. **Notification strings တရုတ်ဘာသာ hard-code** — localization မပြည့်စုံသေး။
10. **Device runtime verification gap** — ဒီစာရေးချိန် Redmi 7 `dumpsys activity services com.kline.kline` တွင် running foreground service မတွေ့ရပြီး TECNO က USB ဖြုတ်ထားသည်။ FCM fallback initialization path နှင့် OEM lifecycle ကို fresh install + logs + background/kill/reboot matrix ဖြင့် ထပ်စမ်းရမည်။

## Production FCM ထည့်ရန်လိုအပ်ချက်များ

### Android/client

1. Firebase project ဖန်တီးပြီး Android application ID `com.kline.kline` register လုပ်ရန်။
2. မှန်ကန်သော `google-services.json` ကို controlled build environment မှ `kline_app/android/app/` ထဲထည့်ရန်။
3. Debug/release signing certificate requirements နှင့် Firebase project settings စစ်ရန်။
4. Android 13+ notification permission UX စမ်းရန်။
5. FCM token register/refresh၊ foreground/background/terminated states အားလုံးစမ်းရန်။

### Backend

1. Firebase Admin service account ကို deployment secret manager/file mount/ADC ဖြင့်ပေးရန်။ Git ထဲမတင်ရ။
2. `FCM_PROJECT_ID` သတ်မှတ်ရန်။
3. Backend startup log မှ FCM client initialize အောင်မြင်ကြောင်းစစ်ရန်။
4. Token registry ကို PostgreSQL သို့ပြောင်းရန်။
5. Invalid/unregistered token response handling၊ retry/backoff၊ metrics ထည့်ရန်။

## Chinese/GMS-less Android test matrix

အနည်းဆုံး အောက်ပါအခြေအနေများကို ဖုန်းအစစ်ဖြင့်စမ်းသင့်သည်:

| Test | မျှော်လင့်ရလဒ် |
|---|---|
| GMS + valid Firebase config | FCM token register; Enhanced service မလို |
| GMS မရှိ | FCM fail; Enhanced foreground notification/service စတင် |
| Notification permission deny | Limitation ကို UI ဖြင့်ရှင်းပြ; reliability degradation ကိုမြင်သာစေ |
| Screen off 30+ minutes | SSE/push wakeup နောက် message sync/ACK |
| App swipe-away | OEM အလိုက် service behavior မှတ်တမ်းတင် |
| Force-stop | Android rule အရ user ပြန်ဖွင့်မချင်း background restart မမျှော်လင့်ရ; ပြန်ဖွင့်လျှင် durable inbox recover |
| Reboot | `autoRunOnBoot` နှင့် login/token/state restore အောင်မြင် |
| Wi-Fi ↔ mobile data | SSE reconnect + cursor gap recovery |
| Backend restart | SSE reconnect; memory-only push token loss ကိုဖော်ထုတ် |
| Duplicate/out-of-order wakeup | Message duplicate မပေါ်; cursor/ACK မှန် |
| OEM battery optimization | Default နှင့် unrestricted modes နှိုင်းယှဉ် |

## စစ်ဆေးရန် commands

Firebase config ရှိ/မရှိ:

```bash
find kline_app/android/app -maxdepth 1 -name google-services.json -print
```

Foreground service runtime:

```bash
adb -s DEVICE_SERIAL shell dumpsys activity services com.kline.kline
```

Notification channel/service notification:

```bash
adb -s DEVICE_SERIAL shell dumpsys notification --noredact | rg -i kline
```

App/Firebase/foreground-task logs:

```bash
adb -s DEVICE_SERIAL logcat | rg -i 'Firebase|Messaging|FlutterForegroundTask|kline'
```

Backend FCM environment ကို secret value မထုတ်ဘဲ variable ရှိ/မရှိသာ deployment environment တွင်စစ်ရမည်။ Credentials/token အပြည့်အစုံကို terminal output၊ screenshot၊ documentation သို့ Git ထဲ မထည့်ရ။

## နိဂုံး

Architecture အရ K-Line သည် GMS Android အတွက် FCM ကိုဦးစားပေးပြီး FCM မရနိုင်သော Android—အထူးသဖြင့် Mainland China ROM များ—အတွက် persistent foreground SSE ဖြစ်သော Enhanced Online Mode သို့ fallback ဝင်ရန်ရေးထားသည်။ ဒါပေမဲ့ လက်ရှိအခြေအနေကို production-ready ဟုမသတ်မှတ်နိုင်သေးပါ။ Real Firebase configuration/end-to-end test၊ Keystore-backed foreground token handoff၊ database-backed push-token registry၊ actual WorkManager sync နှင့် OEM-specific background test matrix ပြီးမှသာ အားထားရသော Chinese/GMS-less delivery solution ဖြစ်မည်။

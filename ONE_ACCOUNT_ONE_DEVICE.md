# တစ် Account တစ် Device (Single-Device Login) — Backend Fix Spec

> **Target repo:** `kline-backend` — **branch: `tzm-branch`** (app က ဒါကိုပဲ မျှော်လင့်ထားတယ်)
> **Audience:** backend developer
> **App-side အဆင့်:** `kline_app` ဘက်က `session.revoked` SSE event ကို handle လုပ်ပြီးပြီ — backend က event ထုတ်ပေးရုံပဲ။
> **Repo alignment:** local `kline-backend` checkout က `origin/master` ဖြစ်နေတယ်၊ `origin/tzm-branch` ထက် 1 commit နောက်ကျန်တယ်။ **အရင် `tzm-branch` ပေါ် အလုပ်လုပ်ပါ** (ဒါမှ `/api/v1/devices*` endpoints တွေ ရှိတယ်)။

---

## 0. TL;DR — ဘာပြင်ရမလဲ

| # | Change | နေရာ | အဆင့် |
|---|--------|-------|--------|
| 1 | `Login()` ရဲ့ session delete ကို `device_id` → `user_id` ပြောင်း + user row lock | `internal/platform/database/auth_store.go:217` | **မဖြစ်မနေ** |
| 2 | Kick ခံရတဲ့ device rows ကို `revoked_at` ရိုက် + session/prekey/inbox cleanup (ရှိပြီးသား `DeviceStore.Revoke` ကို ပြန်သုံး) | `internal/platform/database/device_store.go:124` + `auth_store.go` `Login()` | **မဖြစ်မနေ** (device list မှန်ဖို့) |
| 3 | Kick ခံရသူကို SSE `session.revoked` event ပို့ | `internal/transport/httpapi/auth.go:128` | recommended (instant logout UX) |
| 4 | DB-level အားပေးအဖြစ် unique index | migration + `EnsureAuthSchema` | optional |

**Schema change မလိုဘူး** — fix 1 က SQL statement ပြောင်းရုံပဲ။ `auth_sessions` မှာ `user_id` index ရှိပြီးသား (`migrations/0005_auth.sql`)။

---

## 1. Requirement / Acceptance Criteria

1. Account X ကို device A မှာ login → token A အလုပ်လုပ်တယ်။
2. **Same account** ကို device B မှာ login ထပ်ဝင် → **token A ချက်ချင်း ပျက်ရမယ်**။
   `GET /api/v1/auth/me` ကို A ရဲ့ token နဲ့ ခေါ်ရင် `401 INVALID_CREDENTIALS` ပြန်ရမယ်။
3. Device B ကနေ `GET /api/v1/devices` ခေါ်ရင် device A ကျွန်တော် link ဖြစ်မနေတော့ဘူး (revoked)။
4. Device A မှာ SSE connection ဖွင့်ထားရင် `session.revoked` ရပြီး ချက်ချင်း logout ဖြစ်ရမယ်။
5. Kick ခံရပြီးတဲ့ device A က **ပြန် login ဝင်လို့ရရမယ်** (`DEVICE_BOUND_TO_OTHER_ACCOUNT` မပြရဘူး)။
6. Same account ရဲ့ concurrent login ၂ ခု တစ်ပြိုင်နက်ဝင်ရင် **တစ်ခုပဲ အသက်ရှင်ရမယ်** (race မဖြစ်ရဘူး)။
7. Login အောင်မြင်တဲ့ device (device B) ကိုယ်တော့ **မ kick ခံရဘူး**။

---

## 2. အခုဘာဖြစ်နေလဲ (evidence)

### 2.1 Enforcement point အားလုံးက ဒီတစ်ကြေင်းပေါ်မှာ

`internal/platform/database/auth_store.go` — `Login()` (**tzm-branch :217**, master :205):

```go
if _, err = tx.Exec(ctx, `DELETE FROM auth_sessions WHERE device_id=$1`, result.DeviceID); err != nil {
```

**device တစ်ခုပဲ ဖျက်တယ်** — user ရဲ့ တစ်ခြား device session တွေကို မကြည့်ဘူး။ ဒါကြောင့် device B မှာ login ဝင်ပြီးရင် device A ရဲ့ token က **30 ရက်** (SessionLifetime, `internal/modules/auth/service.go:128`) အတိုင်း ဆက် valid ဖြစ်နေတယ်။

### 2.2 Session table က multi-session by design

`migrations/0005_auth.sql` / `EnsureAuthSchema` (`auth_store.go`):

```sql
CREATE TABLE IF NOT EXISTS auth_sessions(
    token_hash BYTEA PRIMARY KEY,
    user_id    TEXT NOT NULL REFERENCES prototype_users(id) ON DELETE CASCADE,
    device_id  UUID NOT NULL,          -- non-unique
    expires_at TIMESTAMPTZ NOT NULL, ...
);
CREATE INDEX IF NOT EXISTS auth_sessions_user_id_idx ON auth_sessions(user_id);  -- non-unique
```

### 2.3 Token က opaque — JWT မဟုတ်လို့ revoke က လွယ်တယ်

- Token = `crypto/rand` 32 bytes hex (`service.go:102`), DB ထဲမှာ SHA-256 hash ပဲ သိမ်းတယ်။ Refresh token မရှိဘူး။
- `Authenticate()` က **တိုင်း request မှာ** `auth_sessions` table ကို lookup လုပ်တယ် (`auth_store.go:236-253`)။
- ⇒ **Session row တစ်ခုကို delete လုပ်လိုက်ရင် နောက် request မှာ ချက်ချင်း 401 ရတယ်** — blacklist / token_version / jti ဘာမှ မလိုဘူး။

**ဒါကြောင့် fix က အနည်းငယ်ပဲ — `DELETE WHERE device_id=` ကို `WHERE user_id=` ပြောင်းရုံ။**

### 2.4 ဘာတွေရှိပြီးသားလဲ (ပြန်သုံးလို့ရတာ)

| ရှိပြီးသား | နေရာ |
|---|---|
| `DELETE FROM auth_sessions WHERE user_id=$1` (user-scoped wipe) | `auth_store.go:178` (`ResetPassword`), `:287` (`ChangePassword`), kline-admin `store.go` `ForceLogout` |
| `DeviceStore.Revoke()` — revoke + session/prekey/inbox/history cleanup + epoch advance | `internal/platform/database/device_store.go:124` (tzm-branch only) |
| `Authenticate` က revoked device ကို ငြင်း: `JOIN user_devices ... AND d.revoked_at IS NULL` | tzm-branch `auth_store.go` `Authenticate` |
| Revoked installation ပြန် login ဝင်လို့ရအောင် re-admit | tzm-branch `bindDevice` (`auth_store.go:360`) |
| SSE hub + topics (`client:` / `user:` / `device:`) | `internal/platform/asyncflow/hub.go:37-58`, `internal/transport/httpapi/async.go:48-96` |
| Kicked device logout UX (401 → auto logout) | `kline_app` — ပြီးသား |

---

## 3. ဘာကြောင့် `kline_app` တစ်ခုတည်းနဲ့ မရဘူးလဲ

| App-only နည်း | ဘာကြောင့် fail |
|---|---|
| `/auth/me` ကို ပိုမိုခြားနား poll | Token A က server မှာ **still valid** → 200 ပြန်တယ် |
| 401 ကို စောင့်တာ | Session A မဖျက်လို့ 401 **ဘယ်တော့မှ မကျဘူး** |
| Login ပြီး `DELETE /devices/:id` နဲ့ ဟောင်းကို kick | ① enforcement က client ပေါ်မှာပဲ မူတည် — old client / curl caller က bypass လုပ်နိုင်တယ် ② race window ရှိတယ် ③ offline device ကို မကိုင်နိုင်ဘူး |
| SSE `session.revoked` event | Event ထုတ်တာ **backend** (`hub.Publish`) — client ဘာမှ မလုပ်နိုင်ဘူး |

Session validity ဆုံးဖြတ်ချက်အားလုံး server-side မှာ ဖြစ်လို့ **server ကပဲ invalidate လုပ်ရမယ်**။

---

## 4. Fix ၁ (မဖြစ်မနေ) — Login မှာ user-scoped session wipe

**File:** `internal/platform/database/auth_store.go` → `Login()` (tzm-branch :184, delete က :217)

### 4.1 Before

```go
tx, err := s.pool.Begin(ctx)
...
defer func() { _ = tx.Rollback(ctx) }()
if _, err = tx.Exec(ctx, `DELETE FROM auth_sessions WHERE device_id=$1`, result.DeviceID); err != nil {
    return auth.Account{}, err
}
_, err = tx.Exec(ctx, `INSERT INTO auth_sessions(token_hash,user_id,device_id,expires_at) VALUES($1,$2,$3,$4)`,
    tokenHash, result.UserID, result.DeviceID, time.Now().Add(auth.SessionLifetime))
```

### 4.2 After (အကြံပြု implementation)

```go
tx, err := s.pool.Begin(ctx)
if err != nil {
    return auth.Account{}, err
}
defer func() { _ = tx.Rollback(ctx) }()

// (a) Serialize concurrent logins of the same account. Without this, two
//     simultaneous logins can interleave delete/insert and both survive.
if _, err = tx.Exec(ctx, `SELECT id FROM prototype_users WHERE id=$1 FOR UPDATE`, result.UserID); err != nil {
    return auth.Account{}, err
}

// (b) Remember who is about to be kicked, so the caller can notify them (Fix 3).
kicked := []string{}
rows, err := tx.Query(ctx, `SELECT device_id FROM auth_sessions WHERE user_id=$1 AND device_id<>$2`,
    result.UserID, result.DeviceID)
if err != nil {
    return auth.Account{}, err
}
for rows.Next() {
    var deviceID string
    if err = rows.Scan(&deviceID); err != nil {
        rows.Close()
        return auth.Account{}, err
    }
    kicked = append(kicked, deviceID)
}
rows.Close()
if rows.Err() != nil {
    return auth.Account{}, rows.Err()
}

// (c) THE FIX: single-device policy — the account may hold no other session.
if _, err = tx.Exec(ctx, `DELETE FROM auth_sessions WHERE user_id=$1`, result.UserID); err != nil {
    return auth.Account{}, err
}
_, err = tx.Exec(ctx, `INSERT INTO auth_sessions(token_hash,user_id,device_id,expires_at) VALUES($1,$2,$3,$4)`,
    tokenHash, result.UserID, result.DeviceID, time.Now().Add(auth.SessionLifetime))
if err == nil {
    err = tx.Commit(ctx)
}
result.Token = token
return result, err   // 4.3 ကြည့်ပါ — kicked ကို ပြန်ပို့ဖို့ signature လိုနိုင်တယ်
```

### 4.3 Kicked device ID တွေ ဘယ်သူ့ဆီ ပြန်ပို့မလဲ

နည်း ၂ ခု — တစ်ခုကို ရွေးပါ:

- **(A) တိကျတဲ့နည်း (recommended):** `auth.Store` interface (`internal/modules/auth/service.go:66-69`) ရဲ့
  `Login(...) (Account, error)` ကို `Login(...) (Account, []string, error)` (ဒါမှမဟုတ် small result struct) ပြောင်းပြီး kicked device IDs ပြန်ပို့။
  Implementations/mocks/tests အားလုံး ပြင်ရမယ်။
- **(B) ရိုးရှင်းတဲ့နည်း:** interface မပြောင်းဘူး — commit ပြီးမှ handler ကနေ
  kicked device တွေကို post-hoc query လုပ်။ Notification အတွက်ပဲ ဖြစ်လို့ race က လက်ခံနိုင်တယ် (enforcement က tx ထဲမှာ ပြီးသား)။
  **ဒါဆိုရင် Fix 2 ကို device row revoke မတိုင်ခင် (ရှိ/မရှိ) active device list ကို query ရမယ်။**

### 4.4 ဘာတွေ မပြောင်းရဘူး

| နေရာ | ဘာကြောင့် ပြောင်းစရာမလို |
|---|---|
| `Register()` + `createSession()` (`auth_store.go:98` master / tzm-branch equivalent) | User အသစ် — kick လုပ်စရာ တစ်ခြား session မရှိဘူး |
| `ResetPassword` (`:178`) / `ChangePassword` (`:287`) | `WHERE user_id=` သုံးပြီးသား |
| `Logout` (`:257`) | token-scoped — ကိုယ့် session ကိုယ်ပဲ ဖျက်တာ, မှန်တယ် |
| Admin `ForceLogout` (kline-admin) | `DELETE FROM auth_sessions WHERE user_id=$1` သုံးပြီးသား |
| Schema / migration | မလို (optional fix 4 ကလွဲ) |

---

## 5. Fix ၂ (မဖြစ်မနေ) — Kick ခံရတဲ့ device row တွေ cleanup

Session wipe တစ်ခုတည်းနဲ့ **enforcement ပြီးတယ်** — ဒါပေမယ့် `user_devices` ထဲမှာ ဟောင်း device တွေ "linked" အဖြစ် ကျန်ခဲ့ရင်:

- `GET /api/v1/devices` list မှာ ဟောင်း device ပေါ်နေမယ် (app ရဲ့ `verifySessionStillValid` က device list ကို ကြည့်တယ်)
- device A ရဲ့ prekey / inbox / history key envelope တွေ ဆက်ရှိနေမယ်
- message fan-out က ဟောင်း device ဆီ ဆက်ပို့နေမယ်

### 5.1 ရှိပြီးသား code ကို ပြန်သုံးပါ — `DeviceStore.Revoke`

`internal/platform/database/device_store.go:124` (tzm-branch) က လိုအပ်တဲ့ statement set အားလုံး လုပ်ပြီးသား:

```sql
UPDATE user_devices SET revoked_at=now(), revoked_reason=$3 WHERE device_id=$1 AND user_id=$2 AND revoked_at IS NULL;
DELETE FROM auth_sessions          WHERE device_id=$1;
DELETE FROM device_prekey_bundles  WHERE device_id=$1;
DELETE FROM device_one_time_prekeys WHERE device_id=$1;
DELETE FROM device_inbox           WHERE recipient_device_id=$1;
DELETE FROM device_delivery_cursors WHERE recipient_device_id=$1;
DELETE FROM history_key_envelopes  WHERE device_id=$1;
-- history key epoch advance (archive re-seal) ပါ ပါတယ်
```

`Login()` ရဲ့ tx ထဲမှာ (b) မှာ စုဆောင်းထားတဲ့ kicked device ID တိုင်းအတွက် ဒီ logic ကို **ပြန်သုံးပါ**
(inline ထည့်တာ ဒါမှမဟုတ် `DeviceStore` ကို `Login` ထံ pass လုပ်တာ — call direction ကို codebase convention နဲ့ ကိုက်အောင် ရွေးပါ)။

### 5.2 ⚠️ အဓိက သတိပြုရန် — ကိုယ့် device ကိုယ် မ revoke ရ

- `bindDevice()` က `Login()` ထက် **အရင်** ခေါ်တယ် (separate tx) — device B ရဲ့ row က fresh/re-admitted ဖြစ်ပြီးသား။
- Revoke loop မှာ **`device_id <> result.DeviceID` (login ဝင်တဲ့ device အသစ်) ကို အမြဲ ချန်ထားရမယ်**။
  မဟုတ်ရင် login ပြီးတာနဲ့ ကိုယ်ပါ ကိုယ့်ဘာသာ kick ခံရမယ် (acceptance #7 fail)။

### 5.3 ⚠️ ကိုယ့် installation ပြန် login ဝင်လို့ရအောင်

Kick ခံရတဲ့ device A က နောက်တစ်ခါ login ဝင်ရင် `ErrDeviceBound` (`DEVICE_BOUND_TO_OTHER_ACCOUNT`) မပြရဘူး (acceptance #5):

- **tzm-branch:** `bindDevice` က revoked installation ကို re-admit လုပ်ပြီးသား (`auth_store.go:360`, `revoked_at=NULL` + fresh `device_number`) — **ဘာမှ မလုပ်ရဘူး**။
- **master:** `auth_store.go:313` က `revokedAt != nil → ErrDeviceBound` ဆိုပြီး **အမြဲ ငြင်းတယ်** — ဒါဆိုရင် kick ခံရတဲ့ device ပြန်ဝင်လို့ မရတော့ဘူး။ master ပေါ် အလုပ်လုပ်ရင် ဒါကိုပြောင်းရမယ်။
  ⇒ **`tzm-branch` ကိုပဲ target လုပ်ပါ — fix နှစ်ခုလုံး အလိုအလျောက် ရှိ/လွယ်တယ်။**

---

## 6. Fix ၃ (recommended) — SSE `session.revoked` event

App ဘက်က ပြင်ပြီးပြီ: `kline_app/lib/app/services/prototype/prototype_session.dart` → `_handleRealtimeEvent()`
ထဲမှာ `case 'session.revoked':` ရှိတယ် — event ရရင် `revoked` flag တက်ပြီး
`AuthSessionService` က local account ဖျက် + `/auth` screen ကို ခေါ်သွားတယ်။

### 6.1 Publish point

**File:** `internal/transport/httpapi/auth.go:128` (login handler) — tx commit ပြီးမှ, error nil ရင်:

```go
v1.POST("/auth/login", func(c *gin.Context) {
    ...
    account, err := store.Login(c, body.Username, body.Password, body.Device)
    logAuthAttempt("login", body.Username, body.Device, account, err)
    if err == nil && hub != nil {
        for _, kickedDeviceID := range kickedDeviceIDs {   // Fix 1 က ပြန်ပို့တဲ့ list
            hub.Publish(asyncflow.Result{
                ID:         "session.revoked:" + kickedDeviceID,
                Type:       "session.revoked",
                DeviceID:   kickedDeviceID,        // ★ target
                Status:     "success",
                OccurredAt: time.Now().UTC(),
                Data:       json.RawMessage(`{"reason":"single_device_login"}`),
            })
        }
    }
    writeAuth(c, account, err)
})
```

> `hub` က router ထဲမှာ ရှိပြီးသား (`router.go:85` `registerSSERoute(protected, hub, ...)`,
> `app.go:121` `hub := asyncflow.NewHub()`, `app.go:151` hub ကို router ထံ pass) —
> login handler ထံ hub ပို့ဖို့ param တစ်ခု ထည့်ရမယ်
> (`registerAuthRoutes(...)` signature — `auth.go:44`)။

### 6.2 🚨 Event contract — `UserID` / `ClientID` **မထည့်ရ**

`hub.Publish()` (`hub.go:37-54`) က Result ရဲ့ `ClientID` / `UserID` / `DeviceID` အတွက် topic သုံးခုစလုံးကို publish လုပ်တယ်၊
SSE client တစ်ခုချင်းစီက `client:` / `user:` / `device:` topic သုံးခုစလုံးကို subscribe လုပ်ထားတယ် (`async.go:66`)။

- **`DeviceID` = kicked device** → မှန်တဲ့ device ပဲ ရမယ်။
- **`UserID` ထည့်ရင်** → `user:<id>` topic ကတစ်ဆင့် **account ရဲ့ device အားလုံး** ရမယ် —
  **login ဝင်တဲ့ device B ကိုယ်တော့ kick event ရပြီး ကိုယ့်ဘာသာ logout ဖြစ်သွားမယ်** (bug)။
- `ClientID` လည်း ထည့်မထားနဲ့ — `client:` (empty) topic ဟာ client_id မပို့တဲ့ SSE subscriber တွေနဲ့ တိုးနိုင်တယ်။

App ဘက်မှာ ဒုတိယအလွှာ အနေနဲ့ guard ရှိတယ် — event ထဲက `device_id` က ကိုယ့် `identity.deviceId` နဲ့
မတူရင် လက်မခံဘူး။ ဒါပေမယ့် backend ဘက်က မှန်မမှန် ရွေးချယ်စရာ မဟုတ်ဘူး — **contract အတိုင်း လုပ်ပါ**။

### 6.3 SSE ရဲ့ ကန့်သတ်ချက် (backend dev သိထားသင့်)

- SSE connection က handshake တစ်ခါပဲ authenticate လုပ်တယ်၊ heartbeat မှာ re-auth မလုပ်ဘူး (`async.go:85-90`)
  ⇒ session ပျက်သွားလို့ **ဖွင့်ထားတဲ့ connection က disconnect မဖြစ်ဘူး** — event ကတော့ ရောက်တယ်။ ✅
- Kicked device app က offline / SSE မဖွင့်ထားရင် event ပျောက်မယ် —
  fallback အနေနဲ့ app မှာ 60s `verifySessionStillValid()` poll နဲ့ `/auth/me` restore ရှိတယ်။
- Kick ပြီးမှ SSE reconnect ဖြစ်ရင် 401 ရမယ် → app က silent retry loop ပဲ (လက်ခံနိုင်တယ်)။

---

## 7. Optional — DB-level အားပေး

Statement ပြောင်းတာက app တစ်ခုတည်းကိုပဲ မထိန်းနိုင်ဘူး (direct SQL/API caller တွေ)။
DB ကိုယ်တိုင် enforce ချင်ရင်:

```sql
CREATE UNIQUE INDEX IF NOT EXISTS auth_sessions_one_per_user ON auth_sessions(user_id);
```

- ထည့်ရန်: migration file အသစ် (`migrations/0016_single_device_session.sql`) + `EnsureAuthSchema`
  (`auth_store.go` SQL string) **နှစ်နေရာစလုံး** — duplicate DDL ဖြစ်လို့။
- Unique violation (`23505`) ကို `FOR UPDATE` lock (fix 1a) က တားပေးရမယ်; ကျရင်လည်း
  23505 ကို retry/conflict အဖြစ် handle လုပ်ပါ။
- **မလိုအပ်ရင် မထည့်နဲ့** — fix 1 တစ်ခုတည်းနဲ့ requirement ပြီးတယ်။

---

## 8. ⚠️ Product decision — ဘာတွေ ချိုးပစ်မလဲ

လက်ရှိ system က **multi-device by design**။ Single-device policy က ဒီ features တွေကို သေစေမယ် —
**implement မလုပ်ခင် product ဘက်နဲ့ အတည်ပြုပါ:**

| Feature | နေရာ |
|---|---|
| Own-device fan-out (message → account's other devices) | `kline_app` `prototype_session.dart` `_fanOutToOwnDevices` |
| Linked devices screen + manual unlink | `kline_app` `linked_devices_screen.dart`, backend `devices.go` |
| History transfer / sealed archive / `device_number` allocation | `devices/lifecycle.go` (tzm-branch), migrations `0013`/`0015` |
| Multi-account per installation | `saved_account_store.dart`, migration `0014` |
| Design doc ကိုယ်တိုင်: "Multi-device Signal sessions … need further work" | `kline_app/doc/KLINE_SYSTEM_DESIGN_en.md:337` |

**ထင်ရှားတဲ့ သက်ရောက်မှု:** account တစ်ခုကို device ၂ ခု မချိတ်နိုင်တော့ဘူး —
history archive ကို တစ်ခြား device ကို လွှဲဖို့ စဉ်းစားစရာ (kick ခံရတဲ့ device ရဲ့ archive က
`DeviceStore.Revoke` က ဖျက်လိုက်မယ်)။

---

## 9. Tests

### Go (backend)

```go
// 1. single device policy
//    login A → login B (same account) → A token ရဲ့ Authenticate() က error ပြန်ရမယ်
// 2. same device re-login
//    login A twice with the SAME installation → 2 ခါစလုံး success, ErrDeviceBound မပြရ
// 3. kicked device can come back
//    login A → login B → login A ပြန် → success
// 4. concurrency
//    goroutine ၂ ခု တစ်ပြိုင်နက် login → auth_sessions ထဲမှာ row ၁ ခုပဲ ကျန်ရမယ်
// 5. device row cleanup
//    login B ပြီးရင် user_devices ထဲ A ရဲ့ revoked_at IS NOT NULL, B ရဲ့ revoked_at IS NULL
// 6. (optional) SSE session.revoked payload — DeviceID set, UserID empty
```

### App (kline_app)

- `integration_test/device_session_revoked_test.dart`, `test/multi_device_kick_test.dart` ရှိပြီးသား —
  ဒါတွေ **backend fix ပြီးမှ** run ရင် single-device behavior ကို အပြည့်အစုံ verify လုပ်နိုင်တယ်။
- App ဘက် `session.revoked` case ထည့်ထားပြီး — backend publish မလုပ်သေးလို့ E2E verify လုပ်၍မရသေးဘူး (verification gap)။

---

## 10. Verification

### 10.1 Manual (local backend `http://127.0.0.1:7080`)

```powershell
$base = 'http://127.0.0.1:7080'   # live ဆိုရင် https://kline-api.xhtd5566.com

function Post($path, $body, $token) {
  $h = @{ 'Content-Type' = 'application/json' }
  if ($token) { $h['Authorization'] = "Bearer $token" }
  Invoke-RestMethod -Uri "$base$path" -Method Post -Headers $h -Body ($body | ConvertTo-Json -Depth 6)
}
function Get-Auth($token) {
  try {
    Invoke-RestMethod -Uri "$base/api/v1/auth/me" -Headers @{ Authorization = "Bearer $token" }
    'FAIL: old token still valid'
  } catch {
    "OK: $($_.Exception.Response.StatusCode.value__) $($_.ErrorDetails.Message)"
  }
}

$dev = { param($model) @{
  installation_id = [guid]::NewGuid().ToString(); platform = 'linux'
  manufacturer = 'Test'; model = $model; os_version = '1.0'
  app_version = '1.0.0'; build_number = '1'; locale = 'en'; timezone = 'UTC' } }

$suf  = Get-Random -Maximum 99999999
$user = "sd_test_$suf"; $pw = 'SingleDevice123!'

$a = Post '/api/v1/auth/register' @{ display_name=$user; username=$user; password=$pw
  verification_channel=''; email=''; phone=''; device=(& $dev 'PhoneA') }

$b = Post '/api/v1/auth/login' @{ username=$user; password=$pw; device=(& $dev 'PhoneB') }

"device A token  (expect 401): "; Get-Auth $a.token
"device B token  (expect 200): "; (Invoke-RestMethod -Uri "$base/api/v1/auth/me" -Headers @{ Authorization = "Bearer $($b.token)" }).username
```

**Fix မလုပ်ခင်:** ပထမ line က `OK: 200` ပြလိမ့်မယ် (bug ရှိကြောင်း သက်သေ)။
**Fix ပြီးရင်:** `OK: 401` ဖြစ်ရမယ် + B token က 200 ဆက်ပြရမယ်။

### 10.2 SSE kick (Fix 3)

1. Device A မှာ app ဖွင့်ထား (SSE connected)။
2. Device B က login ဝင်။
3. Device A က **ချက်ချင်း** logout ဖြစ်ပြီး login screen ပေါ်ရမယ် (60s poll စောင့်စရာ မလို)။
4. A က app ပိတ်ထား/offline ဆိုရင် app ပြန်ဖွင့်တာနဲ့ `/auth/me` restore fail → account ဖယ်ရှားခံရမယ် (fallback, ရှိပြီးသား)။

---

## 11. Environment / branch warnings

1. **Local `kline-backend` = `origin/master`** — `origin/tzm-branch` ထက် 1 commit နောက်ကျန်တယ်
   (`git -C kline-backend rev-list --left-right --count origin/master...origin/tzm-branch` → `0  1`)။
   `/api/v1/devices*` endpoints တွေ local master မှာ **501 NOT_IMPLEMENTED** (`router.go:96-107` placeholder)။
   ⇒ **`tzm-branch` checkout / merge အရင်လုပ်ပါ** — ဒါမှ app ရဲ့ device features အလုပ်လုပ်မယ်။
2. **Deployed backend (`kline-api.xhtd5566.com`) ဘယ် branch/build လဲ မသိသေးဘူး** —
   deploy မလုပ်ခင် အရင် စစ်ပါ (app က tzm-branch endpoints ကို သုံးနေလို့ live ဟာလည်း tzm-branch ဖြစ်ရမယ်)။
3. **kline_app working tree က dirty** (staged 19 files) — app ဘက် change တစ်ခုတည်းထည့်ထားတယ်
   (`prototype_session.dart` `_handleRealtimeEvent` ထဲ `session.revoked` case)။ commit မလုပ်ရသေးဘူး။
4. Push channel (`push.Service.tokens`) က **in-memory `sync.Map`** — restart ရင် ပျောက်တယ်။
   Kick notification အတွက် push ကို မအားကိုးပါနဲ့ — **SSE ကိုပဲ သုံးပါ**။

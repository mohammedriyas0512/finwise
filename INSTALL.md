# FinWise — Install on PC, Laptop & Mobile

FinWise runs on every device. There is **no single binary that installs on
Windows + Android + iOS** — those are different operating systems. Instead you
get the two best options that together cover every device:

| Device | How to "install" | What you copy / do |
|--------|------------------|--------------------|
| Windows PC / laptop | Single `FinWise.exe` | Copy **one file** and double-click |
| Android phone/tablet | **Run natively in Termux** (server + PWA on the phone) | Copy folder, run `BUILD_ANDROID.sh` / `START_FinWise.sh` |
| Android phone/tablet | Install as an app (PWA) from a PC server | Open the URL in Chrome → "Install app" |
| iPhone / iPad | Add to Home Screen (PWA) | Open the URL in Safari → Share → Add to Home Screen |
| Linux / macOS | Native one-file binary or source | `bash BUILD_LINUX.sh` then run `dist_finwise/FinWise` |
| Any other PC/Mac | Install in browser (PWA) | Chrome/Edge → install icon in address bar |

Once installed, the app gets its own icon and takes device storage like a
normal app, and opens in its own window (no browser bar).

---

## 1. Windows — one file

Build once (`BUILD_EXE.bat`), then grab **`backend\dist_finwise\FinWise.exe`**.

That single `.exe` now contains the backend **and** the whole frontend inside
it — copy just that one file to any Windows PC/laptop or a USB stick and
double-click. On first run it creates `database\finwise.db` next to itself.
Fully portable, no Python needed on the target machine.

---

## 2. Mobile & other devices — installable app (PWA)

FinWise is a Progressive Web App, so it installs to the phone/PC like a native
app.

Steps:

1. On the PC that has `FinWise.exe`, run it. The console prints two URLs:
   ```
   http://127.0.0.1:8000/                 (this PC)
   http://<your-lan-ip>:8000/             (phone / other devices on same Wi-Fi)
   ```
2. Make sure the phone/laptop is on the **same Wi-Fi** as that PC.
3. Open the `http://<your-lan-ip>:8000/` URL on the device:
   - **Android (Chrome):** menu ⋮ → **Install app** (or the "Add to Home
     screen" prompt).
   - **iPhone (Safari):** Share button → **Add to Home Screen**.
   - **Desktop Chrome/Edge:** the **install icon** in the address bar.
4. The FinWise icon appears on the home screen / desktop and opens in its own
   window — installed and using device storage.

Notes:
- The PC running `FinWise.exe` acts as the server; keep it on while phones use
  the app. For a phones-work-anywhere setup, host the backend on a small
  server/VPS and point the devices at that public URL (then the PWA installs
  and works over the internet, and iOS/Android don't need the PC at all).
- iOS only allows PWA install from **Safari**. Android works from Chrome.
- A firewall prompt may appear the first time — allow FinWise on private
  networks so phones can reach it.

---

## 3. Android — run FinWise *on the phone itself* (Termux)

If you want FinWise to live entirely on your Android phone (no PC server needed,
works offline, data stays on the device), run the same stack inside **Termux**:

1. Install **Termux** from F-Droid — https://f-droid.org/packages/com.termux/
   (avoid the Play Store build; it is old and incomplete).
2. Open Termux and grant storage + install tooling:
   ```bash
   termux-setup-storage
   pkg update && pkg upgrade -y
   pkg install -y python clang libjpeg-turbo zlib make nodejs-lts git openssl termux-api
   ```
3. Copy the `FinWise/` folder onto the phone (Download folder, or `git clone`).
4. From inside the folder, run:
   ```bash
   cd FinWise
   bash BUILD_ANDROID.sh        # builds frontend + venv + starts the server
   ```
   (To just start an already-built copy: `bash START_FinWise.sh`.)

5. Open **http://127.0.0.1:8000/** in Chrome → menu ⋮ → **Install app**.
   To use it from another device over Wi-Fi, find the phone's LAN IP
   (`hostname -I`) and open `http://<phone-ip>:8000/` there.

This needs no root and no Play Store. The server runs inside Termux; keep that
session alive (optionally `termux-wake-lock`) while you use the app.

---

## Default login

```
email:    admin@finwise.app
password: Admin@123456
```

## Configuration

Edit `.env` (in the FinWise root, or place one beside `FinWise.exe`). Relative
SQLite paths resolve against the app folder, so the database follows the app
when you move it. For PostgreSQL set
`DATABASE_URL=postgresql+psycopg://user:pass@host:5432/finwise`.

"""FinWise movable-data utility.

FinWise stores ALL its data (SQLite db + uploads + exports + logs) in ONE
folder: "FinWiseData" next to the app (or wherever DATA_DIR points). This script
helps you back it up, restore, or relocate that single folder.

Commands:
  python manage_data.py info            Show where the data folder lives.
  python manage_data.py backup [dest]   Zip FinWiseData -> dest (default:
                                        FinWiseData-<date>.zip next to it).
  python manage_data.py restore <zip>   Extract a backup zip into DATA_DIR.
  python manage_data.py move <newdir>   Move FinWiseData to <newdir> and print
                                        the DATA_DIR line to put in .env.

The app must NOT be running while you restore/move (the db file is locked).

Examples:
  python manage_data.py backup
  python manage_data.py backup D:/Backups/finwise-2026.zip
  python manage_data.py restore D:/Backups/finwise-2026.zip
  python manage_data.py move E:/FinWiseData
"""
from __future__ import annotations

import os
import shutil
import sys
import zipfile
from datetime import datetime
from pathlib import Path

# Resolve DATA_DIR exactly like the app does (without importing the whole stack).
if getattr(sys, "frozen", False):
    APP_DIR = Path(sys.executable).resolve().parent
else:
    APP_DIR = Path(__file__).resolve().parent.parent  # backend/ -> FinWise/

_env = os.getenv("DATA_DIR")
if _env:
    DATA_DIR = (APP_DIR / _env) if not Path(_env).is_absolute() else Path(_env)
else:
    DATA_DIR = APP_DIR / "FinWiseData"


def cmd_info() -> int:
    print(f"App dir   : {APP_DIR}")
    print(f"Data dir  : {DATA_DIR}")
    print(f"DB file   : {DATA_DIR / 'database' / 'finwise.db'}")
    print(f"Exists    : {'yes' if DATA_DIR.exists() else 'no (will be created on first run)'}")
    if DATA_DIR.exists():
        db = DATA_DIR / "database" / "finwise.db"
        if db.exists():
            print(f"DB size   : {db.stat().st_size:,} bytes")
    print("\nTo point the app at a different folder, add to .env:")
    print(f'  DATA_DIR={DATA_DIR}')
    return 0


def cmd_backup(dest: str | None) -> int:
    if not DATA_DIR.exists():
        print(f"[backup] Nothing to back up: {DATA_DIR} does not exist yet.")
        return 1
    if dest:
        out = Path(dest)
        if out.suffix.lower() != ".zip":
            out = out.with_suffix(".zip")
    else:
        out = DATA_DIR.parent / f"FinWiseData-{datetime.now():%Y%m%d-%H%M%S}.zip"
    out.parent.mkdir(parents=True, exist_ok=True)
    print(f"[backup] Zipping {DATA_DIR} -> {out}")
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for p in DATA_DIR.rglob("*"):
            if p.is_file():
                z.write(p, p.relative_to(DATA_DIR.parent))
    print(f"[backup] Done: {out}")
    return 0


def cmd_restore(zip_path: str) -> int:
    zp = Path(zip_path)
    if not zp.is_file():
        print(f"[restore] File not found: {zp}")
        return 1
    if DATA_DIR.exists() and any(DATA_DIR.iterdir()):
        bak = DATA_DIR.parent / f"FinWiseData-before-restore-{datetime.now():%Y%m%d-%H%M%S}"
        print(f"[restore] Existing data backed aside to {bak}")
        shutil.move(str(DATA_DIR), str(bak))
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"[restore] Extracting {zp} -> {DATA_DIR}")
    with zipfile.ZipFile(zp) as z:
        # the backup stores paths as FinWiseData/... ; strip that prefix.
        for name in z.namelist():
            if name.endswith("/"):
                continue
            rel = Path(*Path(name).parts[1:]) if Path(name).parts[0].lower() == "finwisedata" else Path(name)
            target = DATA_DIR / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            with z.open(name) as src, open(target, "wb") as dst:
                dst.write(src.read())
    print(f"[restore] Done. Start FinWise to use the restored data.")
    return 0


def cmd_move(newdir: str) -> int:
    new = Path(newdir)
    if not new.is_absolute():
        new = APP_DIR / new
    if DATA_DIR.exists():
        print(f"[move] Moving {DATA_DIR} -> {new}")
        new.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(DATA_DIR), str(new))
    else:
        new.mkdir(parents=True, exist_ok=True)
        print(f"[move] Created empty data dir at {new}")
    print("[move] Add this line to FinWise/.env so the app finds it:")
    print(f"  DATA_DIR={new}")
    return 0


USAGE = __doc__


def main() -> int:
    args = sys.argv[1:]
    if not args:
        print(USAGE)
        return 1
    cmd = args[0].lower()
    if cmd == "info":
        return cmd_info()
    if cmd == "backup":
        return cmd_backup(args[1] if len(args) > 1 else None)
    if cmd == "restore":
        if len(args) < 2:
            print("[restore] Usage: manage_data.py restore <zip>")
            return 1
        return cmd_restore(args[1])
    if cmd == "move":
        if len(args) < 2:
            print("[move] Usage: manage_data.py move <newdir>")
            return 1
        return cmd_move(args[1])
    print(USAGE)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""CurseForge Profile Code Downloader"""

import sys
import json
import zipfile
import shutil
import tempfile
import re
import subprocess
import os
from pathlib import Path

# ── Set your download folder here, or leave as None to use the script's folder ──
DOWNLOAD_FOLDER = None

try:
    import requests
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests


def get_download_folder():
    if DOWNLOAD_FOLDER:
        folder = Path(DOWNLOAD_FOLDER)
    else:
        folder = Path(__file__).resolve().parent
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def get_pack_name(zip_path):
    try:
        with zipfile.ZipFile(zip_path) as z:
            for name in z.namelist():
                if Path(name).name.lower() in ("manifest.json", "minecraftinstance.json"):
                    return json.loads(z.read(name)).get("name")
    except Exception:
        pass
    return None


def main():
    print("CurseForge Profile Code Downloader\n")

    code = sys.argv[1].strip() if len(sys.argv) > 1 else input("Profile code: ").strip()
    if not code:
        return

    print("\nDownloading...")
    resp = requests.get(
        f"https://api.curseforge.com/v1/shared-profile/{code}",
        allow_redirects=True,
        stream=True,
        timeout=120,
    )

    if resp.status_code == 404:
        print("Code not found or expired.")
        input("Press Enter to exit...")
        return

    resp.raise_for_status()

    tmp = Path(tempfile.gettempdir()) / f"cf_{code}.zip"
    total = int(resp.headers.get("content-length", 0))
    done = 0
    with open(tmp, "wb") as f:
        for chunk in resp.iter_content(1024 * 1024):
            f.write(chunk)
            done += len(chunk)
            if total:
                print(f"\r  {done * 100 // total}%", end="")
    if total:
        print()

    name = get_pack_name(tmp) or code
    dest = get_download_folder() / f"{re.sub(r'[<>:\"/\\\\|?*]', '_', name)}.zip"
    if dest.exists():
        dest.unlink()
    shutil.move(str(tmp), str(dest))

    print(f"Pack: {name}")
    print(f"Saved to: {dest}")
    input("Press Enter to exit...")


if __name__ == "__main__":
    main()

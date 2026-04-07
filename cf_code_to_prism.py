#!/usr/bin/env python3
"""CurseForge Profile Code -> Prism Launcher"""

import sys
import json
import zipfile
import shutil
import tempfile
import re
import subprocess
import os
from pathlib import Path
import platform

try:
    import requests
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests


def find_prism():
    prism = shutil.which("prismlauncher")
    if prism:
        return prism
    if platform.system() == "Windows":
        for p in [
            Path.home() / "AppData" / "Local" / "Programs" / "PrismLauncher" / "prismlauncher.exe",
            Path(os.environ.get("PROGRAMFILES", "C:/Program Files")) / "PrismLauncher" / "prismlauncher.exe",
        ]:
            if p.exists():
                return str(p)
    return None


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
    print("CurseForge -> Prism Launcher\n")

    prism = find_prism()
    if not prism:
        print("Prism Launcher not found.")
        input("Press Enter to exit...")
        return

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
    final = tmp.parent / f"{re.sub(r'[<>:\"/\\\\|?*]', '_', name)}.zip"
    if final.exists():
        final.unlink()
    tmp.rename(final)

    print(f"Pack: {name}")
    print("Opening in Prism Launcher...")
    flags = 0
    if platform.system() == "Windows":
        flags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
    subprocess.Popen([prism, "-I", str(final)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=flags)
    os._exit(0)


if __name__ == "__main__":
    main()

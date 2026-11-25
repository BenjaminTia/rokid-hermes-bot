#!/usr/bin/env python3
"""Show the Hermes Bot setup QR code on Windows (no qrencode, no Preview).

The QR holds your Hermes API URL on the tailnet plus your API_SERVER_KEY, and
is read by the glasses' camera: look at it, tap the temple.

    python rokid-utils/hermes-bot-qr-windows.py

Settings:
    HERMES_HOME      Hermes home folder holding .env   (default: %LOCALAPPDATA%/hermes)
    HERMES_BOT_PORT  tailnet port Hermes is served on   (default: 8461)
    HERMES_BOT_URL   full URL, overrides port and tailnet name

Anyone who can photograph the window gets the key. Show it only to your
glasses and close it afterwards.

Requires: pip install qrcode  (Tkinter ships with Python)
"""

import json
import os
import pathlib
import subprocess
import sys
import tkinter as tk
from urllib.request import Request, urlopen

try:
    import qrcode
except ImportError:
    sys.exit("Needs the qrcode package: pip install qrcode")


def hermes_home() -> pathlib.Path:
    if os.environ.get("HERMES_HOME"):
        return pathlib.Path(os.environ["HERMES_HOME"])
    local = os.environ.get("LOCALAPPDATA")
    if local and (pathlib.Path(local) / "hermes" / ".env").exists():
        return pathlib.Path(local) / "hermes"
    return pathlib.Path.home() / ".hermes"


def read_key(home: pathlib.Path) -> str:
    env = home / ".env"
    if not env.exists():
        sys.exit(f"No .env in {home}. Set API_SERVER_ENABLED and API_SERVER_KEY first.")
    for line in env.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("API_SERVER_KEY="):
            key = line.split("=", 1)[1].strip().strip('"').strip("'")
            if len(key) >= 16:
                return key
    sys.exit(f"No usable API_SERVER_KEY in {env}")


def tailnet_host() -> str:
    try:
        out = subprocess.check_output(["tailscale", "status", "--json"], text=True)
    except (OSError, subprocess.CalledProcessError):
        sys.exit("The tailscale command is not on PATH, or Tailscale is not running.")
    data = json.loads(out)
    if data.get("BackendState") != "Running":
        sys.exit("Tailscale is not connected on this PC.")
    name = (data.get("Self") or {}).get("DNSName", "").rstrip(".")
    if not name:
        sys.exit("Tailscale is connected but MagicDNS is off, so the glasses have no name to use.")
    return name


def main() -> None:
    home = hermes_home()
    key = read_key(home)
    port = os.environ.get("HERMES_BOT_PORT", "8461")
    url = os.environ.get("HERMES_BOT_URL") or f"http://{tailnet_host()}:{port}"

    # Fail early if the API server is not up: the glasses would pair and then
    # fail on the first question.
    try:
        req = Request("http://127.0.0.1:8642/v1/models", headers={"Authorization": f"Bearer {key}"})
        with urlopen(req, timeout=8) as resp:
            if resp.status != 200:
                raise OSError(resp.status)
    except Exception:
        sys.exit("The Hermes API server is not answering with this key on 127.0.0.1:8642. "
                 "Check API_SERVER_* in .env and restart the gateway.")

    payload = json.dumps({"hermes": url, "key": key}, separators=(",", ":"))
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_L, border=4, box_size=1)
    qr.add_data(payload)
    qr.make(fit=True)
    matrix = qr.get_matrix()

    scale = 11
    root = tk.Tk()
    root.title("Private Hermes Bot setup QR")
    root.attributes("-topmost", True)
    canvas = tk.Canvas(root, width=len(matrix) * scale, height=len(matrix) * scale,
                       bg="white", highlightthickness=0)
    canvas.pack(padx=16, pady=12)
    for y, row in enumerate(matrix):
        for x, dark in enumerate(row):
            if dark:
                # Leave the -1 gap: outlines that overlap a neighbour's white
                # module make the code harder to read for the glasses camera.
                canvas.create_rectangle(x * scale, y * scale,
                                        (x + 1) * scale - 1, (y + 1) * scale - 1,
                                        fill="black", outline="")
    tk.Label(root, text=f"{url}\nPrivate setup code: scan with Hermes Bot, then close this window.").pack(pady=(0, 12))
    root.after(600_000, root.destroy)
    print(f"QR shown for {url}. Closes after 10 minutes.")
    root.mainloop()


if __name__ == "__main__":
    main()

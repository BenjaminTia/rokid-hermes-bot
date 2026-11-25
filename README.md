# Rokid Hermes Bot

Talk to your own [Hermes Agent](https://hermes-agent.nousresearch.com/) from Rokid Glasses. Ask by voice, get the answer on the display and read aloud, then keep going. A next-question queue is present but experimental; its known defects are listed below.

Derived from [flaibot/rokid-glasses-bots](https://github.com/flaibot/rokid-glasses-bots) (MIT), with Windows setup notes and a small set of fixes and additions described below.

```
Rokid Glasses ──Bluetooth──▶ Hi Rokid app on the phone ──Tailscale──▶ your PC
                                                                      └─ Hermes API server (127.0.0.1:8642)
```

## What it does

| You do | It does |
|---|---|
| "Hi Rokid, open Hermes Bot" | Opens on your last exchange and starts listening. |
| Speak | Sends after ~3 seconds of quiet. |
| Tap the temple | Talk now · send now · add another question to the queue (experimental) · interrupt a spoken reply. |
| Swipe | Next page of a long reply, earlier exchanges, or the menu. |
| Swipe while it is thinking | Cancels the request and any held questions. While the second capture is open, it cancels just that capture. |

Replies come back short and unformatted, because they are read aloud on a monochrome display.

## What this fork changes

**1. Setup QR scanner reworked.** Upstream hands the camera's WebP frame to a pure-JavaScript decoder (`decodeWebP`, webpjs, built with `new Function`) before the native `BarcodeDetector` sees it. The upstream scanner mounts the camera before the scan tap. A related WhatsApp scanner fix reports that the JavaScript decode can block; the precise cause of the Hermes scanner's failures has not been confirmed. This fork follows the technique in [upstream PR #1](https://github.com/flaibot/rokid-glasses-bots/pull/1): pass the encoded camera image straight to `BarcodeDetector` as a `Blob`, capture with `mode: 'wide'` and a system preview, and add 15-second capture and detection timeouts plus overlapping-tap and stale-result guards. PR #1 changes only `whatsapp-bot`, so Hermes Bot still has the old path on upstream `main`.

**2. Next-question queue (experimental; not finished).** Tapping while a reply is being worked out starts a second capture, holds what you say, and sends it after the current reply. Two defects are known and reproducible at mock level:

- Swiping away from the second capture calls `stopListening(true)`, which aborts the microphone and clears `recognition` but leaves `queueListening` set. The next tap then calls `stopListening(false)`, which no-ops, so the microphone cannot be reopened until the page is reopened.
- If the in-flight reply finishes while the second capture is still open, `drainQueue()` runs against an empty queue and the page goes idle. A question delivered afterwards is appended to the queue but never sent.

The queue is not part of any upstream PR, and neither defect has been fixed in this revision. Treat the queue as unusable for now.

**3. Windows server.** The upstream tooling assumes macOS (`zsh`, `qrencode`, Preview). A small Python script replaces the QR helper, writes the same payload, and shows it in a window for the glasses to scan.

## Verification status

- Setup scanner: covered by a mock test harness (8 checks). The same Blob/native-detector approach was used on Rokid Glasses in an earlier local build; this exact revision has not had a separate hardware run.
- Queue: the mock queue harness reproduces both defects above. No hardware verification.
- Windows QR helper: writes the documented payload using Tkinter and `qrcode`; no hardware claim is made for it.

## Set up

**PC side**

1. Turn on Hermes' API server, bound to loopback only:

   ```
   API_SERVER_ENABLED=true
   API_SERVER_HOST=127.0.0.1
   API_SERVER_PORT=8642
   API_SERVER_KEY=<openssl rand -hex 32>
   ```

   Restart the Hermes gateway afterwards.

2. Expose it to your tailnet only:

   ```
   tailscale serve --bg --http=8461 http://127.0.0.1:8642
   ```

3. Show the pairing code with your own tailnet name:

   ```
   python rokid-utils/hermes-bot-qr-windows.py
   ```

   The payload is `{"hermes": "http://<machine>.<tailnet>.ts.net:8461", "key": "<API_SERVER_KEY>"}`. It contains the key, so show it only to your glasses.

**Glasses side** (no cable, no ADB)

1. AIUI Studio → **New Agent → Import from local folder** → the `hermes-bot` folder.
2. **Device Debug → Package and Save** (this only packages for your own glasses, it does not submit anything).
3. On the glasses: **Settings → Developer → AIUI → Update glasses resources**.
4. Open Hermes Bot, scan the QR, ask something.

Keep the glasses' Wi-Fi **off** during setup: with Wi-Fi off the requests travel through the Hi Rokid app on the phone and your tailnet, which is the path Tailscale can carry.

## Notes on the key

The API server key gives access to your agent and all of its tools. It is stored on the glasses after pairing, never inside the app package. Rotate it by changing `API_SERVER_KEY`, restarting the gateway, and rescanning.

## Credits

Built on [flaibot/rokid-glasses-bots](https://github.com/flaibot/rokid-glasses-bots), which supplies the Hermes, Claude and WhatsApp bots and the iPhone-free install route. The setup-scanner approach follows [upstream PR #1](https://github.com/flaibot/rokid-glasses-bots/pull/1) by [@ShaBP](https://github.com/ShaBP); the diagnosis and technique are the PR author's, and this fork applies them to Hermes Bot. Upstream is MIT licensed; the original `LICENSE` and `THIRD_PARTY_NOTICES.md` are unchanged. This is an unofficial project, not affiliated with Rokid, Nous Research or Tailscale.

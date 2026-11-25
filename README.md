# Rokid Hermes Bot

Talk to your own [Hermes Agent](https://hermes-agent.nousresearch.com/) from Rokid Glasses. Ask by voice, get the answer on the display and read aloud, then keep going — including **queueing the next question while the current one is still being answered**.

Derived from [flaibot/rokid-glasses-bots](https://github.com/flaibot/rokid-glasses-bots) (MIT), with a working setup on Windows and a small set of fixes and additions described below.

```
Rokid Glasses ──Bluetooth──▶ Hi Rokid app on the phone ──Tailscale──▶ your PC
                                                                      └─ Hermes API server (127.0.0.1:8642)
```

## What it does

| You do | It does |
|---|---|
| "Hi Rokid, open Hermes Bot" | Opens on your last exchange and starts listening. |
| Speak | Sends after ~3 seconds of quiet. |
| Tap the temple | Talk now · send now · add another question to the queue · interrupt a spoken reply. |
| Swipe | Next page of a long reply, earlier exchanges, or the menu. |
| Swipe while it is thinking | Cancels the request and clears the queue. |

Replies come back short and unformatted, because they are read aloud on a monochrome display.

## What this fork changes

**1. The setup QR scanner actually works.** The original captured a photo in the same tap that mounted the camera, so the frame was empty and the code never decoded. This version matches Rokid's own scanning sample: the camera preview is mounted first, then `takePhoto({ quality: 'high', mode: 'wide', enableSystemPreview: true })`, then the native `BarcodeDetector` decodes the encoded image directly, with no blocking JavaScript WebP decode.

**2. Queueing while it thinks.** Tapping during a request no longer cancels it. It listens for the next question, holds it, and sends it in order when the current reply has finished being spoken. The hint shows the queue depth. Cancelling moved to a swipe so the old behaviour is still one gesture away.

**3. Windows server.** The upstream tooling assumes macOS (`zsh`, `qrencode`, Preview). A small Python script replaces the QR helper, writes the same payload, and shows it in a window for the glasses to scan.

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

Built on [flaibot/rokid-glasses-bots](https://github.com/flaibot/rokid-glasses-bots), which supplies the Hermes, Claude and WhatsApp bots and the iPhone-free install route. Upstream is MIT licensed; the original `LICENSE` and `THIRD_PARTY_NOTICES.md` are unchanged. This is an unofficial project, not affiliated with Rokid, Nous Research or Tailscale.

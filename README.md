# Rokid Hermes Bot

A voice interface for your own [Hermes Agent](https://hermes-agent.nousresearch.com/) on Rokid Glasses. Speak to Hermes, hear its reply and view text, images, equations or simple charts on the glasses.

This independent project is derived from [flaibot/rokid-glasses-bots](https://github.com/flaibot/rokid-glasses-bots), under its MIT licence. It adds a Windows pairing helper, a revised QR scanner, conversational controls, a question queue and experimental visual delivery. The original licence and third-party notices remain in this repository.

## Features

- Voice conversation, on-device history, Fast and Smart modes, and a menu.
- Tap while a reply is processing to queue a follow-up; swipe to stop the running request.
- A QR scanner using the native barcode detector, plus a Windows pairing helper.
- Experimental images through an authenticated Hermes connection, and native chart and TeX formula components.

## Status and limitations

**Experimental branch:** ordinary graph requests are routed to AIUI's native chart component rather than image generation. Mathematical expressions are requested in TeX by default. These changes have been exercised with the running Hermes API and automated tests, but this exact branch has not been tested on physical glasses. Model compliance, numerical accuracy and display layout are not guaranteed.

The maintainer has reported seeing image, equation and graph visuals on Rokid Glasses. Visuals remain experimental: rendering and recognizer support depend on the installed AIUI runtime, and an assistant may not always return a valid visual. Native graphs and LaTeX depend on structured model output; chart values should be independently checked.

The glasses use AIUI's `SpeechRecognition` and send recognised text to Hermes. The app does not itself call Deepgram; the runtime's recognition provider is not identified here. Hermes gateway voice-message transcription is a separate configuration.

Image requests use a non-streaming authenticated endpoint. They are limited to supported, bounded image data and are not saved in local conversation history. A stopped image request may continue on the server. The API key grants access to your agent and tools; the gateway's media-path rules do not eliminate prompt-injection or unintended image-disclosure risks. Use only on devices and networks you trust.

## Setup

1. Configure the Hermes API server to listen on `127.0.0.1` with a strong unique API key. Follow the [Hermes documentation](https://hermes-agent.nousresearch.com/docs/) for your platform.
2. Make the API reachable only to your authorised devices. For example, expose loopback to your private Tailscale network:

   ```sh
   tailscale serve --bg --http=8461 http://127.0.0.1:8642
   ```

   This example uses HTTP within the tailnet, not public HTTPS. Check the security requirements of your deployment.
3. Run `python rokid-utils/hermes-bot-qr-windows.py` on Windows to display the pairing QR. The QR contains the API key. Keep it private and never commit it.
4. In AIUI Studio, import the `hermes-bot` folder, then choose **Device Debug → Package and Save**. On the glasses, select **Settings → Developer → AIUI → Update glasses resources**. Open Hermes Bot and scan the QR.

See [the bot README](hermes-bot/README.md) for controls and tests. No APK, USB cable, ADB or store submission is required for this development route.

## Credits and licences

Based on [flaibot/rokid-glasses-bots](https://github.com/flaibot/rokid-glasses-bots). The native QR scanning approach follows [upstream PR #1](https://github.com/flaibot/rokid-glasses-bots/pull/1) by [@ShaBP](https://github.com/ShaBP). See [LICENSE](LICENSE) and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). This is an unofficial project, not affiliated with Rokid, Nous Research or Tailscale.

# Hermes Bot

An AIUI voice client for a privately reachable Hermes Agent API. See the [project README](../README.md) for setup, limitations and attribution.

## Controls

- Open the bot to talk; pause or tap to finish a question.
- Tap while Hermes is thinking to queue another question. Swipe while thinking to stop the request and clear queued questions.
- Swipe while listening or speaking to open the menu. The menu includes conversation history, settings, Fast/Smart mode and an optional status panel.
- Ask to show a picture or diagram for the experimental image route. Chart and formula rendering uses native AIUI components when Hermes returns a supported structured visual.

The glasses use AIUI's host speech recognition. The recognised text, not the microphone audio, is sent to Hermes by this app. The host recognizer's provider is not specified by this project.

## Development

Run `npm test` in this folder with Node.js. Run `npx @yodaos-pkg/aix-cli check .` and `npx @yodaos-pkg/aix-cli pack . -o <output.aix>` to check and package it. Automated tests use simulated hardware and do not replace a test on physical glasses.

The client keeps connection settings and conversation history in glasses storage, not the package. The API key gives powerful access to the agent, so keep pairing codes private. An image request may continue server-side if the client stops waiting.

Images, charts and formulas have been seen on the maintainer's glasses in a local build. Different runtime versions and models can behave differently; do not treat the PC tests as a guarantee of on-device behaviour.

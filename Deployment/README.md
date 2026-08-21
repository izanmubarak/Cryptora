# Hosting Cryptora

This document provides some guidance on how to host Cryptora.

## Tokens

Cryptora reads its API tokens from the environment. Anything you export in the shell — or pass to
Docker, or set in a systemd unit — is used directly:

```
export BOT_TOKEN=... CMC_TOKEN=... FMP_TOKEN=...
python3 app.py
```

For local development it is easier to keep them in a file. Copy `.env.example` from the project
root to `.env` and fill in your own values:

```
BOT_TOKEN=Your_BotFather_token_here
CMC_TOKEN=Your_CMC_API_token_here
FMP_TOKEN=Your_Financial_Modeling_Prep_token_here
MISTRAL_TOKEN=Your_Mistral_API_token_here
```

Paste each token directly after the `=`, with no quotation marks around it. Blank lines and lines
starting with `#` are ignored. `.env` is listed in `.gitignore`, so it will not be committed.

An environment variable always takes precedence over the same name in `.env`, which is what lets you
keep a development token in the file and override it in production without editing anything.

| Token | Required | Where to get it |
| --- | --- | --- |
| `BOT_TOKEN` | Yes | BotFather on Telegram |
| `CMC_TOKEN` | Yes | [coinmarketcap.com/api](https://coinmarketcap.com/api/) |
| `FMP_TOKEN` | Historical pricing only | [site.financialmodelingprep.com](https://site.financialmodelingprep.com/developer/docs) |
| `MISTRAL_TOKEN` | No | [console.mistral.ai](https://console.mistral.ai/) |


`MISTRAL_TOKEN` powers natural language queries (see "Anything else" in the main README). Without it,
Cryptora falls back to the typed commands and reports that the currency was not found for any query
it cannot parse — including historical pricing asked for with a relative date such as
`ethereum yesterday`, which needs the model. Absolute dates work either way.

## Running Cryptora

Once your tokens are in place, start the bot with `python3 app.py`. It will run indefinitely in the
terminal until you stop it with Ctrl-C.

If a token is missing or invalid, the failure usually surfaces as an error from the API it belongs
to: an invalid `CMC_TOKEN` produces a `KeyError` for the `data` dictionary, and python-telegram-bot
throws a self-explanatory error for an invalid `BOT_TOKEN`.

## Docker

The `Dockerfile` in this folder clones Cryptora from GitHub and installs its dependencies. Build and
run it with your `.env` file supplied at runtime, so no tokens are baked into the image:

```
docker build -t cryptora Deployment/
docker run --env-file .env cryptora python3 app.py
```

The image has no default command, so name the entry point explicitly as above.

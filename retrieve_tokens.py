# Cryptora - Public Repository

# This file reads in a provided tokens.txt file to retrieve the API tokens for the Telegram Bot API,
# the CoinMarketCap API, and the CoinDesk Data API.


def get_token(service):
    """Return the API token for the requested service.

    Args:
        service: "cmc" for CoinMarketCap, "bot" for Telegram Bot, "coindesk" for CoinDesk Data API.
                 Also accepts True for CoinMarketCap and False for Telegram Bot for backwards compatibility.
    """
    with open("tokens.txt") as f:
        tokens = {}
        for line in f:
            line = line.strip()
            if "=" in line:
                key, value = line.split("=", 1)
                tokens[key] = value

    if service is True or service == "cmc":
        return tokens.get("CMC_TOKEN", "")

    if service is False or service == "bot":
        return tokens.get("BOT_TOKEN", "")

    if service == "coindesk":
        return tokens.get("COINDESK_TOKEN", "")

    return ""

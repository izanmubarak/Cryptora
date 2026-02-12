# Cryptora - Public Repository

# This file reads in a provided tokens.txt file to retrieve the API tokens for the Telegram Bot API and
# the CoinMarketCap API.


def get_token(cmc):
    with open("tokens.txt") as f:
        cmc_token = f.readline().strip().split("=", 1)[1]
        bot_token = f.readline().strip().split("=", 1)[1]

    if cmc:
        return cmc_token

    return bot_token

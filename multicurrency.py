from uuid import uuid4

import requests
from telegram import InlineQueryResultArticle, InputTextMessageContent

from coin import CANONICAL_IDS, Coin, format_monetary_value, get_coin_map, is_known_coin
from retrieve_tokens import get_token


def looks_like_coin_list(query):
    # Return True if the query is a comma separated list of cryptocurrencies and nothing else
    parts = [part.strip() for part in query.split(",")]
    parts = [part for part in parts if part]
    return len(parts) >= 2 and all(is_known_coin(part) for part in parts)


def initialize_multicurrency_query(coin_names):
    token = get_token("cmc")
    coin_map = get_coin_map()
    data_url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?CMC_PRO_API_KEY={token}&id="
    search_string = ""
    ids = []
    coins = []

    for coin_name in coin_names:
        canonical_id = CANONICAL_IDS.get(coin_name.upper())
        if canonical_id is None:
            for cid in CANONICAL_IDS.values():
                for item in coin_map:
                    if item["id"] == cid and coin_name.lower() == item["name"].lower():
                        canonical_id = cid
                        break
                if canonical_id is not None:
                    break

        if canonical_id is not None:
            ids.append(str(canonical_id))
        else:
            for item in coin_map:
                if coin_name.lower() == item["name"].lower() or coin_name.upper() == item["symbol"]:
                    ids.append(str(item["id"]))
                    break

    search_string += ",".join(ids)
    data_url += search_string
    data = requests.get(data_url).json()["data"]
    for result in data.values():
        coin = Coin(None, result)
        if coin.exists:
            coins.append(coin)

    return coins


def generate_multi_currency_list(query):
    coins = [part.strip() for part in query.split(",")]
    coins = initialize_multicurrency_query([part for part in coins if part])

    prices = "***Selected Cryptocurrency Prices***\n\n"
    capitalizations = "***Selected Cryptocurrency Market Capitalizations***\n\n"
    changes = "***Selected Cryptocurrency 24 Hour Percent Change Values***\n\n"

    for coin in coins:
        prices += f"***{coin.name}:*** ${format_monetary_value(coin.price_usd)}\n"
        capitalizations += f"***{coin.name}:*** ${format_monetary_value(coin.market_cap)}\n"
        changes += f"***{coin.name}:*** {coin.percent_change}%\n"

    results = []
    if coins:
        results = [
            InlineQueryResultArticle(
                id=uuid4(),
                title="Prices",
                description="Tap to send.",
                thumbnail_url="https://imgur.com/7RCGCoc.png",
                input_message_content=InputTextMessageContent(prices, "Markdown"),
            ),
            InlineQueryResultArticle(
                id=uuid4(),
                title="Market Capitalizations",
                description="Tap to send.",
                thumbnail_url="https://i.imgur.com/UMczLVP.png",
                input_message_content=InputTextMessageContent(capitalizations, "Markdown"),
            ),
            InlineQueryResultArticle(
                id=uuid4(),
                title="Percent Change Values",
                description="Tap to send.",
                thumbnail_url="https://imgur.com/iAoXFQc.png",
                input_message_content=InputTextMessageContent(changes, "Markdown"),
            ),
        ]

    length = min(len(coins), 10)
    for i in range(length):
        results.append(
            InlineQueryResultArticle(
                id=uuid4(),
                description=f"${format_monetary_value(coins[i].price_usd)}",
                thumbnail_url=coins[i].image_url,
                title=f"{coins[i].name} ({coins[i].symbol})",
                input_message_content=InputTextMessageContent(coins[i].summary, "Markdown"),
            )
        )

    return results

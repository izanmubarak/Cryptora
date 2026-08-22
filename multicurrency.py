from coin import Coin, get_coin_map, is_known_coin, CANONICAL_IDS
from retrieve_tokens import get_token
from telegram import InlineQueryResultArticle, InputTextMessageContent
from uuid import uuid4
import requests


def looks_like_coin_list(query):
    # Return True if the query is a comma separated list of cryptocurrencies and nothing else
    parts = [part.strip() for part in query.split(",")]
    parts = [part for part in parts if part]
    return len(parts) >= 2 and all(is_known_coin(part) for part in parts)


def initialize_multicurrency_query(query):
    token = get_token(True)
    coin_map = get_coin_map()
    data_url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?CMC_PRO_API_KEY={token}&id="

    if query.endswith(","):
        query = query[:-1]
    if query.startswith(","):
        query = query[1:]

    currency_list = query.replace(", ", ",")
    currency_list = currency_list.split(",")

    coins = []

    for i in range(len(currency_list)):
        canonical_id = CANONICAL_IDS.get(currency_list[i].upper())
        if canonical_id is None:
            for symbol, cid in CANONICAL_IDS.items():
                for item in coin_map:
                    if item["id"] == cid and currency_list[i].lower() == item["name"].lower():
                        canonical_id = cid
                        break
                if canonical_id is not None:
                    break

        if canonical_id is not None:
            currency_list[i] = str(canonical_id)
        else:
            for item in coin_map:
                if currency_list[i].lower() == item["name"].lower() or currency_list[i].upper() == item["symbol"]:
                    currency_list[i] = str(item["id"])
                    break

    for i in range(len(currency_list)):
        data_url += currency_list[i] + ","

    data_url = data_url[:-1]
    data = requests.get(data_url).json()["data"]

    for i in range(len(currency_list)):
        coin = Coin(None, data[currency_list[i]])
        if coin.exists:
            coins.append(coin)

    return coins


def generate_multi_currency_list(query):
    coins = initialize_multicurrency_query(query)

    prices = "***Selected Cryptocurrency Prices***\n\n"
    capitalizations = "***Selected Cryptocurrency Market Capitalizations***\n\n"
    changes = "***Selected Cryptocurrency 24 Hour Percent Change Values***\n\n"

    for coin in coins:
        prices += f"***{coin.name}:*** ${coin.price_usd}\n"
        capitalizations += f"***{coin.name}:*** ${coin.market_cap}\n"
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
                description=f"${coins[i].price_usd}",
                thumbnail_url=coins[i].image_url,
                title=coins[i].name,
                input_message_content=InputTextMessageContent(coins[i].summary, "Markdown"),
            )
        )

    return results

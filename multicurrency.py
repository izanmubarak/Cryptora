# Cryptora - Public Repository
"""These functions provide the functionality for Cryptora's multi-currency search functionality. Users
can type in a list of currencies (such as "btc, ltc, eth, dash") and receive an inline list that shows
the price of each coin, with the option to send all of the coins' prices, market capitalizations, and
percent changes."""

from coin import Coin, format_monetary_value, get_coin_map
from retrieve_tokens import get_token
from decimal import Decimal
from telegram import InlineQueryResultArticle, ParseMode, InputTextMessageContent
from uuid import uuid4
import requests


def initialize_multicurrency_query(query):
    """Create a list that holds Coin objects, with each Coin object corresponding to the entered cryptocurrency."""
    token = get_token(True)
    coin_map = get_coin_map()
    data_url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?CMC_PRO_API_KEY={token}&id="

    # Parse the query, creating a list of strings that holds each individual entered cryptocurrency.
    if query.endswith(","):
        query = query[:-1]
    if query.startswith(","):
        query = query[1:]

    currency_list = query.replace(", ", ",")
    currency_list = currency_list.split(",")

    coins = []

    # Replace the list of coin names with their IDs.
    for i in range(len(currency_list)):
        for item in coin_map:
            if currency_list[i].lower() == item["name"].lower() or currency_list[i].upper() == item["symbol"]:
                currency_list[i] = str(item["id"])

    # Generate the JSON file with all the requested currencies.
    for i in range(len(currency_list)):
        data_url += currency_list[i] + ","

    # Remove the last comma from the URL and download the data
    data_url = data_url[:-1]
    data = requests.get(data_url).json()["data"]

    # Generate a Coin object for each entered cryptocurrency and add it to a list of Coin objects.
    for i in range(len(currency_list)):
        coin = Coin(None, data[currency_list[i]])

        # Filter out invalid entries using the "exists" variable.
        if coin.exists:
            coins.append(coin)

    return coins


def generate_multi_currency_list(query):
    """Create the list of options that is displayed to the user when they type a multicurrency query."""
    coins = initialize_multicurrency_query(query)

    prices = "***Selected Cryptocurrency Prices***\n\n"
    capitalizations = "***Selected Cryptocurrency Market Capitalizations***\n\n"
    changes = "***Selected Cryptocurrency 24 Hour Percent Change Values***\n\n"

    for coin in coins:
        prices += f"***{coin.name}:*** ${coin.price_usd}\n"
        capitalizations += f"***{coin.name}:*** ${coin.market_cap}\n"
        changes += f"***{coin.name}:*** {coin.percent_change}%\n"

    results = []

    # Add the "Prices", "Market Capitalizations", and "Percent Change Values" options
    if coins:
        results = [
            InlineQueryResultArticle(
                id=uuid4(),
                title="Prices",
                description="Tap to send.",
                thumb_url="https://imgur.com/7RCGCoc.png",
                input_message_content=InputTextMessageContent(prices, ParseMode.MARKDOWN),
            ),
            InlineQueryResultArticle(
                id=uuid4(),
                title="Market Capitalizations",
                description="Tap to send.",
                thumb_url="https://i.imgur.com/UMczLVP.png",
                input_message_content=InputTextMessageContent(capitalizations, ParseMode.MARKDOWN),
            ),
            InlineQueryResultArticle(
                id=uuid4(),
                title="Percent Change Values",
                description="Tap to send.",
                thumb_url="https://imgur.com/iAoXFQc.png",
                input_message_content=InputTextMessageContent(changes, ParseMode.MARKDOWN),
            ),
        ]

    # Cryptora allows users to put up to 10 coins in a multi-currency query.
    length = min(len(coins), 10)

    # Add each individual coin to the list.
    for x in range(length):
        results.append(
            InlineQueryResultArticle(
                id=uuid4(),
                description=f"${coins[x].price_usd}",
                thumb_url=coins[x].image_url,
                title=coins[x].name,
                input_message_content=InputTextMessageContent(coins[x].summary, ParseMode.MARKDOWN),
            )
        )

    return results

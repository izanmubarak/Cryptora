# Cryptora - Public Repository
# Provides conversion functionality between a cryptocurrency and U.S. dollars.

import requests
from decimal import Decimal
from coin import Coin, format_monetary_value
from telegram import InlineQueryResultArticle, InputTextMessageContent
from uuid import uuid4


def crypto_calculator(query, reverse):
    # Parse the query by splitting the string and reconstructing it to separate the numerical value
    # from the cryptocurrency name/symbol
    query_arr = query.split(" ")
    currency = " ".join(query_arr[1:])

    # Generate a Coin object.
    coin = Coin(currency, None)

    if not coin.exists:
        return []

    # Remove the commas from the already formatted value.
    price = coin.price_usd.replace(",", "")
    input_value = query_arr[0]

    if reverse:
        input_value = input_value[1:]
        value = format_monetary_value(float(input_value) / float(price), True)

        title = f"Convert ${input_value} to {coin.symbol}"
        description = f"Approximately {value} {coin.symbol}"
        message_content = f"${input_value} \u2248 {value} {coin.symbol}"
    else:
        value = format_monetary_value(float(price) * float(input_value), True)

        title = f"Convert {input_value} {coin.symbol} to USD"
        description = f"Approximately ${value}"
        message_content = f"{input_value} {coin.symbol} \u2248 ${value}"

    results = [
        InlineQueryResultArticle(
            id=uuid4(),
            thumbnail_url=f"https://s2.coinmarketcap.com/static/img/coins/200x200/{coin.ID}.png",
            title=title,
            description=description,
            input_message_content=InputTextMessageContent(message_content),
        )
    ]

    return results

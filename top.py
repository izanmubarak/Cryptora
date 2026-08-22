from uuid import uuid4

import requests
from telegram import InlineQueryResultArticle, InputTextMessageContent

from coin import Coin, format_monetary_value
from retrieve_tokens import get_token


def get_top_cryptocurrencies(list_size):
    token = get_token("cmc")
    data = requests.get(
        f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
        f"?CMC_PRO_API_KEY={token}&start=1&limit={list_size}&convert=USD&sort=market_cap"
    ).json()

    data = data["data"]
    top_str = f"***Top {list_size} Cryptocurrencies by Market Capitalization***\n\n"
    results = []

    for result in data:
        coin = Coin(None, result)
        top_str += f"#{coin.rank}. ***{coin.name}***: ${format_monetary_value(coin.market_cap)}\n"
        results.append(
            InlineQueryResultArticle(
                id=uuid4(),
                thumbnail_url=coin.image_url,
                description=f"${format_monetary_value(coin.price_usd)}",
                title=f"{coin.rank}. {coin.name} ({coin.symbol})",
                input_message_content=InputTextMessageContent(coin.summary, "Markdown"),
            )
        )

    results.insert(
        0,
        InlineQueryResultArticle(
            id=uuid4(),
            thumbnail_url="https://imgur.com/g6YajTp.png",
            description="Tap to send list.",
            title=f"Top {list_size} cryptocurrencies by market capitalization",
            input_message_content=InputTextMessageContent(top_str, "Markdown"),
        ),
    )

    return results

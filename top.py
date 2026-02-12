import requests
from retrieve_tokens import get_token
from coin import Coin, format_monetary_value
from decimal import Decimal
from telegram import InlineQueryResultArticle, ParseMode, InputTextMessageContent
from uuid import uuid4


def get_top_cryptocurrencies(list_size):
    token = get_token(True)
    data = requests.get(
        f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
        f"?CMC_PRO_API_KEY={token}&start=1&limit=50&convert=USD&sort=market_cap"
    ).json()

    data = data["data"]
    top_str = f"***Top {list_size} Cryptocurrencies by Market Capitalization***\n\n"
    results = []

    for x in range(list_size):
        coin = Coin(None, data[x])

        top_str += f"#{x + 1}. ***{coin.name}***: ${coin.market_cap}\n"

        results.append(
            InlineQueryResultArticle(
                id=uuid4(),
                thumb_url=coin.image_url,
                description=f"${coin.price_usd}",
                title=f"{coin.rank}. {coin.name} ({coin.symbol})",
                input_message_content=InputTextMessageContent(coin.summary, ParseMode.MARKDOWN),
            )
        )

    results.insert(
        0,
        InlineQueryResultArticle(
            id=uuid4(),
            thumb_url="https://imgur.com/g6YajTp.png",
            description="Tap to send list.",
            title=f"Top {list_size} cryptocurrencies by market capitalization",
            input_message_content=InputTextMessageContent(top_str, ParseMode.MARKDOWN),
        ),
    )

    return results

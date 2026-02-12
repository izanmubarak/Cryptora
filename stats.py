# Cryptora - Public Repository
# All global statistics.

from telegram import InlineQueryResultArticle, ParseMode, InputTextMessageContent
from retrieve_tokens import get_token
from coin import format_monetary_value
from uuid import uuid4
import requests
from decimal import Decimal


def get_global_data():
    """Fetch global cryptocurrency statistics from CoinMarketCap."""
    token = get_token(True)
    return requests.get(
        f"https://pro-api.coinmarketcap.com/v1/global-metrics/quotes/latest?CMC_PRO_API_KEY={token}"
    ).json()["data"]


def get_stats_list():
    data = get_global_data()

    market_cap = format_monetary_value(data["quote"]["USD"]["total_market_cap"], True)
    volume = format_monetary_value(data["quote"]["USD"]["total_volume_24h"], True)
    active_currencies = str(data["active_cryptocurrencies"])
    active_exchanges = str(data["active_exchanges"])
    dominance_eth = format_monetary_value(data["eth_dominance"], True)
    dominance_btc = format_monetary_value(data["btc_dominance"], True)

    global_stats_message = (
        f"***Global Cryptocurrency Statistics***\n\n"
        f"***Total Market Capitalization:*** ${market_cap}\n"
        f"***Total 24 Hour Volume:*** ${volume}\n"
        f"***Bitcoin Dominance:*** {dominance_btc}%\n"
        f"***Ethereum Dominance:*** {dominance_eth}%\n"
        f"***Total Active Currencies:*** {active_currencies}\n"
        f"***Total Active Exchanges:*** {active_exchanges}"
    )

    results = [
        InlineQueryResultArticle(
            id=uuid4(),
            title="Global Cryptocurrency Statistics",
            thumb_url="https://imgur.com/g6YajTp.png",
            description="Tap to send list.",
            input_message_content=InputTextMessageContent(global_stats_message, ParseMode.MARKDOWN),
        ),
        InlineQueryResultArticle(
            id=uuid4(),
            title="Total Market Capitalization",
            thumb_url="https://i.imgur.com/UMczLVP.png",
            description=f"${market_cap}",
            input_message_content=InputTextMessageContent(
                f"***Total Market Capitalization:*** ${market_cap}", ParseMode.MARKDOWN
            ),
        ),
        InlineQueryResultArticle(
            id=uuid4(),
            title="Total 24 Hour Volume",
            thumb_url="https://imgur.com/Qw4y4Ed.png",
            description=f"${volume}",
            input_message_content=InputTextMessageContent(
                f"***Total 24 Hour Volume:*** ${volume}", ParseMode.MARKDOWN
            ),
        ),
        InlineQueryResultArticle(
            id=uuid4(),
            title="Bitcoin Dominance",
            description=f"{dominance_btc}%",
            thumb_url="https://imgur.com/tXiapTn.png",
            input_message_content=InputTextMessageContent(
                f"***Bitcoin Dominance:*** {dominance_btc}%", ParseMode.MARKDOWN
            ),
        ),
        InlineQueryResultArticle(
            id=uuid4(),
            title="Ethereum Dominance",
            description=f"{dominance_eth}%",
            thumb_url="https://i.imgur.com/EMEUTYl.jpg",
            input_message_content=InputTextMessageContent(
                f"***Ethereum Dominance:*** {dominance_eth}%", ParseMode.MARKDOWN
            ),
        ),
        InlineQueryResultArticle(
            id=uuid4(),
            title="Active Cryptocurrencies",
            thumb_url="https://imgur.com/g6YajTp.png",
            description=f"{active_currencies} active cryptocurrencies",
            input_message_content=InputTextMessageContent(
                f"{active_currencies} active cryptocurrencies on CoinMarketCap.",
                ParseMode.MARKDOWN,
            ),
        ),
        InlineQueryResultArticle(
            id=uuid4(),
            thumb_url="https://imgur.com/qO0rcCI.png",
            title="Active Exchanges",
            description=f"{active_exchanges} active exchanges",
            input_message_content=InputTextMessageContent(
                f"{active_exchanges} active exchanges on CoinMarketCap.", ParseMode.MARKDOWN
            ),
        ),
    ]

    return results

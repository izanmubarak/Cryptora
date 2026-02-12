# Cryptora - Public Repository
# Coinbase Pro price retrieval functions.

import cbpro
from coin import format_monetary_value
from decimal import Decimal
from telegram import InlineQueryResultArticle, ParseMode, InputTextMessageContent
from uuid import uuid4


def get_GDAX_prices():
    # Retrieves cryptocurrency prices from Coinbase Pro using the cbpro Python API
    public_client = cbpro.PublicClient()

    btc = format_monetary_value(public_client.get_product_ticker(product_id="BTC-USD")["price"], True)
    ltc = format_monetary_value(public_client.get_product_ticker(product_id="LTC-USD")["price"], True)
    eth = format_monetary_value(public_client.get_product_ticker(product_id="ETH-USD")["price"], True)
    etc = format_monetary_value(public_client.get_product_ticker(product_id="ETC-USD")["price"], True)
    bch = format_monetary_value(public_client.get_product_ticker(product_id="BCH-USD")["price"], True)

    results = [
        InlineQueryResultArticle(
            id=uuid4(),
            title="Coinbase Pro Prices",
            thumb_url="https://i.imgur.com/nJff01I.png",
            description="Tap to send list.",
            input_message_content=InputTextMessageContent(
                f"***Coinbase Pro Trading Prices*** \n \n"
                f"***Bitcoin:*** ${btc}\n"
                f"***Litecoin:*** ${ltc}\n"
                f"***Ethereum:*** ${eth}\n"
                f"***Ethereum Classic:*** ${etc}\n"
                f"***Bitcoin Cash:*** ${bch}",
                ParseMode.MARKDOWN,
            ),
        ),
        InlineQueryResultArticle(
            id=uuid4(),
            title="Bitcoin (BTC)",
            thumb_url="https://s2.coinmarketcap.com/static/img/coins/200x200/1.png",
            description=f"${btc}",
            input_message_content=InputTextMessageContent(
                f"***Coinbase Pro Bitcoin Trading Price:*** ${btc}", ParseMode.MARKDOWN
            ),
        ),
        InlineQueryResultArticle(
            id=uuid4(),
            title="Litecoin (LTC)",
            description=f"${ltc}",
            thumb_url="https://s2.coinmarketcap.com/static/img/coins/200x200/2.png",
            input_message_content=InputTextMessageContent(
                f"***Coinbase Pro Litecoin Trading Price:*** ${ltc}", ParseMode.MARKDOWN
            ),
        ),
        InlineQueryResultArticle(
            id=uuid4(),
            title="Ethereum (ETH)",
            description=f"${eth}",
            thumb_url="https://s2.coinmarketcap.com/static/img/coins/200x200/1027.png",
            input_message_content=InputTextMessageContent(
                f"***Coinbase Pro Ethereum Trading Price:*** ${eth}", ParseMode.MARKDOWN
            ),
        ),
        InlineQueryResultArticle(
            id=uuid4(),
            title="Ethereum Classic (ETC)",
            description=f"${etc}",
            thumb_url="https://s2.coinmarketcap.com/static/img/coins/200x200/1321.png",
            input_message_content=InputTextMessageContent(
                f"***Coinbase Pro Ethereum Classic Trading Price:*** ${etc}", ParseMode.MARKDOWN
            ),
        ),
        InlineQueryResultArticle(
            id=uuid4(),
            title="Bitcoin Cash (BCH)",
            description=f"${bch}",
            thumb_url="https://s2.coinmarketcap.com/static/img/coins/200x200/1831.png",
            input_message_content=InputTextMessageContent(
                f"***Coinbase Pro Bitcoin Cash Trading Price:*** ${bch}", ParseMode.MARKDOWN
            ),
        ),
    ]

    return results

import logging
from datetime import datetime, timezone
from uuid import uuid4

import requests
from telegram import InlineQueryResultArticle, InputTextMessageContent

from coin import Coin, format_monetary_value, is_known_coin
from retrieve_tokens import get_token

logger = logging.getLogger(__name__)

# Absolute dates the classic "[cryptocurrency] [date]" command accepts. Relative dates
# ("2 weeks ago") are left to the language model.
DATE_FORMATS = (
    "%m/%d/%Y",
    "%m/%d/%y",
    "%B %d, %Y",
    "%b %d, %Y",
    "%B %d %Y",
    "%b %d %Y",
    "%Y-%m-%d",
)


def parse_trailing_date(query):
    """Split "bitcoin 08/21/2026" into a (currency, date) pair, or return None."""
    words = query.split()

    # A slash date is one trailing word; "August 21, 2026" is three.
    for tail_length in (1, 3):
        if len(words) <= tail_length:
            continue

        currency = " ".join(words[:-tail_length])
        if not is_known_coin(currency):
            continue

        tail = " ".join(words[-tail_length:])
        for date_format in DATE_FORMATS:
            try:
                date = datetime.strptime(tail, date_format).date()
            except ValueError:
                continue

            # Only completed days have historical open/high/low/close data.
            if date < datetime.now(timezone.utc).date():
                return currency, date

    return None


class PriceOnDay:
    def __init__(self, data):
        self.open = format_monetary_value(data.get("open"), True)
        self.high = format_monetary_value(data.get("high"), True)
        self.low = format_monetary_value(data.get("low"), True)
        self.close = format_monetary_value(data.get("close"), True)
        self.volume = format_monetary_value(data.get("volume"), False)


def download_historical_data(symbol, date):
    date_string = date.isoformat()
    try:
        response = requests.get(
            "https://financialmodelingprep.com/stable/historical-price-eod/full",
            params={
                "symbol": f"{symbol}USD",
                "from": date_string,
                "to": date_string,
                "apikey": get_token("fmp"),
            },
        ).json()
    except ValueError:
        logger.info("No historical data for %s on %s (unrecognized symbol).", symbol, date_string)
        return None
    except requests.RequestException as exc:
        logger.warning("Historical data request failed for %s on %s: %s", symbol, date_string, exc)
        return None

    if not isinstance(response, list) or not response:
        logger.info("No historical data for %s on %s.", symbol, date_string)
        return None

    return response[0]


def generate_historical_pricing_list(currency, date):
    converted_date = date.strftime("%B %d, %Y")

    coin = Coin(currency, None)
    if not coin.exists:
        return []

    data = download_historical_data(coin.symbol, date)
    if data is None:
        return []

    values = PriceOnDay(data)
    summary = (
        f"***Price Data for {coin.name}***\n{converted_date}\n\n"
        f"***Open:*** ${values.open}\n"
        f"***High:*** ${values.high}\n"
        f"***Low:*** ${values.low}\n"
        f"***Close:*** ${values.close}\n"
        f"***Volume:*** {values.volume} {coin.symbol}"
    )

    return [
        InlineQueryResultArticle(
            id=uuid4(),
            title=f"Price Data for {coin.name} ({coin.symbol})",
            description=converted_date,
            thumbnail_url=coin.image_url,
            input_message_content=InputTextMessageContent(summary, "Markdown"),
        ),
        InlineQueryResultArticle(
            id=uuid4(),
            title="Open",
            description=f"${values.open}",
            thumbnail_url="https://imgur.com/EYOqB1W.png",
            input_message_content=InputTextMessageContent(
                f"***{coin.name} Opening Price***\n{converted_date}\n\n${values.open}",
                "Markdown",
            ),
        ),
        InlineQueryResultArticle(
            id=uuid4(),
            title="High",
            description=f"${values.high}",
            thumbnail_url="https://imgur.com/ntXndWR.png",
            input_message_content=InputTextMessageContent(
                f"***{coin.name} High Price***\n{converted_date}\n\n${values.high}",
                "Markdown",
            ),
        ),
        InlineQueryResultArticle(
            id=uuid4(),
            title="Low",
            description=f"${values.low}",
            thumbnail_url="https://imgur.com/zOfZSYj.png",
            input_message_content=InputTextMessageContent(
                f"***{coin.name} Low Price***\n{converted_date}\n\n${values.low}",
                "Markdown",
            ),
        ),
        InlineQueryResultArticle(
            id=uuid4(),
            title="Close",
            description=f"${values.close}",
            thumbnail_url="https://imgur.com/iQXqgYU.png",
            input_message_content=InputTextMessageContent(
                f"***{coin.name} Closing Price***\n{converted_date}\n\n${values.close}",
                "Markdown",
            ),
        ),
        InlineQueryResultArticle(
            id=uuid4(),
            title="Volume",
            description=f"{values.volume} {coin.symbol}",
            thumbnail_url="https://imgur.com/qO0rcCI.png",
            input_message_content=InputTextMessageContent(
                f"***{coin.name} Volume***\n{converted_date}\n\n{values.volume} {coin.symbol}",
                "Markdown",
            ),
        ),
    ]

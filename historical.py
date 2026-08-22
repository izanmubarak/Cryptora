import logging
import datefinder
import dateparser
import requests
from telegram import InlineQueryResultArticle, InputTextMessageContent
from uuid import uuid4
from coin import Coin, format_monetary_value
from retrieve_tokens import get_token

logger = logging.getLogger(__name__)

class Date:
    def __init__(self, day, month, year, num_words):
        self.day = str(day).zfill(2)
        self.month = str(month).zfill(2)
        self.year = str(year)

        # This tells whether the date in the query was 3 words (i.e. August 17, 2018) or 1 word (i.e. 8/17/2018)
        self.num_words = num_words

class PriceOnDay:
    def __init__(self, data):
        self.open = format_monetary_value(data.get("open"), True)
        self.high = format_monetary_value(data.get("high"), True)
        self.low = format_monetary_value(data.get("low"), True)
        self.close = format_monetary_value(data.get("close"), True)
        self.volume = format_monetary_value(data.get("volume"), False)

def determine_if_date_in_string(query):
    """Uses Datefinder to parse the query for any dates present."""
    date_list = list(datefinder.find_dates(query))

    if "yesterday" in query or "ago" in query or len(date_list) > 0:
        return True

    return False


def get_date_from_query(query):
    """Finds the date in the query and returns a Date object."""
    date = ""

    if "yesterday" in query:
        date = dateparser.parse("yesterday")
        return Date(date.day, date.month, date.year, 1)

    elif "/" in query or "." in query:
        date = query.split(" ")
        separated_date = date[len(date) - 1]
        date = dateparser.parse(separated_date)
        return Date(date.day, date.month, date.year, 1)

    else:
        date = query.split(" ")
        separated_date = ""

        for x in range(len(date) - 3, len(date)):
            separated_date += date[x] + " "

        date = dateparser.parse(separated_date)
        return Date(date.day, date.month, date.year, 3)


def convert_month_number_to_name(month):
    """Converts a numbered month to its actual name."""
    months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December",
    ]
    return months[int(month) - 1]


def download_historical_data(symbol, date):
    date_string = f"{date.year}-{date.month}-{date.day}"
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
        logger.info("No historical data for %s on %s (unrecognised symbol).", symbol, date_string)
        return None
    except requests.RequestException as exc:
        logger.warning("Historical data request failed for %s on %s: %s", symbol, date_string, exc)
        return None

    if not isinstance(response, list) or not response:
        logger.info("No historical data for %s on %s.", symbol, date_string)
        return None

    return response[0]


def generate_historical_pricing_list(query):
    date = get_date_from_query(query)
    month_word = convert_month_number_to_name(date.month)
    converted_date = f"{month_word} {date.day}, {date.year}"

    split_query = query.split(" ")
    currency = ""

    # Get the name of the currency from the query.
    for x in range(len(split_query) - date.num_words):
        currency += split_query[x] + " "

    currency = currency[:-1]

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

    results = [
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

    return results

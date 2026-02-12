import datefinder
import dateparser
from bs4 import BeautifulSoup
import requests
from decimal import Decimal
from telegram import InlineQueryResultArticle, ParseMode, InputTextMessageContent
from uuid import uuid4
from coin import Coin, format_monetary_value

# Constant variables for clarity.
OPEN = 3
HIGH = 5
LOW = 7
CLOSE = 9
VOLUME = 11
MARKETCAP = 13


class Date:
    """Represents a date."""

    def __init__(self, day, month, year, num_words):
        self.day = str(day).zfill(2)
        self.month = str(month).zfill(2)
        self.year = str(year)

        # This tells whether the date in the query was 3 words (i.e. August 17, 2018) or 1 word (i.e. 8/17/2018)
        self.num_words = num_words


class PriceOnDay:
    """Represents a cryptocurrency's data on a certain day."""

    def __init__(self, values):
        self.open = format_monetary_value(float(values[OPEN][:-4]), True)
        self.high = format_monetary_value(float(values[HIGH][:-4]), True)
        self.low = format_monetary_value(float(values[LOW][:-4]), True)
        self.close = format_monetary_value(float(values[CLOSE][:-4]), True)
        self.volume = values[VOLUME][:-4]
        self.market_cap = values[MARKETCAP][:-4]


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


def generate_historical_pricing_list(query):
    """Constructs the historical pricing list."""
    date = get_date_from_query(query)
    month_word = convert_month_number_to_name(date.month)
    converted_date = f"{month_word} {date.day}, {date.year}"

    split_query = query.split(" ")
    currency = ""

    # Get the name of the currency from the query.
    for x in range(len(split_query) - date.num_words):
        currency += split_query[x] + " "

    currency = currency[:-1]

    # Generate a Coin object to quickly grab the image URL and the slug
    coin = Coin(currency, None)

    # Construct the URL from where the data will be scraped
    currency_url = (
        f"https://coinmarketcap.com/currencies/"
        f"{coin.slug}/historical-data/?start="
        f"{date.year}{date.month}{date.day}"
        f"&end={date.year}{date.month}{date.day}"
    )

    # Download and scrape the page using BeautifulSoup4 and requests.
    page = requests.get(currency_url)
    soup = BeautifulSoup(page.content, "html.parser")

    values = str(soup.find_all("td"))
    values = values.split(">")
    values = PriceOnDay(values)

    summary = (
        f"***Price Data for {coin.name}***\n{converted_date}\n\n"
        f"***Open:*** ${values.open}\n"
        f"***High:*** ${values.high}\n"
        f"***Low:*** ${values.low}\n"
        f"***Close:*** ${values.close}\n"
        f"***Volume:*** ${values.volume}\n"
        f"***Market Capitalization:*** ${values.market_cap}"
    )

    results = [
        InlineQueryResultArticle(
            id=uuid4(),
            title=f"Price Data for {coin.name} ({coin.symbol})",
            description=converted_date,
            thumb_url=coin.image_url,
            input_message_content=InputTextMessageContent(summary, ParseMode.MARKDOWN),
        ),
        InlineQueryResultArticle(
            id=uuid4(),
            title="Open",
            description=f"${values.open}",
            thumb_url="https://imgur.com/EYOqB1W.png",
            input_message_content=InputTextMessageContent(
                f"***{coin.name} Opening Price***\n{converted_date}\n\n${values.open}",
                ParseMode.MARKDOWN,
            ),
        ),
        InlineQueryResultArticle(
            id=uuid4(),
            title="High",
            description=f"${values.high}",
            thumb_url="https://imgur.com/ntXndWR.png",
            input_message_content=InputTextMessageContent(
                f"***{coin.name} High Price***\n{converted_date}\n\n${values.high}",
                ParseMode.MARKDOWN,
            ),
        ),
        InlineQueryResultArticle(
            id=uuid4(),
            title="Low",
            description=f"${values.low}",
            thumb_url="https://imgur.com/zOfZSYj.png",
            input_message_content=InputTextMessageContent(
                f"***{coin.name} Low Price***\n{converted_date}\n\n${values.low}",
                ParseMode.MARKDOWN,
            ),
        ),
        InlineQueryResultArticle(
            id=uuid4(),
            title="Close",
            description=f"${values.close}",
            thumb_url="https://imgur.com/iQXqgYU.png",
            input_message_content=InputTextMessageContent(
                f"***{coin.name} Closing Price***\n{converted_date}\n\n${values.close}",
                ParseMode.MARKDOWN,
            ),
        ),
        InlineQueryResultArticle(
            id=uuid4(),
            title="Volume",
            description=f"${values.volume}",
            thumb_url="https://imgur.com/qO0rcCI.png",
            input_message_content=InputTextMessageContent(
                f"***{coin.name} Volume***\n{converted_date}\n\n${values.volume}",
                ParseMode.MARKDOWN,
            ),
        ),
        InlineQueryResultArticle(
            id=uuid4(),
            title="Market Capitalization",
            description=f"${values.market_cap}",
            thumb_url="https://i.imgur.com/UMczLVP.png",
            input_message_content=InputTextMessageContent(
                f"***{coin.name} Market Capitalization***\n{converted_date}\n\n${values.market_cap}",
                ParseMode.MARKDOWN,
            ),
        ),
    ]

    return results

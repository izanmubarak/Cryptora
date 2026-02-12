# Cryptora - Public Repository
"""The Coin class represents a cryptocurrency and its metadata.
Cryptora currently displays the requested cryptocurrency's symbol, name, supply, market cap, price,
and percent change. The Coin class holds this information, as well as the summary of the coin that
is printed when the user clicks on the crypto's name in the popup list that appears."""

import requests
from decimal import Decimal
from retrieve_tokens import get_token
from telegram import InlineQueryResultArticle, InputTextMessageContent
from uuid import uuid4

# Download the full list of coins from CoinMarketCap. This list is parsed to find the user's coin,
# get the official name, symbol, and the coin's logo.
_coin_map = None

# Canonical CoinMarketCap IDs for major cryptocurrencies. When a query matches one of these,
# only the canonical coin is returned instead of showing a disambiguation list.
CANONICAL_IDS = {
    "BTC": 1,
    "ETH": 1027,
    "LTC": 2,
    "XRP": 52,
    "BCH": 1831,
    "ADA": 2010,
    "DOT": 6636,
    "DOGE": 74,
    "SOL": 5426,
    "BNB": 1839,
}


def get_coin_map():
    global _coin_map
    if _coin_map is None:
        token = get_token(True)
        _coin_map = requests.get(
            f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/map?CMC_PRO_API_KEY={token}"
        ).json()["data"]
    return _coin_map


class Coin:

    def __init__(self, query, data):
        coin_map = get_coin_map()

        # Record whether the coin exists. Used for multicurrency to filter out invalid entries.
        self.exists = False

        # Stores the currencies with the same name or symbol as a comma separated list.
        self.currencies_with_symbol = ""

        # Record the number of currencies found with the same symbol or name.
        self.occurrences = 0

        if data is None:
            # Check if the query matches a canonical cryptocurrency. If so, skip the full
            # scan and only use the canonical ID to avoid returning duplicate/shitcoins.
            canonical_id = CANONICAL_IDS.get(query.upper())
            if canonical_id is None:
                # Also check by name (e.g. "bitcoin" -> "BTC" -> 1)
                for symbol, cid in CANONICAL_IDS.items():
                    for item in coin_map:
                        if item["id"] == cid and query.lower() == item["name"].lower():
                            canonical_id = cid
                            break
                    if canonical_id is not None:
                        break

            for item in coin_map:
                # Cryptora supports both the name of the currency and its symbol for search.
                if query.upper() == item["symbol"] or query.lower() == item["name"].lower():
                    # If a canonical ID exists for this query, skip non-canonical matches.
                    if canonical_id is not None and item["id"] != canonical_id:
                        continue

                    self.exists = True

                    # Get the coin's full name, ID, date of first historical data, and symbol from CMC
                    self.symbol = item["symbol"]
                    self.name = item["name"]
                    self.slug = item["slug"]
                    self.ID = item["id"]
                    self.first_data = item["first_historical_data"]

                    # Store the IDs of each currency with the same symbol in a list.
                    self.currencies_with_symbol += f"{self.ID},"
                    self.occurrences += 1

                    # Get the coin's logo from CMC
                    self.image_url = f"https://s2.coinmarketcap.com/static/img/coins/200x200/{self.ID}.png"

                    # Get the metadata about the specific coin entered in JSON form
                    self.data = download_coin_data(self.ID)

                    # Parse and store the necessary data
                    self.rank = str(self.data["cmc_rank"])
                    self.supply = format_monetary_value(self.data["circulating_supply"], False)
                    self.market_cap = format_monetary_value(self.data["quote"]["USD"]["market_cap"], True)
                    self.price_usd = format_monetary_value(self.data["quote"]["USD"]["price"], True)

                    # Will always round percent changes to the hundredths place.
                    self.percent_change = str(
                        Decimal(self.data["quote"]["USD"]["percent_change_24h"])
                        .quantize(Decimal("1.00"), rounding="ROUND_HALF_DOWN")
                    )

                    # If using a canonical ID, we found our match - stop searching.
                    if canonical_id is not None:
                        break

        else:
            # This block generates a Coin object with a passed in JSON array containing all of the
            # coin's metadata. Used in "Top X" and multicurrency functionality.
            self.exists = True
            self.name = data["name"]
            self.symbol = data["symbol"]
            self.ID = data["id"]
            self.first_data = data["date_added"]
            self.image_url = f"https://s2.coinmarketcap.com/static/img/coins/200x200/{self.ID}.png"
            self.rank = str(data["cmc_rank"])
            self.supply = format_monetary_value(data["circulating_supply"], False)
            self.market_cap = format_monetary_value(data["quote"]["USD"]["market_cap"], True)
            self.price_usd = format_monetary_value(data["quote"]["USD"]["price"], True)
            self.percent_change = str(
                Decimal(data["quote"]["USD"]["percent_change_24h"])
                .quantize(Decimal("1.00"), rounding="ROUND_HALF_DOWN")
            )

        if self.exists:
            # Generate a summary that is displayed when the user clicks on the name of the coin
            self.summary = (
                f"***{self.name}*** ({self.symbol})\n\n"
                f"***Rank:*** #{self.rank} out of {len(coin_map)}\n"
                f"***Price***: ${self.price_usd}\n"
                f"***Market Capitalization***: ${self.market_cap}\n"
                f"***Circulating Supply***: {self.supply} {self.symbol}\n"
                f"***24 Hour Percent Change***: {self.percent_change}% \n"
            )


def download_coin_data(coin_id):
    """Download the JSON file that contains the data about the user's coin."""
    token = get_token(True)
    data = requests.get(
        f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?CMC_PRO_API_KEY={token}&id={coin_id}"
    ).json()
    return data["data"][str(coin_id)]


def format_monetary_value(value, decimals):
    """Format monetary values and percents correctly (with commas and decimal rounding)."""
    if value is None or value == 0:
        return "N/A"

    if abs(float(value)) >= 1.00:
        if decimals:
            value = Decimal(value).quantize(Decimal("1.00"), rounding="ROUND_HALF_DOWN")
        return f"{value:,}"
    else:
        return str(Decimal(value).quantize(Decimal("1.00000000"), rounding="ROUND_HALF_DOWN"))


def get_coin_info(query):
    """Generate the list displayed in the Telegram chat."""
    coin_map = get_coin_map()
    results = []
    coin = Coin(query, None)

    if coin.occurrences > 1:
        return generate_list_for_same_symbol_currencies(coin.currencies_with_symbol)

    if not coin.exists:
        return False

    results = [
        InlineQueryResultArticle(
            id=uuid4(),
            title=f"{coin.name} ({coin.symbol})",
            description=f"#{coin.rank} out of {len(coin_map)}",
            thumbnail_url=coin.image_url,
            input_message_content=InputTextMessageContent(coin.summary, "Markdown"),
        ),
        InlineQueryResultArticle(
            id=uuid4(),
            title="Price",
            description=f"${coin.price_usd}",
            thumbnail_url="https://imgur.com/7RCGCoc.png",
            input_message_content=InputTextMessageContent(f"1 {coin.symbol} = ${coin.price_usd}"),
        ),
        InlineQueryResultArticle(
            id=uuid4(),
            title="Market Capitalization",
            description=f"${coin.market_cap}",
            thumbnail_url="https://i.imgur.com/UMczLVP.png",
            input_message_content=InputTextMessageContent(
                f"Market Capitalization of {coin.name} ({coin.symbol}): ${coin.market_cap}"
            ),
        ),
        InlineQueryResultArticle(
            id=uuid4(),
            title="Circulating Supply",
            description=f"{coin.supply} {coin.symbol}",
            thumbnail_url="https://i.imgur.com/vXAN23U.png",
            input_message_content=InputTextMessageContent(
                f"Circulating Supply of {coin.name} ({coin.symbol}): {coin.supply} {coin.symbol}"
            ),
        ),
        InlineQueryResultArticle(
            id=uuid4(),
            title="Percent Change (24 hours)",
            description=f"{coin.percent_change}%",
            thumbnail_url="https://imgur.com/iAoXFQc.png",
            input_message_content=InputTextMessageContent(
                f"24 Hour Change in {coin.name} ({coin.symbol}) Price: {coin.percent_change}%"
            ),
        ),
    ]

    return results


def generate_list_for_same_symbol_currencies(currencies_with_symbol):
    """Generate the list for a currency symbol that corresponds to multiple currencies."""
    token = get_token(True)

    # Remove the last comma from the URL
    currencies_with_symbol = currencies_with_symbol[:-1]
    currency_list = currencies_with_symbol.split(",")

    results = []
    all_prices_list = "***Selected Cryptocurrency Prices***\n\n"

    data = requests.get(
        f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?CMC_PRO_API_KEY={token}&id={currencies_with_symbol}"
    ).json()["data"]

    for x in range(len(data)):
        coin = Coin(None, data[currency_list[x]])

        results.append(
            InlineQueryResultArticle(
                id=uuid4(),
                title=f"{coin.name} ({coin.symbol})",
                description=f"${coin.price_usd}",
                thumbnail_url=coin.image_url,
                input_message_content=InputTextMessageContent(coin.summary, "Markdown"),
            )
        )

        all_prices_list += f"***{coin.name}***: ${coin.price_usd}\n"

    results.insert(
        0,
        InlineQueryResultArticle(
            id=uuid4(),
            title="Multiple Currencies Found",
            description="Tap to send prices.",
            thumbnail_url="https://imgur.com/g6YajTp.png",
            input_message_content=InputTextMessageContent(all_prices_list, "Markdown"),
        ),
    )

    return results

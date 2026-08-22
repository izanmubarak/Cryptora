import requests
from decimal import Decimal
from retrieve_tokens import get_token
from telegram import InlineQueryResultArticle, InputTextMessageContent
from uuid import uuid4

_coin_map = None
_coin_lookup = None

# IDs for major cryptocurrencies (to prevent obscure memecoins with the same symbol from showing up)
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
        token = get_token("cmc")
        _coin_map = requests.get(
            f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/map?CMC_PRO_API_KEY={token}"
        ).json()["data"]
    return _coin_map


# Build a set of every symbol (uppercased) and name (lowercased) in the coin map to avoid unnecessary API calls
def get_coin_lookup():
    global _coin_lookup
    if _coin_lookup is None:
        _coin_lookup = set()
        for item in get_coin_map():
            _coin_lookup.add(item["symbol"].upper())
            _coin_lookup.add(item["name"].lower())
    return _coin_lookup


def is_known_coin(query):
    if not query:
        return False

    query = query.strip()
    if not query:
        return False

    lookup = get_coin_lookup()
    return query.upper() in lookup or query.lower() in lookup


class Coin:
    def __init__(self, query, data):
        coin_map = get_coin_map()

        # Record whether the coin exists. Used for multicurrency to filter out invalid entries.
        self.exists = False

        # Stores the currencies with the same name or symbol
        self.currencies_with_symbol = []

        if data is None:
            canonical_id = CANONICAL_IDS.get(query.upper())
            if canonical_id is None:
                for symbol, cid in CANONICAL_IDS.items():
                    for item in coin_map:
                        if item["id"] == cid and query.lower() == item["name"].lower():
                            canonical_id = cid
                            break
                    if canonical_id is not None:
                        break

            for item in coin_map:
                if query.upper() == item["symbol"] or query.lower() == item["name"].lower():
                    if canonical_id is not None and item["id"] != canonical_id:
                        continue

                    self.ID = item["id"]
                    data = download_coin_data(self.ID)

                    self.exists = True
                    self.symbol = item["symbol"]
                    self.name = item["name"]
                    self.slug = item["slug"]
                    self.first_data = item["first_historical_data"]
                    self.currencies_with_symbol.append(f"{self.ID}")
                    self.image_url = f"https://s2.coinmarketcap.com/static/img/coins/200x200/{self.ID}.png"
                    self.rank = str(data["cmc_rank"])
                    self.supply = format_monetary_value(data["circulating_supply"], False)
                    self.market_cap = data["quote"]["USD"]["market_cap"]
                    self.price_usd = data["quote"]["USD"]["price"]

                    percent_change = Decimal(data["quote"]["USD"]["percent_change_24h"]).quantize(Decimal("1.00"), rounding="ROUND_HALF_DOWN")
                    sign = "+" if percent_change >= 0 else "-"
                    self.percent_change = sign + str(percent_change)

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
            self.market_cap = data["quote"]["USD"]["market_cap"]
            self.price_usd = data["quote"]["USD"]["price"]
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
    token = get_token("cmc")
    data = requests.get(
        f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?CMC_PRO_API_KEY={token}&id={coin_id}"
    ).json()
    return data["data"][str(coin_id)]


def format_monetary_value(value, decimals=True):
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
    coin_map = get_coin_map()
    results = []
    coin = Coin(query, None)

    if len(coin.currencies_with_symbol) > 1:
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
            description=f"${format_monetary_value(coin.price_usd, True)}",
            thumbnail_url="https://imgur.com/7RCGCoc.png",
            input_message_content=InputTextMessageContent(f"1 {coin.symbol} = ${coin.price_usd}"),
        ),
        InlineQueryResultArticle(
            id=uuid4(),
            title="Market Capitalization",
            description=f"${format_monetary_value(coin.market_cap, True)}",
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
    token = get_token("cmc")

    search_string = ""
    for index, currency in enumerate(currencies_with_symbol):
        search_string += currency
        if index != len(currencies_with_symbol) - 1:
            search_string += ","

    results = []
    all_prices_list = "***Selected Cryptocurrency Prices***\n\n"

    data = requests.get(
        f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?CMC_PRO_API_KEY={token}&id={search_string}"
    ).json()["data"]

    for x in range(len(data)):
        coin = Coin(None, data[currencies_with_symbol[x]])
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

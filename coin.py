import time
from decimal import Decimal
from functools import lru_cache
from uuid import uuid4

import requests
from telegram import InlineQueryResultArticle, InputTextMessageContent

from retrieve_tokens import get_token

_coin_map = None
_coin_lookup = None
_last_fetch_time = 0
MIN_REFRESH_INTERVAL = 300  # 5-minute cooldown before re-fetching on a miss to prevent API spam

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


class Coin:
    def __init__(self, data=None):
        coin_map = get_coin_map()
        self.exists = bool(data)
        if not self.exists:
            return

        self.name = data.get("name", "")
        self.symbol = data.get("symbol", "")
        self.ID = data.get("id")
        self.first_data = data.get("date_added")
        self.image_url = f"https://s2.coinmarketcap.com/static/img/coins/200x200/{self.ID}.png"
        self.rank = str(data.get("cmc_rank", ""))
        self.supply = format_monetary_value(data.get("circulating_supply"), False)

        quote_data = data.get("quote", {})
        if isinstance(quote_data, list):
            usd_quote = next((q for q in quote_data if q.get("symbol") == "USD"), {})
        elif isinstance(quote_data, dict):
            usd_quote = quote_data.get("USD", {})
        else:
            usd_quote = {}

        self.market_cap = usd_quote.get("market_cap")
        self.price_usd = usd_quote.get("price")

        pct = usd_quote.get("percent_change_24h")
        if pct is not None:
            percent_change = Decimal(str(pct)).quantize(Decimal("1.00"), rounding="ROUND_HALF_DOWN")
            self.percent_change = f"{percent_change:+}"
        else:
            self.percent_change = "+0.00"

        self.summary = (
            f"***{self.name}*** ({self.symbol})\n\n"
            f"***Rank:*** #{self.rank} out of {len(coin_map)}\n"
            f"***Price***: ${format_monetary_value(self.price_usd)}\n"
            f"***Market Capitalization***: ${format_monetary_value(self.market_cap)}\n"
            f"***Circulating Supply***: {self.supply} {self.symbol}\n"
            f"***24 Hour Percent Change***: {self.percent_change}% \n"
        )


def fetch_fresh_coin_map():
    """Fetch the full coin list from CoinMarketCap and build lookup structures."""
    global _coin_map, _coin_lookup, _last_fetch_time
    token = get_token("cmc")
    try:
        data = (
            requests.get(
                f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/map?CMC_PRO_API_KEY={token}",
                timeout=10,
            )
            .json()
            .get("data", [])
        )
        _coin_map = data
        _coin_lookup = set()
        for item in _coin_map:
            _coin_lookup.add(item["symbol"].upper())
            _coin_lookup.add(item["name"].lower())
        _last_fetch_time = time.time()
        _resolve_single_coin.cache_clear()
    except Exception:
        if _coin_map is None:
            _coin_map = []
            _coin_lookup = set()


def get_coin_map():
    if _coin_map is None:
        fetch_fresh_coin_map()
    return _coin_map


def get_coin_lookup():
    if _coin_lookup is None:
        fetch_fresh_coin_map()
    return _coin_lookup


def maybe_refresh_on_miss():
    """If the map hasn't been refreshed within MIN_REFRESH_INTERVAL, fetch a fresh one."""
    elapsed = time.time() - _last_fetch_time
    if elapsed > MIN_REFRESH_INTERVAL:
        fetch_fresh_coin_map()
        return True
    return False


def is_known_coin(query):
    """Fast in-memory check if a query is a recognized cryptocurrency symbol or name."""
    if not query:
        return False

    query = query.strip()
    if not query:
        return False

    lookup = get_coin_lookup()
    return query.upper() in lookup or query.lower() in lookup


@lru_cache(maxsize=2048)
def _resolve_single_coin(query):
    """Resolve a single coin query (symbol or name) to (symbol, cmc_id)."""
    if not query:
        return None

    query = query.strip()
    coin_map = get_coin_map()

    canonical_id = CANONICAL_IDS.get(query.upper())
    if canonical_id is None:
        for cid in CANONICAL_IDS.values():
            for item in coin_map:
                if item["id"] == cid and query.lower() == item["name"].lower():
                    canonical_id = cid
                    break
            if canonical_id is not None:
                break

    if canonical_id is not None:
        for item in coin_map:
            if item["id"] == canonical_id:
                return (item["symbol"].upper(), canonical_id)

    for item in coin_map:
        if query.lower() == item["name"].lower() or query.upper() == item["symbol"]:
            return (item["symbol"].upper(), item["id"])

    return None


def resolve_coin_ids(queries):
    """Resolve a list of coin queries (symbols or names) to CoinMarketCap IDs.

    Uses memoized lookups and automatically refreshes on a miss for new coins.
    """
    resolved = []
    for query in queries:
        res = _resolve_single_coin(query)
        if res is None and maybe_refresh_on_miss():
            res = _resolve_single_coin(query)
        if res is not None:
            resolved.append(res)

    return resolved


def download_coin_data(coin_id):
    token = get_token("cmc")
    data = requests.get(
        f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?CMC_PRO_API_KEY={token}&id={coin_id}"
    ).json()
    return data["data"][str(coin_id)]


def get_currencies_with_symbol(query):
    """Find all CMC IDs matching a query, prioritizing canonical IDs."""
    coin_map = get_coin_map()
    canonical_id = CANONICAL_IDS.get(query.upper())
    if canonical_id is None:
        for cid in CANONICAL_IDS.values():
            for item in coin_map:
                if item["id"] == cid and query.lower() == item["name"].lower():
                    canonical_id = cid
                    break
            if canonical_id is not None:
                break

    if canonical_id is not None:
        return [str(canonical_id)]

    matches = [
        str(item["id"])
        for item in coin_map
        if query.upper() == item["symbol"] or query.lower() == item["name"].lower()
    ]

    if not matches and maybe_refresh_on_miss():
        coin_map = get_coin_map()
        matches = [
            str(item["id"])
            for item in coin_map
            if query.upper() == item["symbol"] or query.lower() == item["name"].lower()
        ]

    return matches


def get_coin(query):
    """Resolve and fetch a single Coin object for a given query (symbol or name)."""
    matches = get_currencies_with_symbol(query)
    if not matches:
        return None
    data = download_coin_data(matches[0])
    return Coin(data)


def get_coin_info(query):
    coin_map = get_coin_map()
    matches = get_currencies_with_symbol(query)

    if not matches:
        return False

    if len(matches) > 1:
        return generate_list_for_same_symbol_currencies(matches)

    data = download_coin_data(matches[0])
    coin = Coin(data)

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
            input_message_content=InputTextMessageContent(
                f"1 {coin.symbol} = ${format_monetary_value(coin.price_usd)}"
            ),
        ),
        InlineQueryResultArticle(
            id=uuid4(),
            title="Market Capitalization",
            description=f"${format_monetary_value(coin.market_cap, True)}",
            thumbnail_url="https://i.imgur.com/UMczLVP.png",
            input_message_content=InputTextMessageContent(
                f"Market Capitalization of {coin.name} ({coin.symbol}): ${format_monetary_value(coin.market_cap)}"
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
    token = get_token("cmc")
    results = []
    search_string = ",".join(currencies_with_symbol)
    all_prices_list = "***Selected Cryptocurrency Prices***\n\n"
    data = requests.get(
        f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?CMC_PRO_API_KEY={token}&id={search_string}"
    ).json()["data"]

    for result in data.values():
        coin = Coin(result)
        results.append(
            InlineQueryResultArticle(
                id=uuid4(),
                title=f"{coin.name} ({coin.symbol})",
                description=f"${format_monetary_value(coin.price_usd)}",
                thumbnail_url=coin.image_url,
                input_message_content=InputTextMessageContent(coin.summary, "Markdown"),
            )
        )
        all_prices_list += f"***{coin.name}***: ${format_monetary_value(coin.price_usd)}\n"

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

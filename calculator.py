import math
import re
from coin import Coin, format_monetary_value
from telegram import InlineQueryResultArticle, InputTextMessageContent
from uuid import uuid4

SUFFIX_MULTIPLIERS = {"k": 1_000, "m": 1_000_000, "b": 1_000_000_000, "t": 1_000_000_000_000}

_AMOUNT_PATTERN = re.compile(
    r"""^\$?\s*                          # an optional dollar sign
        (\d{1,3}(?:,\d{3})+|\d*)         # whole part, either comma grouped or plain
        (\.\d+)?                         # optional decimal part
        ([kmbt])?                        # optional magnitude suffix, attached to the number
        $""",
    re.IGNORECASE | re.VERBOSE,
)

# Parse the numeric half of a calculator query into a float
def parse_amount(text):
    if not isinstance(text, str):
        return None

    match = _AMOUNT_PATTERN.match(text.strip())
    if not match:
        return None

    whole, fraction, suffix = match.groups()

    # The whole part may be empty ("$.5"), but not when there is no fraction either.
    if not whole and not fraction:
        return None

    try:
        value = float(whole.replace(",", "") + (fraction or ""))
    except ValueError:
        return None

    if suffix:
        value *= SUFFIX_MULTIPLIERS[suffix.lower()]

    if not math.isfinite(value) or value <= 0:
        return None

    return value


def crypto_calculator(query, reverse):
    query_arr = query.split(" ")
    currency = " ".join(query_arr[1:])
    coin = Coin(currency, None)

    if not coin.exists:
        return []

    amount = parse_amount(query_arr[0])
    if amount is None:
        return []

    if coin.price_usd <= 0:
        return []

    if reverse:
        value = format_monetary_value(amount / coin.price_usd, True)
        title = f"Convert ${format_monetary_value(amount)} to {coin.symbol}"
        description = f"Approximately {value} {coin.symbol}"
        message_content = f"${format_monetary_value(amount)} \u2248 {value} {coin.symbol}"
    else:
        value = format_monetary_value(coin.price_usd * amount, True)
        amount = f"{int(amount):,}" if amount.is_integer() else f"{amount:,}"
        title = f"Convert {amount} {coin.symbol} to USD"
        description = f"Approximately ${value}"
        message_content = f"{amount} {coin.symbol} \u2248 ${value}"

    results = [
        InlineQueryResultArticle(
            id=uuid4(),
            thumbnail_url=f"https://s2.coinmarketcap.com/static/img/coins/200x200/{coin.ID}.png",
            title=title,
            description=description,
            input_message_content=InputTextMessageContent(message_content),
        )
    ]

    return results

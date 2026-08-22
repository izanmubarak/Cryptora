import asyncio
import json
import logging
import re
import time
from collections import OrderedDict, deque
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from telegram import InlineQueryResultArticle

from calculator import crypto_calculator
from coin import get_coin_info, is_known_coin
from historical import generate_historical_pricing_list
from multicurrency import generate_multi_currency_list
from news import get_news_list
from retrieve_tokens import get_token
from stats import get_stats_list
from top import get_top_cryptocurrencies

logger = logging.getLogger(__name__)
MODEL = "ministral-3b-latest"
REQUEST_TIMEOUT = 4.0
MAX_TOP_LIST_SIZE = 49
DEFAULT_TOP_LIST_SIZE = 40
MAX_MULTICURRENCY_COINS = 10
STRICT_SCHEMA = True
CACHE_SIZE = 512
_cache = OrderedDict()

ROUTES = (
    "coin",
    "multicurrency",
    "crypto_to_usd",
    "usd_to_crypto",
    "historical",
    "top",
    "stats",
    "news",
    "unknown",
)

UNKNOWN = {"route": "unknown"}
DISABLED_ROUTES = {
    "historical": "Historical pricing is currently unavailable.",
    "news": "News is currently unavailable.",
}

RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "route": {"type": "string", "enum": list(ROUTES)},
        "coins": {"type": "array", "items": {"type": "string"}},
        "amount": {"type": "number"},
        "date": {"type": "string"},
        "limit": {"type": "integer"},
    },
    "required": ["route", "coins"],
}

_client = None
_client_unavailable = False


def build_system_prompt(today):
    """Build the routing instructions. Today's date is injected so relative dates can be resolved."""
    yesterday = (today - timedelta(days=1)).isoformat()

    return f"""Route a cryptocurrency bot query to one feature. Today is {today.isoformat()} (UTC).

coin: one coin. multicurrency: several coins. top: ranked list (limit).
stats: whole market. news: headlines. historical: one coin on a past date (date).
crypto_to_usd: what an amount OF COIN is worth in dollars (amount = coin quantity).
usd_to_crypto: what a DOLLAR amount buys (amount = dollars).
unknown: anything else, or when unsure.

If the number is money ($, dollars, bucks) use usd_to_crypto; if it counts coins use crypto_to_usd.
A conversion needs a quantity the user actually wrote. No quantity means coin, never a conversion.
Always include "coins" ([] if none). Never invent a coin. Dates must be past, YYYY-MM-DD.

"half a bitcoin in dollars" {{"route":"crypto_to_usd","coins":["bitcoin"],"amount":0.5}}
"what do I get for 500 bucks of eth" {{"route":"usd_to_crypto","coins":["ETH"],"amount":500}}
"bitcoin price yesterday" {{"route":"historical","coins":["bitcoin"],"date":"{yesterday}"}}
"20 biggest coins" {{"route":"top","coins":[],"limit":20}}
"how is the market doing" {{"route":"stats","coins":[]}}
"anything happening in crypto" {{"route":"news","coins":[]}}
"compare bitcoin and solana" {{"route":"multicurrency","coins":["bitcoin","solana"]}}
"tell me about dogecoin" {{"route":"coin","coins":["dogecoin"]}}
"bitcoin today" {{"route":"coin","coins":["bitcoin"]}}
"hey there" {{"route":"unknown","coins":[]}}"""


def get_client():
    global _client, _client_unavailable

    if _client_unavailable:
        return None

    if _client is None:
        token = get_token("mistral")
        if not token:
            logger.warning(
                "No MISTRAL_TOKEN found in tokens.txt. Natural language query routing is disabled."
            )
            _client_unavailable = True
            return None

        try:
            from mistralai.client import Mistral
        except ImportError:
            logger.warning(
                "The mistralai package is not installed. Natural language query routing is disabled."
            )
            _client_unavailable = True
            return None

        _client = Mistral(api_key=token)

    return _client



def build_cache_key(query, today):
    """Key routing decisions by date, so that relative dates do not survive past midnight."""
    return (today.isoformat(), query.strip().lower())


def is_cached(query):
    """Return True if this query's route is already known and needs no request to answer."""
    today = datetime.now(timezone.utc).date()
    return build_cache_key(query, today) in _cache


# Classify a natural language query, returning a validated route dictionary
async def route_query(query):
    today = datetime.now(timezone.utc).date()
    cache_key = build_cache_key(query, today)

    if cache_key in _cache:
        _cache.move_to_end(cache_key)
        logger.debug("Routing %r from cache; no Mistral call made.", query)
        return _cache[cache_key]

    parsed = await request_route(query, today)
    result = validate_route(parsed, today, query)

    # Only cache decisions the model actually made
    if parsed is not None:
        _cache[cache_key] = result
        _cache.move_to_end(cache_key)
        if len(_cache) > CACHE_SIZE:
            _cache.popitem(last=False)

    return result

# Parse the model's reply, either JSON or markdown
def extract_json(text):
    if not isinstance(text, str):
        raise TypeError(f"expected a string reply, got {type(text).__name__}")

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Fall back to the outermost {...} in the reply.
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise json.JSONDecodeError("no JSON object in reply", text, 0)

    return json.loads(match.group(0))


def build_response_format():
    from mistralai.client.models import JSONSchema, ResponseFormat

    return ResponseFormat(
        type="json_schema",
        json_schema=JSONSchema(
            name="cryptora_route",
            schema_definition=RESPONSE_SCHEMA,
            strict=STRICT_SCHEMA,
        ),
    )


async def request_route(query, today):
    client = get_client()
    if client is None:
        return None

    messages = [
        {"role": "system", "content": build_system_prompt(today)},
        {"role": "user", "content": query},
    ]

    started = time.monotonic()

    try:
        response = await asyncio.wait_for(
            client.chat.complete_async(
                model=MODEL,
                messages=messages,
                response_format=build_response_format(),
                temperature=0,
                max_tokens=256,
            ),
            timeout=REQUEST_TIMEOUT,
        )
        parsed = extract_json(response.choices[0].message.content)
        return parsed
    except asyncio.TimeoutError:
        logger.warning("Mistral routing timed out after %ss for query", REQUEST_TIMEOUT)
        return None
    except (json.JSONDecodeError, TypeError, ValueError, AttributeError, IndexError) as exc:
        logger.warning("Mistral returned an unreadable routing response: %s", exc)
        return None
    except Exception as exc:
        # Rate limiting is called out separately because it is the failure most likely to show up
        # in production and the least obvious from a generic error.
        if getattr(exc, "status_code", None) == 429 or "429" in str(exc):
            logger.warning("Mistral rate limit reached")
        else:
            logger.warning("Mistral routing failed")
        return None


# Words that state a quantity without using a digit, so that "half a bitcoin in dollars" is still
# recognised as a conversion. "a" and "an" are included because "what is a bitcoin worth" means one.
NUMBER_WORDS = frozenset(
    "a an one two three four five six seven eight nine ten half quarter third dozen couple".split()
)


def states_a_quantity(query):
    """Return True if the query actually names an amount to convert."""
    if any(character.isdigit() for character in query):
        return True

    return bool(set(re.findall(r"[a-z]+", query.lower())) & NUMBER_WORDS)


# Re-check everything the model produced before any of it reaches the rest of the bot
def validate_route(parsed, today, query=""):
    if not isinstance(parsed, dict):
        return UNKNOWN

    route = parsed.get("route")
    if route not in ROUTES or route == "unknown":
        return UNKNOWN

    if route in ("stats", "news"):
        return {"route": route}

    if route == "top":
        limit = parsed.get("limit")
        if not isinstance(limit, int) or isinstance(limit, bool) or limit < 1:
            limit = DEFAULT_TOP_LIST_SIZE
        return {"route": "top", "limit": min(limit, MAX_TOP_LIST_SIZE)}

    raw_coins = parsed.get("coins")
    if not isinstance(raw_coins, list):
        return UNKNOWN

    coins = []
    seen = set()
    for entry in raw_coins:
        if not isinstance(entry, str):
            continue
        entry = entry.strip()
        if entry.lower() in seen or not is_known_coin(entry):
            continue
        seen.add(entry.lower())
        coins.append(entry)

    if not coins:
        return UNKNOWN

    if route == "multicurrency":
        # A "comparison" that survived validation with one coin is really a single coin lookup.
        if len(coins) == 1:
            return {"route": "coin", "coins": coins}
        return {"route": "multicurrency", "coins": coins[:MAX_MULTICURRENCY_COINS]}

    if route == "coin":
        return {"route": "coin", "coins": coins[:1]}

    if route in ("crypto_to_usd", "usd_to_crypto"):
        amount = parsed.get("amount")
        if not isinstance(amount, (int, float)) or isinstance(amount, bool) or amount <= 0:
            return UNKNOWN

        if query and not states_a_quantity(query):
            return {"route": "coin", "coins": coins[:1]}

        return {"route": route, "coins": coins[:1], "amount": float(amount)}

    if route == "historical":
        raw_date = parsed.get("date")
        if not isinstance(raw_date, str):
            return UNKNOWN
        try:
            parsed_date = datetime.strptime(raw_date.strip(), "%Y-%m-%d").date()
        except ValueError:
            return UNKNOWN
        # Only completed days have historical open/high/low/close data.
        if parsed_date >= today:
            return UNKNOWN
        return {"route": "historical", "coins": coins[:1], "date": parsed_date}

    return UNKNOWN


def format_amount(amount):
    """Render an amount for the calculator, which re-parses it out of a query string."""
    formatted = f"{amount:.8f}".rstrip("0").rstrip(".")
    return formatted or "0"


def dispatch(parsed):
    route = parsed["route"]
    coins = parsed.get("coins", [])

    if route in DISABLED_ROUTES:
        return []

    if route == "stats":
        return get_stats_list()

    if route == "news":
        return get_news_list()

    if route == "top":
        return get_top_cryptocurrencies(parsed["limit"])

    if route == "coin":
        return get_coin_info(coins[0])

    if route == "multicurrency":
        return generate_multi_currency_list(",".join(coins))

    if route == "crypto_to_usd":
        return crypto_calculator(f"{format_amount(parsed['amount'])} {coins[0]}", False)

    if route == "usd_to_crypto":
        return crypto_calculator(f"${format_amount(parsed['amount'])} {coins[0]}", True)

    if route == "historical":
        day = parsed["date"]
        return generate_historical_pricing_list(
            f"{coins[0]} {day.month:02d}/{day.day:02d}/{day.year}"
        )

    return []


# Describe the model's interpretation in the user's own terms, for display above the results
def describe_route(parsed):
    route = parsed["route"]
    coins = parsed.get("coins", [])

    if route == "stats":
        return "overall cryptocurrency market statistics"

    if route == "news":
        return "the latest cryptocurrency news"

    if route == "top":
        return f"the top {parsed['limit']} cryptocurrencies"

    if route == "coin":
        return f"information about {coins[0]}"

    if route == "multicurrency":
        return f"prices for {', '.join(coins)}"

    if route == "crypto_to_usd":
        return f"{format_amount(parsed['amount'])} {coins[0]} converted to U.S. dollars"

    if route == "usd_to_crypto":
        return f"${format_amount(parsed['amount'])} converted to {coins[0]}"

    if route == "historical":
        return f"the price of {coins[0]} on {parsed['date'].strftime('%B %d, %Y')}"

    return ""


def add_interpretation(results, parsed):
    description = describe_route(parsed)
    if not results or not description:
        return results

    interpretation = InlineQueryResultArticle(
        id=str(uuid4()),
        title=f"Interpreted as: {description}",
        description="Tap to send.",
        thumbnail_url="https://i.ibb.co/7JSfhJHX/Screenshot-2026-08-21-at-8-58-28-PM.png",
        input_message_content=results[0].input_message_content,
    )

    return [interpretation] + list(results)

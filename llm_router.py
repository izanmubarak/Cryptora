# Cryptora - Public Repository
"""Natural language routing for queries that Cryptora's deterministic parser does not recognize.

Most queries are handled without an LLM: a leading digit means the calculator, a leading dollar
sign means the reverse calculator, and a bare cryptocurrency name or symbol means a coin lookup.
When a query matches none of those, this module asks a small Mistral model to classify it into one
of the bot's existing features and extract the arguments that feature needs.

The model never talks to the user and never produces prices. It only picks a route and pulls out
arguments, all of which are re-validated here before anything is dispatched.
"""

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

# Ministral 3B. Consider pinning this to a dated release once you have confirmed which ones your
# account can reach, so that a new Ministral release cannot silently change how queries are routed.
MODEL = "ministral-3b-latest"

# Mistral accepts a JSON schema either as a hard constraint (strict) or as guidance. This is left
# off deliberately: strict mode requires every property to appear in "required" and forbids
# additional properties, which would mean asking the model to emit placeholder values for the
# arguments a route does not use. Turn it on only alongside a schema reshaped to match.
STRICT_SCHEMA = False

# The model is only picking one of nine labels out of a short query, so it typically answers in
# well under a second. This is a ceiling for the occasional slow call, not an expected wait; the
# user is already waiting out the typing debounce plus the CoinMarketCap request that follows.
REQUEST_TIMEOUT = 4.0

# Cryptora caps "top X" lists at 49 entries, matching the limit enforced in app.py.
MAX_TOP_LIST_SIZE = 49
DEFAULT_TOP_LIST_SIZE = 40

# Multi-currency queries display at most ten coins, matching the limit in multicurrency.py.
MAX_MULTICURRENCY_COINS = 10

# Telegram sends an inline query on every keystroke, so the same text is classified repeatedly as
# users retype and correct themselves. Cache decisions, keyed by date so that queries containing
# relative dates ("yesterday") do not survive past midnight.
CACHE_SIZE = 512
_cache = OrderedDict()

# Requests per minute your Mistral plan allows across the whole bot. This figure is only quoted in
# the call log, so that the observed rate is readable against the ceiling without having to
# remember it -- nothing enforces it. Set it to whatever your account actually permits.
RATE_LIMIT_RPM = 60

# Every request that actually reaches Mistral is counted here, so the log shows how often the
# router falls through to the model rather than answering from the cache or deterministic parser.
_calls_total = 0
_call_times = deque()


def record_call():
    """Count a call to Mistral, returning (calls in the last minute, calls since startup)."""
    global _calls_total

    now = time.monotonic()
    _calls_total += 1
    _call_times.append(now)

    while _call_times and now - _call_times[0] >= 60.0:
        _call_times.popleft()

    return len(_call_times), _calls_total

# Route names are deliberately self-describing. They were once "calculator" and
# "reverse_calculator", which forced the model to memorise which direction "reverse" meant while
# "amount" silently changed unit between them, and small models guessed wrong about half the time.
# Naming the direction in the label removes the convention it has to remember.
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

RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "route": {"type": "string", "enum": list(ROUTES)},
        "coins": {"type": "array", "items": {"type": "string"}},
        "amount": {"type": "number"},
        "date": {"type": "string"},
        "limit": {"type": "integer"},
    },
    # "coins" is required because when it is optional the model intermittently omits it on
    # otherwise correct answers -- and a route naming no cryptocurrency is unusable here.
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
Always include "coins" ([] if none). Never invent a coin. Dates must be past, YYYY-MM-DD.

"half a bitcoin in dollars" {{"route":"crypto_to_usd","coins":["bitcoin"],"amount":0.5}}
"what do I get for 500 bucks of eth" {{"route":"usd_to_crypto","coins":["ETH"],"amount":500}}
"bitcoin price yesterday" {{"route":"historical","coins":["bitcoin"],"date":"{yesterday}"}}
"20 biggest coins" {{"route":"top","coins":[],"limit":20}}
"how is the market doing" {{"route":"stats","coins":[]}}
"anything happening in crypto" {{"route":"news","coins":[]}}
"compare bitcoin and solana" {{"route":"multicurrency","coins":["bitcoin","solana"]}}
"tell me about dogecoin" {{"route":"coin","coins":["dogecoin"]}}
"hey there" {{"route":"unknown","coins":[]}}"""


def get_client():
    """Return a cached Mistral client, or None if no API token is configured."""
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
            # The 2.x SDK moved the client out of the top level package, which is now a namespace.
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


async def route_query(query):
    """Classify a natural language query, returning a validated route dictionary.

    Always returns a dictionary with a "route" key. Every failure mode -- no token, a timeout, a
    malformed response, a hallucinated cryptocurrency -- collapses to the "unknown" route, which
    leaves the caller showing the same "not found" message the bot showed before this feature.
    """
    today = datetime.now(timezone.utc).date()
    cache_key = build_cache_key(query, today)

    if cache_key in _cache:
        _cache.move_to_end(cache_key)
        # Deliberately not logged at INFO: a cache hit costs no request, so counting it alongside
        # real calls would misrepresent how often the bot actually reaches Mistral.
        logger.debug("Routing %r from cache; no Mistral call made.", query)
        return _cache[cache_key]

    parsed = await request_route(query, today)
    result = validate_route(parsed, today)

    # Only cache decisions the model actually made. A timeout or a transport error also produces
    # "unknown", and caching that would pin the query to a failure for the rest of the day instead
    # of letting the user's next keystroke retry it.
    if parsed is not None:
        _cache[cache_key] = result
        _cache.move_to_end(cache_key)
        if len(_cache) > CACHE_SIZE:
            _cache.popitem(last=False)

    return result


def extract_json(text):
    """Parse the model's reply, tolerating JSON wrapped in prose or a markdown code fence.

    Small models do this even when asked for JSON, and the schema is guidance rather than a hard
    constraint unless STRICT_SCHEMA is on, so the reply is not guaranteed to be bare JSON.
    """
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
    """Describe the expected JSON shape to Mistral."""
    from mistralai.client.models import JSONSchema, ResponseFormat

    return ResponseFormat(
        type="json_schema",
        json_schema=JSONSchema(
            name="cryptora_route",
            # Serialises to "schema"; the SDK renames it to avoid clashing with pydantic.
            schema_definition=RESPONSE_SCHEMA,
            strict=STRICT_SCHEMA,
        ),
    )


async def request_route(query, today):
    """Ask Mistral to classify the query. Returns the raw parsed JSON, or None on any failure."""
    client = get_client()
    if client is None:
        return None

    messages = [
        {"role": "system", "content": build_system_prompt(today)},
        {"role": "user", "content": query},
    ]

    recent, total = record_call()
    logger.info(
        "Mistral call #%d for %r (%d in the last 60s, plan allows %d)",
        total,
        query,
        recent,
        RATE_LIMIT_RPM,
    )
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
        logger.info(
            "Mistral call #%d answered in %.2fs: route=%s",
            total,
            time.monotonic() - started,
            parsed.get("route") if isinstance(parsed, dict) else "malformed",
        )
        return parsed
    except asyncio.TimeoutError:
        logger.warning("Mistral routing timed out after %ss for query: %s", REQUEST_TIMEOUT, query)
        return None
    except (json.JSONDecodeError, TypeError, ValueError, AttributeError, IndexError) as exc:
        logger.warning("Mistral returned an unreadable routing response for %r: %s", query, exc)
        return None
    except Exception as exc:
        # Rate limiting is called out separately because it is the failure most likely to show up
        # in production and the least obvious from a generic error.
        if getattr(exc, "status_code", None) == 429 or "429" in str(exc):
            logger.warning(
                "Mistral rate limit reached; natural language routing is degraded until it clears. "
                "Query was %r.",
                query,
            )
        else:
            logger.warning("Mistral routing failed for %r: %s", query, exc)
        return None


def validate_route(parsed, today):
    """Re-check everything the model produced before any of it reaches the rest of the bot.

    Language models will confidently name cryptocurrencies that do not exist, so every coin is
    verified against the CoinMarketCap map, and every route that cannot be satisfied with the
    arguments actually present is downgraded to "unknown".
    """
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

    # Every remaining route needs at least one real cryptocurrency.
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
    """Run the route the model chose, reusing the same functions the deterministic parser calls."""
    route = parsed["route"]
    coins = parsed.get("coins", [])

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
        # generate_historical_pricing_list re-parses the date out of the query string, and only
        # takes the "last word is the date" path when that word contains a slash or a period.
        day = parsed["date"]
        return generate_historical_pricing_list(
            f"{coins[0]} {day.month:02d}/{day.day:02d}/{day.year}"
        )

    return []


def describe_route(parsed):
    """Describe the model's interpretation in the user's own terms, for display above the results."""
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
    """Prepend a result that spells out how the query was understood.

    Natural language routing is invisible otherwise, and a user who gets the wrong feature has no
    way to tell why. Tapping this entry sends the same message the first real result would, so it
    never costs the user a step.
    """
    description = describe_route(parsed)
    if not results or not description:
        return results

    interpretation = InlineQueryResultArticle(
        id=str(uuid4()),
        title=f"Interpreted as: {description}",
        description="Tap to send.",
        thumbnail_url=results[0].thumbnail_url,
        input_message_content=results[0].input_message_content,
    )

    return [interpretation] + list(results)

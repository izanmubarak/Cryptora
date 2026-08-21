# Cryptora - Public Repository
import re
import asyncio
import logging
import sys
import time
from telegram import InlineQueryResultArticle, InlineQueryResultsButton, InputTextMessageContent, Update
from telegram.ext import Application, InlineQueryHandler, ContextTypes
from retrieve_tokens import get_token
from coin import get_coin_info, is_known_coin
from top import get_top_cryptocurrencies
from calculator import crypto_calculator
from multicurrency import generate_multi_currency_list
from stats import get_stats_list
from historical import determine_if_date_in_string, generate_historical_pricing_list
from help_messages import get_help_messages
from news import get_news_list
import llm_router

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

# Telegram sends an inline query on every keystroke, so a typed-out sentence arrives as dozens of
# separate updates. Natural language routing costs an API call, so it only runs once the user has
# stopped typing. Each update records itself here, waits, and gives up if a newer keystroke landed.
#
# This value behaves as a cliff rather than a dial, so do not lower it to shave latency. A keystroke
# only survives if nothing else arrives within the delay, so a delay above the user's typing gap
# costs one request per query and a delay below it costs one request per character.
#
# What decides the cost in practice is not average typing speed but how long people stop to think
# mid-query. Mean requests for one 32 character query:
#
#     pause behaviour              1.0s   1.5s   2.0s   2.5s   3.0s
#     no hesitation                 1.0    1.0    1.0    1.0    1.0
#     occasional 1.0-1.5s pauses    7.2    4.7    1.0    1.0    1.0
#     occasional 1.5-2.5s pauses    7.2    7.2    6.0    2.9    1.0
#     frequent 2.0-4.0s pauses     10.3   10.3   10.3    9.4    7.0
#
# 2.0 seconds covers ordinary hesitation. Going higher buys little against long pauses while adding
# latency to every query, so the unbounded tail is the per-user cap's job, not this value's.
DEBOUNCE_DELAY = 2.0
_latest_query = {}


# Mistral rate limits requests per minute across every user of the bot at once, so one person
# typing slowly enough to defeat the debounce could exhaust the allowance by themselves. This caps
# what any single user can spend, leaving the rest available to everyone else.
MAX_ROUTER_CALLS_PER_USER = 4
ROUTER_CALL_WINDOW = 60.0
_recent_router_calls = {}


def claim_router_budget(user_id):
    """Record a routing request for this user, returning False if they are over their allowance."""
    now = time.monotonic()

    # Users who have not asked anything in a while are dropped entirely, so this cannot grow
    # without bound on a busy bot.
    if len(_recent_router_calls) > 1000:
        for uid in [u for u, ts in _recent_router_calls.items() if now - max(ts) >= ROUTER_CALL_WINDOW]:
            del _recent_router_calls[uid]

    timestamps = [t for t in _recent_router_calls.get(user_id, []) if now - t < ROUTER_CALL_WINDOW]
    _recent_router_calls[user_id] = timestamps

    # if len(timestamps) >= MAX_ROUTER_CALLS_PER_USER:
    #     return False

    timestamps.append(now)
    return True


async def wait_for_typing_to_settle(user_id, query):
    """Return True if no newer inline query arrived from this user while we waited."""
    _latest_query[user_id] = query
    await asyncio.sleep(DEBOUNCE_DELAY)

    if _latest_query.get(user_id) != query:
        return False

    # This query won, so the user has stopped typing and nothing needs to be remembered for them.
    del _latest_query[user_id]
    return True


async def route_with_language_model(update, query):
    """Interpret a query the parser above could not handle.

    Returns the results to display, or None when the query has already been dealt with and the
    caller should simply return -- either because the user is still typing, or because nothing
    could be made of the query and the "not found" button has been sent.
    """
    user_id = update.inline_query.from_user.id

    if not await wait_for_typing_to_settle(user_id, query):
        # The user kept typing, so a later update is already handling their query.
        return None

    # A cached decision costs no API call, so it should not spend the user's allowance.
    if not llm_router.is_cached(query) and not claim_router_budget(user_id):
        logger.info("User %s is over their routing allowance; skipping Mistral.", user_id)
        await update.inline_query.answer(
            results=[],
            button=InlineQueryResultsButton(
                text="Too many questions at once. Please wait a moment and try again.",
                start_parameter="do_something",
            ),
        )
        return None

    parsed = await llm_router.route_query(query)
    results = llm_router.dispatch(parsed) if parsed["route"] != "unknown" else []

    print(results)

    if not results:
        await update.inline_query.answer(
            results=[],
            button=InlineQueryResultsButton(
                text="Requested currency not found. Please try again.",
                start_parameter="do_something",
            ),
        )
        return None

    return llm_router.add_interpretation(results, parsed)


async def inlinequery(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Initialize the query
    query = update.inline_query.query
    results = []

    if not query:
        results = get_help_messages()
    else:
        # Crypto calculator
        if query[0].isdigit() and query != "0x":
            results = crypto_calculator(query, False)
            if not results:
                await update.inline_query.answer(
                    results=[],
                    button=InlineQueryResultsButton(
                        text="Failed to convert cryptocurrency. Please try again.",
                        start_parameter="do_something",
                    ),
                )
                return

        # Reverse crypto calculator
        elif query[0] == "$":
            results = crypto_calculator(query, True)
            if not results:
                await update.inline_query.answer(
                    results=[],
                    button=InlineQueryResultsButton(
                        text="Failed to convert cryptocurrency. Please try again.",
                        start_parameter="do_something",
                    ),
                )
                return

        # Get global information
        elif query.lower() in ("global", "stats"):
            results = get_stats_list()

        # Get the news
        elif query.lower() == "news":
            results = get_news_list()

        # Top X. Only "top" and "top <number>" are handled here; any other phrasing that mentions
        # a top list is left for the language model further down.
        elif re.fullmatch(r"top(\s+[1-9]\d*)?", query.strip(), re.IGNORECASE):
            split_query = query.split()

            if len(split_query) == 1:
                list_size = 40
            else:
                list_size = int(split_query[1])
                if list_size > 49:
                    await update.inline_query.answer(
                        results=[],
                        button=InlineQueryResultsButton(
                            text="Requested list too large. Please try again.",
                            start_parameter="do_something",
                        ),
                    )
                    return

            results = get_top_cryptocurrencies(list_size)

        # Historical pricing
        elif determine_if_date_in_string(query):
            try:
                results = generate_historical_pricing_list(query)
            except Exception as exc:
                # Datefinder matches loosely, so plain English queries land here without actually
                # naming a coin and a date in the shape this branch expects.
                logger.info("Historical parsing failed for %r (%s). Falling back to the router.", query, exc)
                results = await route_with_language_model(update, query)
                if results is None:
                    return

        # Cryptocurrency information
        else:
            if "," in query:
                results = generate_multi_currency_list(query)

            # A query that is exactly a cryptocurrency's name or symbol is a plain coin lookup.
            # This check reads an in-memory set, so it costs nothing and keeps the common case
            # away from the language model.
            elif is_known_coin(query):
                results = get_coin_info(query)

            # Anything left is not something the parser above understands, so fall back to
            # interpreting it as natural language.
            else:
                results = await route_with_language_model(update, query)
                if results is None:
                    return

    await update.inline_query.answer(results=results, cache_time=1)


async def error(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    # Updates must be processed concurrently for the typing debounce to work. Without this,
    # python-telegram-bot handles one update at a time, so an update waiting out the debounce
    # would block the very keystrokes it is waiting to detect.
    application = Application.builder().token(get_token(False)).concurrent_updates(True).build()
    application.add_handler(InlineQueryHandler(inlinequery))
    application.add_error_handler(error)
    application.run_polling()


if __name__ == "__main__":
    main()

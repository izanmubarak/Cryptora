import re
import asyncio
from telegram import InlineQueryResultsButton, Update
from telegram.ext import Application, InlineQueryHandler, ContextTypes
from retrieve_tokens import get_token
from calculator import parse_amount
from coin import is_known_coin
from multicurrency import looks_like_coin_list
from help_messages import get_help_messages
import llm_router

DEBOUNCE_DELAY = 1.0
NOT_FOUND_MESSAGE = "Requested currency not found. Please try again."
EMPTY_RESULT_MESSAGES = {
    "historical": "No historical data found for that date.",
}
_latest_query = {}

async def wait_for_typing_to_settle(user_id, query):
    """Return True if no newer inline query arrived from this user while we waited."""
    _latest_query[user_id] = query
    await asyncio.sleep(DEBOUNCE_DELAY)

    if _latest_query.get(user_id) != query:
        return False

    del _latest_query[user_id]
    return True

async def answer_with_message(update, text):
    await update.inline_query.answer(
        results=[],
        button=InlineQueryResultsButton(text=text, start_parameter="do_something"),
    )

def parse_conversion(query, route):
    split_query = query.split(" ")

    amount = parse_amount(split_query[0])
    currency = " ".join(split_query[1:]).strip()

    if amount is None or not is_known_coin(currency):
        return None

    return {"route": route, "coins": [currency], "amount": amount}


# Classic Cryptora commands
def parse_deterministically(query):
    query = query.strip()
    if not query:
        return None

    if query[0].isdigit() and query != "0x":
        return parse_conversion(query, "crypto_to_usd")

    if query[0] == "$":
        return parse_conversion(query, "usd_to_crypto")

    if query.lower() in ("global", "stats"):
        return {"route": "stats"}

    if query.lower() == "news":
        return {"route": "news"}

    # Top X functionality
    if re.fullmatch(r"top(\s+[1-9]\d*)?", query, re.IGNORECASE):
        split_query = query.split()

        if len(split_query) == 1:
            return {"route": "top", "limit": 40}

        list_size = int(split_query[1])
        if list_size > 49:
            return {"error": "Requested list too large. Please try again."}

        return {"route": "top", "limit": list_size}

    # Multicurrency support
    if looks_like_coin_list(query):
        return {"route": "multicurrency", "coins": [p.strip() for p in query.split(",") if p.strip()]}

    if is_known_coin(query):
        return {"route": "coin", "coins": [query]}

    return None


async def route_with_language_model(update, query):
    user_id = update.inline_query.from_user.id
    if not await wait_for_typing_to_settle(user_id, query):
        return None
    return await llm_router.route_query(query)


async def inlinequery(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query

    if not query:
        await update.inline_query.answer(results=get_help_messages(), cache_time=1)
        return

    # Try classic commands first to avoid unnecessary LLM calls
    parsed = parse_deterministically(query)
    from_model = False

    if parsed is None:
        parsed = await route_with_language_model(update, query)
        if parsed is None:
            # user is still typing
            return
        from_model = True

    if "error" in parsed:
        await answer_with_message(update, parsed["error"])
        return

    unavailable = llm_router.DISABLED_ROUTES.get(parsed["route"])
    if unavailable:
        await answer_with_message(update, unavailable)
        return

    results = llm_router.dispatch(parsed)
    if not results:
        await answer_with_message(
            update, EMPTY_RESULT_MESSAGES.get(parsed["route"], NOT_FOUND_MESSAGE)
        )
        return

    if from_model:
        results = llm_router.add_interpretation(results, parsed)

    await update.inline_query.answer(results=results, cache_time=1)

def main():
    application = Application.builder().token(get_token("bot")).concurrent_updates(True).build()
    application.add_handler(InlineQueryHandler(inlinequery))
    application.run_polling()

if __name__ == "__main__":
    main()

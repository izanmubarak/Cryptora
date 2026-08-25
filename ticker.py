import logging
from datetime import datetime, timezone
from uuid import uuid4

import requests
from telegram import InlineQueryResultArticle, InputTextMessageContent, Update
from telegram.constants import ChatMemberStatus, ChatType
from telegram.error import BadRequest, Forbidden
from telegram.ext import ContextTypes

from coin import Coin, format_monetary_value, is_known_coin, resolve_coin_ids

logger = logging.getLogger(__name__)

DEFAULT_COINS = ["BTC", "ETH"]
TICKER_JOB_PREFIX = "ticker_"
TICKER_INTERVAL_SECONDS = 60
INVISIBLE_SPACE = "\u200b"

KEYLESS_BASE = "https://pro-api.coinmarketcap.com/public-api"


def generate_ticker_list(coins):
    resolved = resolve_coin_ids(coins if coins else DEFAULT_COINS)
    symbols = [sym for sym, _ in resolved] if resolved else coins

    if len(symbols) == 1:
        message = symbols[0]
    elif len(symbols) == 2:
        message = f"{symbols[0]} and {symbols[1]}"
    else:
        message = ", ".join(symbols[:-1]) + ", and " + symbols[-1]

    return [
        InlineQueryResultArticle(
            id=uuid4(),
            title="Start live ticker",
            description=f"Tap to start a live ticker for {message} in this chat.\n"
            "Cryptora will update the message every minute.",
            thumbnail_url="https://i.ibb.co/n8Kjr6PG/Ticker.png",
            input_message_content=InputTextMessageContent(f"/ticker {' '.join(symbols)}"),
        )
    ]


def fetch_ticker_prices(queries):
    """Batch-fetch latest prices from the CoinMarketCap keyless public API.

    Accepts coin symbols or names (e.g. ["BTC", "ethereum", "Solana"]).
    Uses CMC's keyless API to prevent burning through personal API key limits.
    Returns a list of Coin objects preserving the requested order.
    """
    resolved = resolve_coin_ids(queries)
    if not resolved:
        return []

    id_string = ",".join(str(cid) for _, cid in resolved)
    response = requests.get(
        f"{KEYLESS_BASE}/v3/cryptocurrency/quotes/latest?id={id_string}&convert=USD",
        timeout=10,
    )
    raw_data = response.json().get("data", [])
    data_by_id = {item["id"]: item for item in raw_data}

    coins = []
    for _, cmc_id in resolved:
        coin_data = data_by_id.get(cmc_id)
        if coin_data:
            coin = Coin(coin_data)
            if coin.exists:
                coins.append(coin)

    return coins


def format_ticker_message(coins):
    """Format a list of Coin objects into a clean ticker message."""
    now = datetime.now(timezone.utc).strftime("%b %d, %Y %H:%M UTC")
    lines = []
    for coin in coins:
        price_str = f"${format_monetary_value(coin.price_usd)}"
        lines.append(f"***{coin.symbol}*** {price_str} ({coin.percent_change}%) {INVISIBLE_SPACE}")

    lines.append(f"\n_Last updated: {now}_")
    return "\n".join(lines)


def _job_name(chat_id):
    return f"{TICKER_JOB_PREFIX}{chat_id}"


def parse_ticker_args(args):
    if not args:
        return DEFAULT_COINS

    if isinstance(args, (list, tuple)):
        raw = " ".join(args).strip()
    else:
        raw = str(args).strip()

    if not raw:
        return DEFAULT_COINS

    if "," in raw:
        return [p.strip() for p in raw.split(",") if p.strip()]
    return [p.strip() for p in raw.split() if p.strip()]


def parse_ticker_query(raw_text):
    """Parse a potential deterministic ticker command.

    Returns a list of coin queries if strictly valid and non-conversational,
    or None if it should fall through to the LLM.
    """
    query = raw_text.strip()
    if query.lower() == "ticker":
        return DEFAULT_COINS

    if not query.lower().startswith("ticker "):
        return None

    coins_part = query[7:].strip()
    if not coins_part:
        return DEFAULT_COINS

    # If it starts with "for " or contains natural language connectors, leave it to the LLM
    lowered = coins_part.lower()
    if lowered.startswith("for ") or " and " in lowered or " with " in lowered:
        return None

    coins = parse_ticker_args(coins_part)
    if coins and all(is_known_coin(c) for c in coins):
        return coins

    return None


async def _stop_existing_ticker(chat_id, context):
    """Stop any existing ticker in the chat, cleaning up jobs and unpinning."""
    jobs = context.job_queue.get_jobs_by_name(_job_name(chat_id))
    for job in jobs:
        job.schedule_removal()

    msg_id = context.chat_data.get("ticker_message_id")
    if msg_id and context.chat_data.get("ticker_pinned"):
        try:
            await context.bot.unpin_chat_message(chat_id=chat_id, message_id=msg_id)
        except (BadRequest, Forbidden):
            pass

    context.chat_data.pop("ticker_message_id", None)
    context.chat_data.pop("ticker_symbols", None)
    context.chat_data.pop("ticker_pinned", None)


async def _is_user_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    chat = update.effective_chat
    user = update.effective_user
    sender_chat = update.message.sender_chat if update.message else None

    if not chat:
        return False

    if chat.type == ChatType.PRIVATE:
        return True

    # Anonymous group admins post on behalf of the group/channel
    if sender_chat and sender_chat.id == chat.id:
        return True

    if not user:
        return False

    try:
        member = await context.bot.get_chat_member(chat_id=chat.id, user_id=user.id)
        return member.status in (
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.OWNER,
            "administrator",
            "creator",
        )
    except (BadRequest, Forbidden):
        return False


async def start_ticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await _is_user_admin(update, context):
        await update.message.reply_text("Only group administrators can start the live ticker.")
        return

    chat_id = update.effective_chat.id
    existing_jobs = context.job_queue.get_jobs_by_name(_job_name(chat_id))
    if existing_jobs:
        await _stop_existing_ticker(chat_id, context)

    # Parse optional coin arguments: /ticker btc, ltc, eth, solana or /ticker btc eth
    queries = parse_ticker_args(context.args)

    invalid = [q for q in queries if not is_known_coin(q)]
    if invalid:
        await update.message.reply_text(
            f"Unknown coin(s): {', '.join(invalid)}\n"
            "Use symbols (BTC, ETH) or full names (Bitcoin, Ethereum)."
        )
        return

    try:
        coins = fetch_ticker_prices(queries)
    except Exception:
        await update.message.reply_text("Failed to fetch prices. Please try again later.")
        return

    if not coins:
        await update.message.reply_text("Could not resolve any coins. Please try again.")
        return

    text = format_ticker_message(coins)
    msg = await update.message.reply_text(text, parse_mode="Markdown")
    context.chat_data["ticker_message_id"] = msg.message_id
    context.chat_data["ticker_symbols"] = [coin.symbol for coin in coins]

    context.job_queue.run_repeating(
        callback=update_ticker,
        interval=TICKER_INTERVAL_SECONDS,
        first=TICKER_INTERVAL_SECONDS,
        chat_id=chat_id,
        name=_job_name(chat_id),
    )


async def stop_ticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /stopticker command. Stops the live ticker and optionally unpins."""
    if not await _is_user_admin(update, context):
        await update.message.reply_text("Only group administrators can stop the live ticker.")
        return

    chat_id = update.effective_chat.id

    jobs = context.job_queue.get_jobs_by_name(_job_name(chat_id))
    if not jobs:
        await update.message.reply_text("No ticker is currently running in this chat.")
        return

    await _stop_existing_ticker(chat_id, context)

    await update.message.reply_text("Ticker stopped.")


async def update_ticker(context: ContextTypes.DEFAULT_TYPE):
    """Job callback: fetch fresh prices and edit the pinned ticker message."""
    chat_id = context.job.chat_id
    chat_data = context.application.chat_data.get(chat_id, {})

    msg_id = chat_data.get("ticker_message_id")
    symbols = chat_data.get("ticker_symbols")

    if not msg_id or not symbols:
        context.job.schedule_removal()
        return

    try:
        coins = fetch_ticker_prices(symbols)
    except Exception:
        logger.exception("Failed to fetch ticker prices for chat %s", chat_id)
        return

    if not coins:
        return

    text = format_ticker_message(coins)

    try:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=msg_id,
            text=text,
            parse_mode="Markdown",
        )
    except BadRequest as e:
        if "message is not modified" in str(e).lower():
            pass
        elif "message to edit not found" in str(e).lower():
            context.job.schedule_removal()
            chat_data.pop("ticker_message_id", None)
            chat_data.pop("ticker_symbols", None)
            chat_data.pop("ticker_pinned", None)
        else:
            logger.exception("Failed to edit ticker message in chat %s", chat_id)
    except Forbidden:
        # Bot was removed from the chat
        context.job.schedule_removal()

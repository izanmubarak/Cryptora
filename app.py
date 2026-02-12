# Cryptora - Public Repository
import re
import logging
import sys
from telegram import InlineQueryResultArticle, InputTextMessageContent, Update
from telegram.ext import Application, InlineQueryHandler, ContextTypes
from retrieve_tokens import get_token
from coin import get_coin_info
from top import get_top_cryptocurrencies
from calculator import crypto_calculator
from multicurrency import generate_multi_currency_list
from stats import get_stats_list
from historical import determine_if_date_in_string, generate_historical_pricing_list
from help_messages import get_help_messages
from news import get_news_list

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


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
                    switch_pm_text="Failed to convert cryptocurrency. Please try again.",
                    switch_pm_parameter="do_something",
                )
                return

        # Reverse crypto calculator
        elif query[0] == "$":
            results = crypto_calculator(query, True)
            if not results:
                await update.inline_query.answer(
                    results=[],
                    switch_pm_text="Failed to convert cryptocurrency. Please try again.",
                    switch_pm_parameter="do_something",
                )
                return

        # Get global information
        elif query.lower() in ("global", "stats"):
            results = get_stats_list()

        # Get the news
        elif query.lower() == "news":
            results = get_news_list()

        # Top X
        elif "top" in query:
            if query.lower() == "top":
                list_size = 40
            else:
                list_size = int(query.split(" ")[1])
                if list_size > 49:
                    await update.inline_query.answer(
                        results=[],
                        switch_pm_text="Requested list too large. Please try again.",
                        switch_pm_parameter="do_something",
                    )
                    return

            results = get_top_cryptocurrencies(list_size)

        # Historical pricing
        elif determine_if_date_in_string(query):
            results = generate_historical_pricing_list(query)

        # Cryptocurrency information
        else:
            if "," in query:
                results = generate_multi_currency_list(query)
            else:
                results = get_coin_info(query)
                if not results:
                    await update.inline_query.answer(
                        results=[],
                        switch_pm_text="Requested currency not found. Please try again.",
                        switch_pm_parameter="do_something",
                    )
                    return

    await update.inline_query.answer(results=results, cache_time=1)


async def error(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(get_token(False)).build()

    application.add_handler(InlineQueryHandler(inlinequery))

    # log all errors
    application.add_error_handler(error)

    # Start the Bot
    application.run_polling()


if __name__ == "__main__":
    main()

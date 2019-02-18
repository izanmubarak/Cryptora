# Cryptora - Public Repository
import re
from telegram.utils.helpers import escape_markdown
from telegram import InlineQueryResultArticle, ParseMode,InputTextMessageContent
from telegram.ext import Updater, InlineQueryHandler, CommandHandler
import logging
import sys
from collections import OrderedDict
from retrieve_tokens import *
from coin import *
from top import *
from calculator import *
from coinbase_pro import *
from multicurrency import *
from stats import *
from historical import *
from help_messages import *
from news import *

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - \
 %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def inlinequery(bot, update):

	# Initialize the query
	query = update.inline_query.query
	results = []

	if not query:
		results = get_help_messages()

	else:

		# Crypto calculator
		if query[0].isdigit() and query != '0x':
			results = crypto_calculator(query, False)
			if not results:
				bot.answerInlineQuery(update.inline_query.id, results=[], \
						switch_pm_text='Failed to convert cryptocurrency. Please try again.',\
						switch_pm_parameter='do_something')

		# Reverse crypto calculator		
		elif query[0] == "$":
			results = crypto_calculator(query, True)
			if not results:
				bot.answerInlineQuery(update.inline_query.id, results=[], \
						switch_pm_text='Failed to convert cryptocurrency. Please try again.',\
						switch_pm_parameter='do_something')

		# GDAX pricing
		elif query.upper() == "GDAX" or query.lower() == "coinbase pro":
			results = get_GDAX_prices()

		# Get global information
		elif query.lower() == "global" or query.lower() == "stats":
			results = get_stats_list()

		# Get the news
		elif query.lower() == "news":
			results = get_news_list()

		# Top X
		elif "top" in query:

			if query.lower() == "top":
				listSize = 40
			else:
				listSize = (int(query.split(" ")[1]))
				if listSize > 49:
					bot.answerInlineQuery(update.inline_query.id, results=[], \
						switch_pm_text='Requested list too large. Please try again.',\
						switch_pm_parameter='do_something')

			results = get_top_cryptocurrencies(listSize)


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
					bot.answerInlineQuery(update.inline_query.id, results=[], \
						switch_pm_text='Requested currency not found. Please try again.',\
						switch_pm_parameter='do_something')

	bot.answerInlineQuery(update.inline_query.id, results=results, cache_time=1)

def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)

def main():
    # Create the Updater and pass it your bot's token.
    updater = Updater(get_token(False))

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    dp.add_handler(InlineQueryHandler(inlinequery))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Block until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()
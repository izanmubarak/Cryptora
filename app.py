# Cryptora - Public Repository
import re
from telegram.utils.helpers import escape_markdown
from telegram import InlineQueryResultArticle, ParseMode,InputTextMessageContent
from telegram.ext import Updater, InlineQueryHandler, CommandHandler
import logging
import sys
from collections import OrderedDict
from coin import *
from top import *
from calculator import *
from gdax_info import *
from multicurrency import *
from stats import *
from historical import *
from help_messages import *
from news import *

# Constant variables 
JSON_API_URL = 'https://api.coinmarketcap.com/v1/ticker/?limit=10000'
NEWS_URL = "http://coindesk.com/feed"

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - \
 %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def inlinequery(bot, update):

	# Initialize the query
	query = update.inline_query.query
	dateInString = determine_if_date_in_string(query)
	results = []

	for x in range (0, len(query)):
		if query.endswith(","):
			query = query[:-1]
		if query.startswith(","):
			query = query[1:]

	# Crypto calculator
	if query[0].isdigit() and query != '0x':
		results = generate_cryptoCalculator_result(query)

	# Reverse crypto calculator		
	elif query[0] == "$":
		results = generate_reverseCryptoCalculator_result(query)

	# Help section
	elif query.lower() == "help":
		results = get_help_messages()

	# GDAX pricing
	elif query.upper() == "GDAX":
		results = get_GDAX_prices()

	elif query.lower() == "global":
		results = get_stats_list()

	# Get the news
	elif query.lower() == "news":
		results = get_news_list()

	# Top X
	elif "top" in query:

		if query.lower() == "top":
			listSize = 51
		else:
			listSize = (int(query.split(" ")[1]) + 1)

		results = get_top_cryptocurrencies(listSize)


	# Historical pricing
	elif dateInString == True or "ago" in query or "yesterday" in query:
		results = get_historical_pricing_list(query, bot, update, dateInString)

	# Cryptocurrency information
	else:

		if "," in query:

			try:
				results = generate_multi_currency_list(query)

			except:
				bot.answerInlineQuery(update.inline_query.id, results=[], \
				switch_pm_text='Invalid currencies entered. Please try again.',switch_pm_parameter='do_something')


			
		else:
			results = get_coin_info(query)

	bot.answerInlineQuery(update.inline_query.id, results=results, cache_time=1)

def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)

def main():
    # Create the Updater and pass it your bot's token.
    updater = Updater('token')

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
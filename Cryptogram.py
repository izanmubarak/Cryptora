''' CRYPTOGRAM '''
# A Telegram bot built in Python that specializes in retrieving information 
# about your favorite cryptocurrency. Current data sourced from CoinMarketCap. Historical data sourced from Coinbase. News articles sourced from Coindesk.


''' TODO (In no particular order):

1. Implement Historical Pricing Data from Coinbase.
2. Clean up code and implement classes.
3. Implement a faster solution to retrieving news via FeedParser. 
4. Write documentation and comments.
5. Finish Top X feature.

'''

# Dependencies.
from uuid import uuid4
import re
from telegram.utils.helpers import escape_markdown
from telegram import InlineQueryResultArticle, ParseMode,InputTextMessageContent, InlineQueryResultPhoto
from telegram.ext import Updater, InlineQueryHandler, CommandHandler
import logging
import sys
import requests
from decimal import Decimal
from bs4 import BeautifulSoup
from Cryptogram_functions import *

# Constant variables. 
JSON_API_URL = 'https://api.coinmarketcap.com/v1/ticker/?limit=1315'
JSON_DATA = requests.get(JSON_API_URL).json()
NEWS_URL = "https://feeds.feedburner.com/CoinDesk"
token = '463277822:AAGhIn--7kELcYSB7MhVp-JUTkOOZtCWZUo'

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - \
 %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def inlinequery(bot, update):

	# This function handles all queries to the bot. 
	# It directs user choice by providing 7 options: 
		# CryptoCalculator (done!)
		# Price (done!)
		# Market capitalization (done!)
		# Circulating supply (done!)
		# 24hr % change (done!)
		# A summary of the cryptocurrency, which provides the aforementioned 
			# data in a single message. (done!)

	query = update.inline_query.query

	if query[0].isdigit():
		# CryptoCalculator.
		calcQuery = CryptoCalculatorInstance(query)
		results = [
			InlineQueryResultArticle(
				id=uuid4(),
				thumb_url='https://files.coinmarketcap.com/static/img/coins/200x200/' + calcQuery.id + '.png',
				title=("Convert " + calcQuery.input + " " + calcQuery.symbol + " to USD"),
				description="$" + calcQuery.price_USD,
				input_message_content=InputTextMessageContent(calcQuery.input + " " + calcQuery.symbol + " = $" + calcQuery.price_USD))
		]
	
	elif query[0] == "$":
		# Reverse CryptoCalculator.
		# Gigantic mess of spaghetti code that needs to be cleaned up.
		requestedCrypto = ""
		reverseCryptoCalculatorQuery = query.split(" ")
		splitReverseCryptoQueryLength = len(reverseCryptoCalculatorQuery)
		dollarValue = float(reverseCryptoCalculatorQuery[0][1:])
		if reverseCryptoCalculatorQuery[1] == "to":
			for x in range (2, splitReverseCryptoQueryLength):
				requestedCrypto += query.split(" ")[x] + " "
		else:
			for x in range (1, splitReverseCryptoQueryLength):
				requestedCrypto += query.split(" ")[x] + " "

		requestedCrypto = requestedCrypto[:-1]
		requestedCryptoSymbol = retrieveCryptoSymbol(requestedCrypto)
		requestedCryptoID = retrieveCryptoID(requestedCrypto)

		for x in range (0, 1314): 
			if requestedCrypto.title() == JSON_DATA[x]['name'] or requestedCrypto.upper() == JSON_DATA[x]['symbol']:
				requestedCryptoPrice = float(JSON_DATA[x]['price_usd'])

		cryptoValue = round((float(dollarValue / requestedCryptoPrice)), 5)
		formattedCryptoValue = str(reverseCryptoCalculatorQuery[0]) + " = " + str(cryptoValue) + " " + str(requestedCryptoSymbol.upper())

		results = [
			InlineQueryResultArticle(
				id=uuid4(),
				thumb_url='https://files.coinmarketcap.com/static/img/coins/128x128/' + requestedCryptoID + '.png',
				title=("Convert " + str(reverseCryptoCalculatorQuery[0]) + " to " + requestedCryptoSymbol),
				description=formattedCryptoValue.split(" ")[2] + " " + formattedCryptoValue.split(" ")[3],
				input_message_content=InputTextMessageContent(formattedCryptoValue))
		]

	elif query == "news":
		results = []
		for x in range (1, 10):

			results.append(

				InlineQueryResultArticle(
					id=uuid4(),
					description=(scrapeArticleSubtitle(x)),
					title=(scrapeArticleTitle(x + 1)),
					input_message_content=InputTextMessageContent(scrapeArticleURL(x - 1))),

				)

	elif "top" in query:
		results = []
		listSize = (int(query.split(" ")[1]) + 1)
		for rank in range (1, listSize):
			listElement = Coin(query, rank)	
			results.append(
				InlineQueryResultArticle(
					id=uuid4(),
					thumb_url='https://files.coinmarketcap.com/static/img/coins/128x128/' + listElement.id + '.png',
					description=("$" + listElement.price_USD),
					title=(str(rank) + ". " + listElement.name),
					input_message_content=InputTextMessageContent(listElement.summary, ParseMode.MARKDOWN))
				)

	else:
		coin = Coin(query, None)
		if coin.name == "None":
			# Makes sure if the user types an invalid cryptocurrency name, it doesn't pop up with a "None" currency with "None" values. This essentially throws off the inline bot by feeding it junk it can't comprehend. 
			results = [
				InlineQueryResultArticle(
            		id=uuid4(),
            		title=(),
            		thumb_url=(),
            		input_message_content=InputTextMessageContent()) 
				]

		results = [
    		# Summary
    		InlineQueryResultArticle(
            	id=uuid4(),
            	title=(coin.name + " (" + coin.symbol + ")"),
            	description="View summary...",
            	thumb_url='https://files.coinmarketcap.com/static/img/coins/128x128/' + coin.id + '.png',
            	input_message_content=InputTextMessageContent(coin.summary, ParseMode.MARKDOWN)),

    		# USD Price
    		InlineQueryResultArticle(
        		id=uuid4(),
        		title=("Price"),
        		description="$" + coin.price_USD,
        		thumb_url="https://imgur.com/7RCGCoc.png",
        		input_message_content=InputTextMessageContent("1 " + coin.symbol + " = $" + coin.price_USD)),

    		# Market Capitalization (USD)
        	InlineQueryResultArticle(
            	id=uuid4(),
            	title=("Market Capitalization"),
            	description="$" + coin.marketCap,
            	thumb_url="https://i.imgur.com/UMczLVP.png",
            	input_message_content=InputTextMessageContent("Market Capitalization of " + coin.name + " (" + coin.symbol + ")" + ": $" + coin.marketCap)),

        	# Circulating Supply 
        	InlineQueryResultArticle(
            	id=uuid4(),
            	title=("Circulating Supply"),
            	description=coin.supply + " " + coin.symbol,
            	thumb_url=("https://i.imgur.com/vXAN23U.png"),
            	input_message_content=InputTextMessageContent("Circulating Supply of " + coin.name + " (" + coin.symbol + ")" + ": " + coin.supply + " " + coin.symbol)),

        	# 24 Hour Percent Change
        	InlineQueryResultArticle(
            	id=uuid4(),
            	title=("Percent Change (24 hours)"),
            	description=coin.percentChange + "%",
            	thumb_url=("https://imgur.com/iAoXFQc.png"),
            	input_message_content=InputTextMessageContent("24 Hour Change in " + coin.name + " (" + coin.symbol + ")" + " Price: " + coin.percentChange + "%"))
        ]

	update.inline_query.answer(results)

def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)

def main():
    # Create the Updater and pass it your bot's token.
    updater = Updater("463277822:AAGhIn--7kELcYSB7MhVp-JUTkOOZtCWZUo")

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram

    # on noncommand i.e message - echo the message on Telegram
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
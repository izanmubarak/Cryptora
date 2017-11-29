''' CRYPTOGRAM '''
# A Telegram bot built in Python that specializes in retrieving information 
# about your favorite cryptocurrency. Current data sourced from CoinMarketCap. Historical data sourced from Coinbase. News articles sourced from Coindesk.

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
		convertQueryInputValue = retrieveConvertQueryUserInputValue(query)
		nameConvertQuery = retrieveConvertQueryCryptoName(query)
		convertQuerySymbol = retrieveCryptoSymbol(nameConvertQuery)
		convertQueryID = retrieveCryptoID(nameConvertQuery)
		convertQueryPrice = calculatePrice(query, convertQuerySymbol)
		results = [
			InlineQueryResultArticle(
				id=uuid4(),
				thumb_url='https://files.coinmarketcap.com/static/img/coins/200x200/' + convertQueryID + '.png',
				title=("Convert " + convertQueryInputValue + " " + convertQuerySymbol + " to USD"),
				description="$" + convertQueryPrice,
				input_message_content=InputTextMessageContent(convertQueryInputValue + " " + convertQuerySymbol + " = $" + convertQueryPrice))
		]
	
	elif query[0] == "$":
		# Reverse CryptoCalculator.
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

		"top 5 cryptocurrencies"

		requestedQuantity = int(query.split(" ")[1])
		results = []

		for x in range (1, requestedQuantity + 1):

			name = convertToFullName(str(x))
			price = retrieveAndFormatCryptoPrice(str(x))
			ID = retrieveCryptoID(str(x))
			results.append(

				InlineQueryResultArticle(
					id=uuid4(),
					thumb_url='https://files.coinmarketcap.com/static/img/coins/128x128/' + ID + '.png',
					description=("$" + price),
					title=(str(x) + ". " + name),
					input_message_content=InputTextMessageContent("Test"))

				)

	else:

		# Main Cryptogram functions.

		# Cryptocurrency data, stored and properly formatted in different variables.
		cryptoName = convertToFullName(query)
		formattedCryptoPrice = retrieveAndFormatCryptoPrice(cryptoName) 
		formattedMarketCap = retrieveAndFormatCryptoMarketCap(cryptoName)
		formattedSupplyValue = retrieveAndFormatCirculatingSupply(cryptoName)
		formattedPercentChange = retrieveAndFormat24HourPercentChange(cryptoName)
		cryptoSymbol = retrieveCryptoSymbol(cryptoName)
		summary = formattedSummary(formattedCryptoPrice, formattedMarketCap, formattedSupplyValue, formattedPercentChange, cryptoName, cryptoSymbol)
		cryptoID = retrieveCryptoID(cryptoName)

		results = [
    		# Summary
    		InlineQueryResultArticle(
            	id=uuid4(),
            	title=(cryptoName + " (" + cryptoSymbol + ")"),
            	description="View summary...",
            	thumb_url='https://files.coinmarketcap.com/static/img/coins/128x128/' \
            	 + cryptoID + '.png',
            	input_message_content=InputTextMessageContent(summary, parse_mode=ParseMode.MARKDOWN)),

    		# USD Price
    		InlineQueryResultArticle(
        		id=uuid4(),
        		title=("Price"),
        		description="$" + formattedCryptoPrice,
        		thumb_url="https://imgur.com/7RCGCoc.png",
        		input_message_content=InputTextMessageContent("1 " + \
        			str(retrieveCryptoSymbol(query)) + " = $" + \
        			str(retrieveAndFormatCryptoPrice(cryptoName)))),

    		# Market Capitalization (USD)
        	InlineQueryResultArticle(
            	id=uuid4(),
            	title=("Market Capitalization (USD)"),
            	description="$" + formattedMarketCap,
            	thumb_url="https://i.imgur.com/UMczLVP.png",
            	input_message_content=InputTextMessageContent\
            	("Market Capitalization of " + cryptoName + " (" + \
				 	str(retrieveCryptoSymbol(query)) + ")" + ": $" + \
			 		str(retrieveAndFormatCryptoMarketCap(cryptoName)))),

        	# Circulating Supply 
        	InlineQueryResultArticle(
            	id=uuid4(),
            	title=("Circulating Supply"),
            	description=formattedSupplyValue + " " + cryptoSymbol,
            	thumb_url=("https://i.imgur.com/vXAN23U.png"),
            	input_message_content=\
            	InputTextMessageContent("Circulating Supply of " + cryptoName + \
            		" (" + str(retrieveCryptoSymbol(query)) + ")" + ": " + \
            		str(retrieveAndFormatCirculatingSupply(cryptoName)) + \
            		" " + str(retrieveCryptoSymbol(query)))),

        	# 24 Hour Percent Change
        	InlineQueryResultArticle(
            	id=uuid4(),
            	title=("Percent Change (24 hours)"),
            	description=formattedPercentChange + "%",
            	thumb_url=("https://imgur.com/iAoXFQc.png"),
            	input_message_content=\
            	InputTextMessageContent("24 Hour Change in " + cryptoName + " (" + \
			 	str(retrieveCryptoSymbol(cryptoName)) + ")" + " Price: " + \
			 	retrieveAndFormat24HourPercentChange(cryptoName) + "%"))
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
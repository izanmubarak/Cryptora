''' CRYPTOGRAM '''
# A Telegram bot built in Python that specializes in retrieving information 
# about your favorite cryptocurrency. Data sourced from CoinMarketCap.com. 

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

# Constant variables. 
JSON_API_URL = 'https://api.coinmarketcap.com/v1/ticker/?limit=1315'
JSON_DATA = requests.get(JSON_API_URL).json()
token = '463277822:AAGhIn--7kELcYSB7MhVp-JUTkOOZtCWZUo'

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - \
 %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def retrieveRank(query):
	for x in range (0, 1314):
		if query.upper() == JSON_DATA[x]['symbol'] or \
		(query.lower() == JSON_DATA[x]['id']) or \
		(query.title() == JSON_DATA[x]['name']):
			return int(x)

def convertToFullName(query):

	# With this function, a user can type in the symbol or the name of the 
	# cryptocurrency in any case (lower or upper case), and this function will 
	# return the properly formatted name. 
    
	for x in range (0, 1314): 
		if query.upper() == JSON_DATA[x]['symbol'] or \
		(query.lower() == JSON_DATA[x]['id']) or \
		(query.title() == JSON_DATA[x]['name']):
			fullCryptoCurrencyName = JSON_DATA[x]['name']
			return fullCryptoCurrencyName

def retrieveCryptoSymbol(query):

	# This function will retrieve the cryptocurrency symbol for the chosen 
	# currency.

	for x in range (0, 1314): 
		if query.upper() == JSON_DATA[x]['symbol'] or \
		query.lower() == JSON_DATA[x]['id'] or \
		query.title() == JSON_DATA[x]['name'] :
			return JSON_DATA[x]['symbol']

def retrieveCryptoID(query):

	# Retrieves cryptocurrency ID on CoinMarketCap.

	for x in range (0, 1314):
		if query.upper() == JSON_DATA[x]['symbol'] or \
		 query.lower() == JSON_DATA[x]['id'] or \
		 query.title() == JSON_DATA[x]['name']:
			return JSON_DATA[x]['id']


def retrieveAndFormatCryptoPrice(query):

	# This function retrieves and properly formats the chosen cryptocurrency's
	# price. If the price of the coin is above $0.01, it automatically rounds. 
	# to two decimal places. It also intelligently adds comma separators.

	for x in range (0, 1314): 
		if query == JSON_DATA[x]['name']:
			unformattedCryptoPrice = float(JSON_DATA[x]['price_usd'])
			if unformattedCryptoPrice > 0.01:
				unformattedCryptoPrice = round(unformattedCryptoPrice, 2)
			formattedCryptoPrice = "{:,}".format(unformattedCryptoPrice)
			return formattedCryptoPrice

def retrieveAndFormatCryptoMarketCap(query):

	# This function retrieves and properly formats the chosen cryptocurrency's
	# market capitalization. 

	for x in range (0, 1314):
		if query == JSON_DATA[x]['name']:
			unformattedMarketCap = float((JSON_DATA[x]['market_cap_usd']))
			unformattedMarketCap = Decimal(unformattedMarketCap)
			formattedMarketCap = "{:,}".format(unformattedMarketCap)
			return formattedMarketCap

def retrieveAndFormatCirculatingSupply(query):

	# Retrieves and properly formats chosen cryptocurrency's circulating supply 
	# count.

	for x in range (0, 1314):
		if query == JSON_DATA[x]['name']:
			unformattedSupplyValue = float((JSON_DATA[x]['available_supply']))
			unformattedSupplyValue = Decimal(unformattedSupplyValue)
			formattedSupplyValue = "{:,}".format(unformattedSupplyValue)
			return formattedSupplyValue

def retrieveAndFormat24HourPercentChange(query):

	# Retrieves and properly formats chosen cryptocurrency's change in value in
	# the last 24 hours.

	for x in range (0, 1314):
		if query == JSON_DATA[x]['name']:
			formattedPercentChange = JSON_DATA[x]['percent_change_24h']
			return formattedPercentChange

def formattedSummary(price, cap, supplyValue, percentChange, name, symbol):

	# Returns a summary of the cryptocurrency.

	summary = "***" + name + "***" + " (" + symbol + ")" + '\n \n' + '***Price***: $' + price + '\n' + '***Market Capitalization***: $' + cap + '\n' + '***Circulating Supply***: ' + supplyValue + " " + symbol + '\n' + '***24 Hour Percent Change***: ' + percentChange + "% \n"
	return summary

def inlinequery(bot, update):

	# This function handles all queries to the bot. 
	# It directs user choice by providing 6 options: 
		# Price (done!)
		# Market capitalization (done!)
		# Circulating supply (done!)
		# 24hr % change (done!)
		# A summary of the cryptocurrency, which provides the aforementioned 
			# data in a single message. (done!)

	query = update.inline_query.query

	# Cryptocurrency data, stored and properly formatted in different variables.
	cryptoName = convertToFullName(query)
	formattedCryptoPrice = retrieveAndFormatCryptoPrice(cryptoName) 
	formattedMarketCap = retrieveAndFormatCryptoMarketCap(cryptoName)
	formattedSupplyValue = retrieveAndFormatCirculatingSupply(cryptoName)
	formattedPercentChange = retrieveAndFormat24HourPercentChange(cryptoName)
	cryptoSymbol = retrieveCryptoSymbol(cryptoName)
	summary = formattedSummary(formattedCryptoPrice, \
		formattedMarketCap, formattedSupplyValue, formattedPercentChange, \
		cryptoName, cryptoSymbol)
	cryptoID = retrieveCryptoID(cryptoName)

	results = [

    	# Summary
        InlineQueryResultArticle(
            id=uuid4(),
            title=(cryptoName),
            thumb_url='https://files.coinmarketcap.com/static/img/coins/128x128/' \
             + cryptoID + '.png',
            input_message_content=InputTextMessageContent(summary, parse_mode=ParseMode.MARKDOWN)),

    	# USD Price
    	InlineQueryResultArticle(
        	id=uuid4(),
        	title=("Price (USD)"),
        	thumb_url="https://imgur.com/7RCGCoc.png",
        	input_message_content=InputTextMessageContent("1 " + \
        		str(retrieveCryptoSymbol(query)) + " = $" + \
        		str(retrieveAndFormatCryptoPrice(cryptoName)))),

    	# Market Capitalization (USD)
        InlineQueryResultArticle(
            id=uuid4(),
            title=("Market Capitalization (USD)"),
            thumb_url="https://i.imgur.com/UMczLVP.png",
            input_message_content=InputTextMessageContent\
            ("Market Capitalization of " + cryptoName + " (" + \
			 str(retrieveCryptoSymbol(query)) + ")" + ": $" + \
			 str(retrieveAndFormatCryptoMarketCap(cryptoName)))),

        # Circulating Supply 
        InlineQueryResultArticle(
            id=uuid4(),
            title=("Circulating Supply"),
            input_message_content=\
            InputTextMessageContent("Circulating Supply of " + cryptoName + \
            	" (" + str(retrieveCryptoSymbol(query)) + ")" + ": " + \
            	str(retrieveAndFormatCirculatingSupply(cryptoName)) + \
            	" " + str(retrieveCryptoSymbol(query)))),

        # 24 Hour Percent Change
        InlineQueryResultArticle(
            id=uuid4(),
            title=("Percent Change (24 hours)"),
            input_message_content=\
            InputTextMessageContent("24 Hour Change in " + cryptoName + " (" + \
			 str(retrieveCryptoSymbol(cryptoName)) + ")" + " Price: " + \
			 retrieveAndFormatCirculatingSupply(cryptoName) + "%"))
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
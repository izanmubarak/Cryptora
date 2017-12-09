from uuid import uuid4
import re
from telegram.utils.helpers import escape_markdown
from telegram import InlineQueryResultArticle, ParseMode,InputTextMessageContent
from telegram.ext import Updater, InlineQueryHandler, CommandHandler
import logging
import sys
import requests
from decimal import Decimal
from bs4 import BeautifulSoup
import feedparser
import datefinder
import dateparser
from Cryptora_functions import *

# -*- coding: utf-8 -*-
import redis
import os
# import some_api_lib
# import ...

# Example of your code beginning
#           Config vars
token = os.environ['TELEGRAM_TOKEN']
#             ...

# If you use redis, install this add-on https://elements.heroku.com/addons/heroku-redis
r = redis.from_url(os.environ.get("REDIS_URL"))

#       Your bot code below
# bot = telebot.TeleBot(token)
# some_api = some_api_lib.connect(some_api_token)
#              ...

# Constant variables. 
JSON_API_URL = 'https://api.coinmarketcap.com/v1/ticker/?limit=10000'
JSON_DATA = requests.get(JSON_API_URL).json()
NEWS_URL = "http://coindesk.com/feed"

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - \
 %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def inlinequery(bot, update):

	query = update.inline_query.query
	dateInString = determine_if_date_in_string(query)

	# CryptoCalculator
	if query[0].isdigit():

		userInputName = ""
		for x in range (1, len(query.split(" "))):
			userInputName += query.split(" ")[x] + " "

		inputCoin = Coin((userInputName[:-1]).title(), None, False)
		instance = CryptoCalculatorInstance(query, inputCoin.symbol, False, None, None)
		results = [
			InlineQueryResultArticle(
				id=uuid4(),
				thumb_url='https://files.coinmarketcap.com/static/img/coins/200x200/' + inputCoin.id + '.png',
				title=("Convert " + instance.inputValue + " " + inputCoin.symbol + " to USD"),
				description="$" + instance.calculatedValue,
				input_message_content=InputTextMessageContent(instance.inputValue + " " + inputCoin.symbol + " = $" + instance.calculatedValue))
		]
	
	# Reverse CryptoCalculator
	elif query[0] == "$":	
		splitQuery = query.split(" ")
		length = len(splitQuery)
		inputDollarValue = (splitQuery[0])[1:]
		currency = ""

		if splitQuery[1] == "to":
			for x in range (2, length):
				currency += splitQuery[x] + " "
		else:
			for x in range (1, length):
				currency += splitQuery[x] + " "

		currency = currency[:-1]
		inputCoin = Coin(currency, None, True)
		value = CryptoCalculatorInstance(query, inputCoin.symbol, True, inputCoin.price_USD, inputDollarValue)

		results = [
			InlineQueryResultArticle(
				id=uuid4(),
				title=("Convert $" + inputDollarValue + " to " + inputCoin.symbol),
				thumb_url='https://files.coinmarketcap.com/static/img/coins/200x200/' + inputCoin.id + '.png',
				description=(str(value.calculatedValue) + " " + str(inputCoin.symbol)),
				input_message_content=InputTextMessageContent("$" + str(inputDollarValue) + " = " + str(value.calculatedValue) + " " + str(inputCoin.symbol)))
		]

	# News
	elif "news" in query:
		results = []
		feed = feedparser.parse("http://coindesk.com/feed")
		for x in range (0, 9):
			article = NewsArticle(x, feed)
			results.append(
				InlineQueryResultArticle(
					id=uuid4(),
					description=(article.subtitle),
					thumb_url=article.thumbnailURL,
					title=(article.title),
					input_message_content=InputTextMessageContent(article.URL)),
				)
	# Top X
	elif "top" in query:
		results = []
		listSize = (int(query.split(" ")[1]) + 1)
		for rank in range (1, listSize):
			listElement = Coin(query, str(rank), False)	
			results.append(
				InlineQueryResultArticle(
					id=uuid4(),
					thumb_url='https://files.coinmarketcap.com/static/img/coins/128x128/' + listElement.id + '.png',
					description=("$" + listElement.price_USD),
					title=(str(rank) + ". " + listElement.name),
					input_message_content=InputTextMessageContent(listElement.summary, ParseMode.MARKDOWN))
				)

	elif dateInString == True or "ago" in query:

		if "ago" in query:

			splitQuery = query.split(" ")
			relativeDate = splitQuery[-3:]
			relativeDate = " ".join(relativeDate)

			day = str((dateparser.parse(relativeDate)).day)
			month = str((dateparser.parse(relativeDate)).month)
			year = str((dateparser.parse(relativeDate)).year)

			name = splitQuery[:len(splitQuery)-3]
			name = " ".join(name)

			coin = Coin(name, None, True)
			data = PriceOnDay(coin.id, day, month, year)

			monthName = convert_month_number_to_name(data.month)

			description = monthName + " " + data.day + ", " + data.year

			string = ("***Price Data for " + coin.name + "*** \n" + description + "\n \n" + "***High:*** $" + data.high + "\n***Low:*** $" + data.low + "\n***Open:*** $" + data.open + "\n***Close:*** $" + data.close)

			if len(data.year) != 4:
				results = [
					InlineQueryResultArticle(
            			id=uuid4(),
            			title=(),
            			thumb_url=(),
            			input_message_content=InputTextMessageContent())
					]

			results = [
					InlineQueryResultArticle(
            			id=uuid4(),
            			title=("View Price Data for " + coin.name),
            			thumb_url='https://files.coinmarketcap.com/static/img/coins/128x128/' + coin.id + '.png',
            			description=(description),
            			input_message_content=InputTextMessageContent(string, ParseMode.MARKDOWN)),

					InlineQueryResultArticle(
            			id=uuid4(),
            			title=("High"),
            			description=("$" + data.high),
            			thumb_url="https://imgur.com/ntXndWR.png",
            			input_message_content=InputTextMessageContent("***" + coin.name + " High Price*** \n" + description + "\n \n$" + data.high,  ParseMode.MARKDOWN)),

					InlineQueryResultArticle(
	            		id=uuid4(),
	            		title=("Low"),
	            		description=("$" + data.low),
	            		thumb_url="https://imgur.com/zOfZSYj.png",
	            		input_message_content=InputTextMessageContent("***" + coin.name + " Low Price*** \n" + description + "\n \n$" +data.low, ParseMode.MARKDOWN)),

					InlineQueryResultArticle(
	            		id=uuid4(),
	            		title=("Open"),
	            		thumb_url="https://imgur.com/EYOqB1W.png",
	            		description=("$" + data.open),
	            		input_message_content=InputTextMessageContent("***" + coin.name + " Opening Price*** \n" + description + "\n \n$" + data.open, ParseMode.MARKDOWN)),

					InlineQueryResultArticle(
	            		id=uuid4(),
	            		title=("Close"),
	            		thumb_url="https://imgur.com/iQXqgYU.png",
	            		description=("$" + data.close),
	            		input_message_content=InputTextMessageContent("***" + coin.name + " Closing Price*** \n" + description + "\n \n$" + data.close, ParseMode.MARKDOWN))

					]

		else:
		
			name = get_coin_name_from_historical_query(get_coin_word_count(query), query)

			day = str(get_day(query, True))
			month = str(get_month(query, True))
			year = str(get_year(query, True))

			coin = Coin(name, None, True)
			data = PriceOnDay(coin.id, day, month, year)

			monthName = convert_month_number_to_name(data.month)

			description = monthName + " " + data.day + ", " + data.year

			string = ("***Price Data for " + coin.name + "*** \n" + description + "\n \n" + "***High:*** $" + data.high + "\n***Low:*** $" + data.low + "\n***Open:*** $" + data.open + "\n***Close:*** $" + data.close)

			if len(data.year) != 4:
				results = [
					InlineQueryResultArticle(
            			id=uuid4(),
            			title=(),
            			thumb_url=(),
            			input_message_content=InputTextMessageContent())
					]

			results = [
					InlineQueryResultArticle(
            			id=uuid4(),
            			title=("View Price Data for " + coin.name),
            			thumb_url='https://files.coinmarketcap.com/static/img/coins/128x128/' + coin.id + '.png',
            			description=(description),
            			input_message_content=InputTextMessageContent(string, ParseMode.MARKDOWN)),

					InlineQueryResultArticle(
            			id=uuid4(),
            			title=("High"),
            			description=("$" + data.high),
            			thumb_url="https://imgur.com/ntXndWR.png",
            			input_message_content=InputTextMessageContent("***" + coin.name + " High Price*** \n" + description + "\n \n$" + data.high,  ParseMode.MARKDOWN)),

					InlineQueryResultArticle(
	            		id=uuid4(),
	            		title=("Low"),
	            		description=("$" + data.low),
	            		thumb_url="https://imgur.com/zOfZSYj.png",
	            		input_message_content=InputTextMessageContent("***" + coin.name + " Low Price*** \n" + description + "\n \n$" +data.low, ParseMode.MARKDOWN)),

					InlineQueryResultArticle(
	            		id=uuid4(),
	            		title=("Open"),
	            		thumb_url="https://imgur.com/EYOqB1W.png",
	            		description=("$" + data.open),
	            		input_message_content=InputTextMessageContent("***" + coin.name + " Opening Price*** \n" + description + "\n \n$" + data.open, ParseMode.MARKDOWN)),

					InlineQueryResultArticle(
	            		id=uuid4(),
	            		title=("Close"),
	            		thumb_url="https://imgur.com/iQXqgYU.png",
	            		description=("$" + data.close),
	            		input_message_content=InputTextMessageContent("***" + coin.name + " Closing Price*** \n" + description + "\n \n$" + data.close, ParseMode.MARKDOWN))

					]

		

	# Cryptocurrency information
	else:
		coin = Coin(query, None, False)
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
    updater = Updater(token)

	PORT = int(os.environ.get('PORT', '5000'))
	updater = Updater(token)
	# add handlers
	updater.start_webhook(listen="0.0.0.0",
                      port=PORT,
                      url_path=token)
	updater.bot.set_webhook("https://cryptora.herokuapp.com/" + token)
	updater.idle()

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
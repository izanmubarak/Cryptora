# -*- coding: utf-8 -*-
# Cryptora - Public Repository
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
import gdax
from collections import OrderedDict
from Cryptora_functions import *

# Constant variables. 
JSON_API_URL = 'https://api.coinmarketcap.com/v1/ticker/?limit=10000'
NEWS_URL = "http://coindesk.com/feed"

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - \
 %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def inlinequery(bot, update):

	query = update.inline_query.query
	dateInString = determine_if_date_in_string(query)
	
	for x in range (0, len(query)):
		if query.endswith(","):
			query = query[:-1]
		if query.startswith(","):
			query = query[1:]

	# CryptoCalculator
	if query[0].isdigit() and query[0] != '0':

		userInputName = ""
		for x in range (1, len(query.split(" "))):
			userInputName += query.split(" ")[x] + " "

		inputCoin = Coin((userInputName[:-1]).title(), None, False)
		instance = CryptoCalculatorInstance(query, inputCoin.symbol, \
			False, None, None)

		results = [
			InlineQueryResultArticle(
				id=uuid4(),
				thumb_url='https://files.coinmarketcap.com/static/img/coins/' \
				+ '200x200/' + inputCoin.id + '.png',
				title=("Convert " + instance.inputValue + " " + \
					inputCoin.symbol + " to USD"),
				description="$" + instance.calculatedValue,
				input_message_content=InputTextMessageContent(\
					instance.inputValue + " " + inputCoin.symbol + " = $" + \
					 instance.calculatedValue))
		]

		if inputCoin.name == "None":

			bot.answerInlineQuery(update.inline_query.id, results=[], \
				switch_pm_text='No cryptocurrency found. Please try again.', \
				switch_pm_parameter='do_something')
	
	# Reverse CryptoCalculator
	elif query[0] == "$":	
		try:
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
			value = CryptoCalculatorInstance(query, inputCoin.symbol, True, \
				inputCoin.price_USD, inputDollarValue)

			results = [
				InlineQueryResultArticle(
					id=uuid4(),
					title=("Convert $" + inputDollarValue + " to " \
						+ inputCoin.symbol),
					thumb_url='https://files.coinmarketcap.com/static/img/coins/' \
					+ '200x200/' + inputCoin.id + '.png',
					description=(str(value.calculatedValue) + " " + \
						str(inputCoin.symbol)),
					input_message_content=InputTextMessageContent("$" + \
						str(inputDollarValue) + " = " + str(value.calculatedValue) \
						+ " " + str(inputCoin.symbol)))
			]
		except:

			bot.answerInlineQuery(update.inline_query.id, results=[], \
				switch_pm_text='No cryptocurrency found. Please try again.', \
				switch_pm_parameter='do_something')

	# News
	elif "news" in query:
		results = []
		feed = feedparser.parse("http://coindesk.com/feed")
		for x in range (0, 10):
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
		data = requests.get(JSON_API_URL).json()
		if query.lower() == "top":
			listSize = 51
		else:
			listSize = (int(query.split(" ")[1]) + 1)

		for rank in range (1, listSize):
			
			ID = data[rank - 1]['id']
			symbol = data[rank - 1]['symbol']
			name = data[rank - 1]['name']
			supplyValue = "{:,}".format(Decimal(float(\
					data[rank - 1]['available_supply'])))
			cap = str("{:,}".format(Decimal(\
					float(data[rank - 1]['market_cap_usd']))))
			percentChange = data[rank - 1]['percent_change_24h']

			if float(data[rank - 1]['price_usd']) < 1.00:		
				price = data[rank - 1]['price_usd']

			else:
				decimalizedPrice = Decimal(data[rank - 1]['price_usd']).quantize(\
					Decimal('1.00'), rounding = 'ROUND_HALF_DOWN')
				price = str("{:,}".format(decimalizedPrice))
				

			summary = ("***" + name + "***" + " (" + symbol + ")" + '\n \n' + \
			'***Price***: $' + price + '\n' + '***Market Capitalization***: $' \
			 + cap + '\n' + '***Circulating Supply***: ' + supplyValue + " " + \
			  symbol + '\n' + '***24 Hour Percent Change***: ' + \
			   percentChange + "% \n")

	
			results.append(
				InlineQueryResultArticle(
					id=uuid4(),
					thumb_url='https://files.coinmarketcap.com/static/img/' \
					+ 'coins/128x128/' + ID + '.png',
					description=("$" + price),
					title=(str(rank) + ". " + name),
					input_message_content=InputTextMessageContent(\
						summary, ParseMode.MARKDOWN))
				)

	elif query.upper() == "GDAX":

		public_client = gdax.PublicClient()

		bitcoin = get_GDAX_price('bitcoin')
		bitcoinCash = get_GDAX_price('bitcoin_cash')
		ethereum = get_GDAX_price('ethereum')
		litecoin = get_GDAX_price('litecoin')

		results = [
					InlineQueryResultArticle(
            			id=uuid4(),
            			title=("GDAX Pricing"),
            			thumb_url="https://imgur.com/Eyh7KSb.png",
            			description=("View summary..."),
            			input_message_content=InputTextMessageContent((\
            				"***GDAX Trading Prices*** \n \n***Bitcoin:*** $" \
            				+ bitcoin + "\n***Litecoin:*** $" + litecoin + \
            				"\n***Ethereum:*** $" + ethereum + "\n***Bitcoin Cash:*** $" + \
            				bitcoinCash), ParseMode.MARKDOWN)),

					InlineQueryResultArticle(
            			id=uuid4(),
            			title=("Bitcoin"),
            			thumb_url='https://files.coinmarketcap.com/static/' + \
            			'img/coins/128x128/bitcoin.png',
            			description=("$" + bitcoin),
            			input_message_content=InputTextMessageContent((\
            				"***GDAX Bitcoin Trading Price:*** $" + bitcoin),\
            				 ParseMode.MARKDOWN)),

					InlineQueryResultArticle(
            			id=uuid4(),
            			title=("Litecoin"),
            			description=("$" + litecoin),
            			thumb_url='https://files.coinmarketcap.com/static/' + \
            			'img/coins/128x128/litecoin.png',
            			input_message_content=InputTextMessageContent((\
            				"***GDAX Litecoin Trading Price:*** $" + litecoin), \
            				 ParseMode.MARKDOWN)),

					InlineQueryResultArticle(
	            		id=uuid4(),
	            		title=("Ethereum"),
	            		description=("$" + ethereum),
            			thumb_url='https://files.coinmarketcap.com/static/' + \
            			'img/coins/128x128/ethereum.png',
            			input_message_content=InputTextMessageContent((\
            				"***GDAX Ethereum Trading Price:*** $" + ethereum),\
            				 ParseMode.MARKDOWN)),

					InlineQueryResultArticle(
	            		id=uuid4(),
	            		title=("Bitcoin Cash"),
	            		description=("$" + bitcoinCash),
            			thumb_url='https://files.coinmarketcap.com/static/' + \
            			'img/coins/128x128/bitcoin-cash.png',
            			input_message_content=InputTextMessageContent((\
            				"***GDAX Bitcoin Cash Trading Price:*** $" + bitcoinCash),\
            				 ParseMode.MARKDOWN))

					]

	elif dateInString == True or "ago" in query or "yesterday" in query:
		
		if "yesterday" in query:

			day = str((dateparser.parse("yesterday")).day)
			month = str((dateparser.parse("yesterday")).month)
			year = str((dateparser.parse("yesterday")).year)

			splitQuery = query.split(" ")
			del splitQuery[-1]
			name = " ".join(splitQuery)

			coin = Coin(name, None, True)
			data = PriceOnDay(coin.id, day, month, year)

			monthName = convert_month_number_to_name(data.month)

			description = monthName + " " + data.day + ", " + data.year

			string = ("***Price Data for " + coin.name + "*** \n" + \
				description + "\n \n" + "***High:*** $" + data.high + \
				"\n***Low:*** $" + data.low + "\n***Open:*** $" + data.open + \
				"\n***Close:*** $" + data.close)

			results = [
					InlineQueryResultArticle(
            			id=uuid4(),
            			title=("Price Data for " + coin.name),
            			thumb_url='https://files.coinmarketcap.com/static/' + \
            			'img/coins/128x128/' + coin.id + '.png',
            			description=(description),
            			input_message_content=InputTextMessageContent(string, \
            			 ParseMode.MARKDOWN)),

					InlineQueryResultArticle(
            			id=uuid4(),
            			title=("Market Capitalization"),
            			description=("$" + data.marketCap),
            			thumb_url="https://i.imgur.com/UMczLVP.png",
            			input_message_content=InputTextMessageContent("***" + \
            			 coin.name + " Market Capitalization*** \n" + description + \
            			  "\n \n$" + data.marketCap,  ParseMode.MARKDOWN)),

					InlineQueryResultArticle(
            			id=uuid4(),
            			title=("High"),
            			description=("$" + data.high),
            			thumb_url="https://imgur.com/ntXndWR.png",
            			input_message_content=InputTextMessageContent("***" + \
            				coin.name + " High Price*** \n" + description + \
            				"\n \n$" + data.high,  ParseMode.MARKDOWN)),

					InlineQueryResultArticle(
	            		id=uuid4(),
	            		title=("Low"),
	            		description=("$" + data.low),
	            		thumb_url="https://imgur.com/zOfZSYj.png",
	            		input_message_content=InputTextMessageContent("***" + \
	            			coin.name + " Low Price*** \n" + description + \
	            			"\n \n$" +data.low, ParseMode.MARKDOWN)),

					InlineQueryResultArticle(
	            		id=uuid4(),
	            		title=("Open"),
	            		thumb_url="https://imgur.com/EYOqB1W.png",
	            		description=("$" + data.open),
	            		input_message_content=InputTextMessageContent("***" + \
	            			coin.name + " Opening Price*** \n" + description + \
	            			 "\n \n$" + data.open, ParseMode.MARKDOWN)),

					InlineQueryResultArticle(
	            		id=uuid4(),
	            		title=("Close"),
	            		thumb_url="https://imgur.com/iQXqgYU.png",
	            		description=("$" + data.close),
	            		input_message_content=InputTextMessageContent("***" + \
	            			coin.name + " Closing Price*** \n" + description + \
	            			"\n \n$" + data.close, ParseMode.MARKDOWN))

					]

		elif "ago" in query:

			try:

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

				string = ("***Price Data for " + coin.name + "*** \n" + \
					description + "\n \n" + "***High:*** $" + data.high + \
					"\n***Low:*** $" + data.low + "\n***Open:*** $" + data.open + \
					"\n***Close:*** $" + data.close)

				results = [
						InlineQueryResultArticle(
	            			id=uuid4(),
	            			title=("Price Data for " + coin.name),
	            			thumb_url='https://files.coinmarketcap.com/static/' + \
	            			'img/coins/128x128/' + coin.id + '.png',
	            			description=(description),
	            			input_message_content=InputTextMessageContent(string, \
	            			 ParseMode.MARKDOWN)),

						InlineQueryResultArticle(
	            			id=uuid4(),
	            			title=("Market Capitalization"),
	            			description=("$" + data.marketCap),
	            			thumb_url="https://i.imgur.com/UMczLVP.png",
	            			input_message_content=InputTextMessageContent("***" + \
	            			 coin.name + " Market Capitalization*** \n" + description + \
	            			  "\n \n$" + data.marketCap,  ParseMode.MARKDOWN)),

						InlineQueryResultArticle(
	            			id=uuid4(),
	            			title=("High"),
	            			description=("$" + data.high),
	            			thumb_url="https://imgur.com/ntXndWR.png",
	            			input_message_content=InputTextMessageContent("***" + \
	            				coin.name + " High Price*** \n" + description + \
	            				"\n \n$" + data.high,  ParseMode.MARKDOWN)),

						InlineQueryResultArticle(
		            		id=uuid4(),
		            		title=("Low"),
		            		description=("$" + data.low),
		            		thumb_url="https://imgur.com/zOfZSYj.png",
		            		input_message_content=InputTextMessageContent("***" + \
		            			coin.name + " Low Price*** \n" + description + \
		            			"\n \n$" +data.low, ParseMode.MARKDOWN)),

						InlineQueryResultArticle(
		            		id=uuid4(),
		            		title=("Open"),
		            		thumb_url="https://imgur.com/EYOqB1W.png",
		            		description=("$" + data.open),
		            		input_message_content=InputTextMessageContent("***" + \
		            			coin.name + " Opening Price*** \n" + description + \
		            			 "\n \n$" + data.open, ParseMode.MARKDOWN)),

						InlineQueryResultArticle(
		            		id=uuid4(),
		            		title=("Close"),
		            		thumb_url="https://imgur.com/iQXqgYU.png",
		            		description=("$" + data.close),
		            		input_message_content=InputTextMessageContent("***" + \
		            			coin.name + " Closing Price*** \n" + description + \
		            			"\n \n$" + data.close, ParseMode.MARKDOWN))

						]
			except:
				bot.answerInlineQuery(update.inline_query.id, results=[], \
					switch_pm_text='Invalid date query. Please try again.', \
					switch_pm_parameter='do_something')

		else:

			try:
				name = get_coin_name_from_historical_query(get_coin_word_count(query), query)

				day = str(get_day(query, True))
				month = str(get_month(query, True))
				year = str(get_year(query, True))

				coin = Coin(name, None, True)
				data = PriceOnDay(coin.id, day, month, year)

				monthName = convert_month_number_to_name(data.month)

				description = monthName + " " + data.day + ", " + data.year

				string = ("***Price Data for " + coin.name + "*** \n" + \
					description + "\n \n" + "***High:*** $" + data.high + \
					"\n***Low:*** $" + data.low + "\n***Open:*** $" + data.open + \
					 "\n***Close:*** $" + data.close)

				if len(data.year) != 4:
					bot.answerInlineQuery(update.inline_query.id, results=[], \
						switch_pm_text='Invalid date entered. Please try again.', \
						switch_pm_parameter='do_something')

				results = [
						InlineQueryResultArticle(
	            			id=uuid4(),
	            			title=("Price Data for " + coin.name),
	            			thumb_url='https://files.coinmarketcap.com/static/img/' \
	            			+ 'coins/128x128/' + coin.id + '.png',
	            			description=(description),
	            			input_message_content=InputTextMessageContent(string, \
	            				ParseMode.MARKDOWN)),

						InlineQueryResultArticle(
	            			id=uuid4(),
	            			title=("Market Capitalization"),
	            			description=("$" + data.marketCap),
	            			thumb_url="https://i.imgur.com/UMczLVP.png",
	            			input_message_content=InputTextMessageContent("***" + \
	            			 coin.name + " Market Capitalization*** \n" + description + \
	            			  "\n \n$" + data.marketCap,  ParseMode.MARKDOWN)),

						InlineQueryResultArticle(
	            			id=uuid4(),
	            			title=("High"),
	            			description=("$" + data.high),
	            			thumb_url="https://imgur.com/ntXndWR.png",
	            			input_message_content=InputTextMessageContent("***" + \
	            			 coin.name + " High Price*** \n" + description + \
	            			  "\n \n$" + data.high,  ParseMode.MARKDOWN)),

						InlineQueryResultArticle(
		            		id=uuid4(),
		            		title=("Low"),
		            		description=("$" + data.low),
		            		thumb_url="https://imgur.com/zOfZSYj.png",
		            		input_message_content=InputTextMessageContent("***" + \
		            			coin.name + " Low Price*** \n" + description + \
		            			"\n \n$" +data.low, ParseMode.MARKDOWN)),

						InlineQueryResultArticle(
		            		id=uuid4(),
		            		title=("Open"),
		            		thumb_url="https://imgur.com/EYOqB1W.png",
		            		description=("$" + data.open),
		            		input_message_content=InputTextMessageContent("***" + \
		            			coin.name + " Opening Price*** \n" + description + \
		            			 "\n \n$" + data.open, ParseMode.MARKDOWN)),

						InlineQueryResultArticle(
		            		id=uuid4(),
		            		title=("Close"),
		            		thumb_url="https://imgur.com/iQXqgYU.png",
		            		description=("$" + data.close),
		            		input_message_content=InputTextMessageContent("***" + \
		            			coin.name + " Closing Price*** \n" + description + \
		            			"\n \n$" + data.close, ParseMode.MARKDOWN))

						]
			except:
				bot.answerInlineQuery(update.inline_query.id, results=[], \
					switch_pm_text='Invalid date entered. Please try again.', \
					switch_pm_parameter='do_something')

	elif query.lower() == "global":

		data = GeneralStats()

		results = [

			InlineQueryResultArticle(
    			id=uuid4(),
    			title=("Total Market Capitalization"),
				thumb_url="https://i.imgur.com/UMczLVP.png",
    			description=("$" + str(data.marketCap)),
    			input_message_content=InputTextMessageContent("***Total Market Capitalization:*** " \
    				+ "$" + str(data.marketCap), ParseMode.MARKDOWN)),

			InlineQueryResultArticle(
    			id=uuid4(),
    			title=("Total 24 Hour Volume"),
				thumb_url="https://imgur.com/Qw4y4Ed.png",
    			description=("$" + str(data.volume24h)),
    			input_message_content=InputTextMessageContent("***Total 24 Hour Volume:*** $" \
    				+ str(data.volume24h),  ParseMode.MARKDOWN)),

			InlineQueryResultArticle(
    			id=uuid4(),
    			title=("Bitcoin Dominance"),
    			description=(str(data.dominanceBTC) + "%"),
    			thumb_url="https://imgur.com/tXiapTn.png",
    			input_message_content=InputTextMessageContent("***Bitcoin Dominance:*** " \
    				+ str(data.dominanceBTC) + "%",  ParseMode.MARKDOWN)),

			InlineQueryResultArticle(
        		id=uuid4(),
        		title=("Active Cryptocurrencies"),
        		thumb_url="https://imgur.com/g6YajTp.png",
        		description=(str(data.activeCryptoCount) + " active cryptocurrencies"),
        		input_message_content=InputTextMessageContent(str(data.activeCryptoCount) \
        			+ " active cryptocurrencies on CoinMarketCap.", ParseMode.MARKDOWN)),

			InlineQueryResultArticle(
        		id=uuid4(),
        		thumb_url="https://imgur.com/qO0rcCI.png",
        		title=("Markets"),
        		description=(str(data.marketCount) + " markets"),
        		input_message_content=InputTextMessageContent(str(data.marketCount) \
        			+ " markets on CoinMarketCap." , ParseMode.MARKDOWN)),

			]


	elif "help" == query.lower():

		results = [
				InlineQueryResultArticle(
	    			id=uuid4(),
	    			title=("Retrieve cryptocurrency prices"),
	    			description=('"BTC", "bitcoin"'),
	    			thumb_url="https://imgur.com/joQ2gGR.png",
	    			input_message_content=InputTextMessageContent(\
	    				"To get information about a cryptocurrency, just type " \
	    				+ "the name or the shorthand abbreviation. For example, " \
	    				+ "if you want to see information about Ethereum, you " \
	    				+ "can just type `ethereum` or `ETH` (case does not " \
	    				+ "matter), and Cryptora will get up to the moment " \
	    				+ "information about Ethereum for you. \n\nYou can " \
	    				+ "also type the name of your cryptocurrency, followed " \
	    				+ "by a date in MM/DD/YYYY format (or Month Day, Year " \
	    				+ "format) to get historical pricing. Alternatively, " \
	    				+ "you can type relative dates too – so typing " \
	    				+ "`bitcoin 2 weeks ago` will get you the price of " \
	    				+ "Bitcoin two weeks ago.", ParseMode.MARKDOWN)),

				InlineQueryResultArticle(
	        		id=uuid4(),
	        		title=("Convert between cryptocurrencies and U.S. dollars"),
	        		description=('"$2000 BTC", "50 BTC"'),
	        		thumb_url="https://imgur.com/8XwhAWO.png",
	        		input_message_content=InputTextMessageContent("Cryptora " \
	        		+ "can convert cryptocurrency values to U.S. dollars. Just " \
	        		+ "type in a cryptocurrency value – for instance, `50 ETH` " \
	        		+ "– to see the USD value of 50 ETH. " \
	        		+ "\n\nYou can also type in a U.S. dollar amount and follow " \
	        		+ "that with a cryptocurrency to convert from dollars to a " \
	        		+ "cryptocurrency. For example, `$50 ETH` will retrieve the " \
	        		+ "quantity of Ethereum that $50 will get you.", ParseMode.MARKDOWN)),

				InlineQueryResultArticle(
	    			id=uuid4(),
	    			title=("Read the latest cryptocurrency headlines"),
	    			description=('"news"'),
	    			thumb_url="https://imgur.com/FUX10Vi.png",
	    			input_message_content=InputTextMessageContent("You can type " \
	    			+ "`news` to get the ten latest headlines from CoinDesk.com " \
	    			+ "in-line. Tap a link to send to your chat.", ParseMode.MARKDOWN)),

				InlineQueryResultArticle(
	        		id=uuid4(),
	        		title=("See the top cryptocurrencies"),
	        		thumb_url="https://imgur.com/g6YajTp.png",
	        		description=('"top"'),
	        		input_message_content=InputTextMessageContent("Type `top` " \
	        			+ "to see the top 50 cryptocurrencies, ranked by " \
	        			+ "their market capitalization. If you'd like to see " \
	        			+ "a specific number of cryptocurrencies, you can type " \
	        			+ "`top x` (where x ≤ 50) – so typing `top 20` will display " \
	        			+ "the top 20 cryptocurrencies.", ParseMode.MARKDOWN)),

				InlineQueryResultArticle(
	        		id=uuid4(),
	        		title=("See real-time trading prices on GDAX"),
	        		thumb_url="https://imgur.com/Eyh7KSb.png",
	        		description='"gdax"',
	        		input_message_content=InputTextMessageContent("Need more up-to-the-minute " \
	        		+ "prices than the standard cryptocurrency lookup? Cryptora can retrieve " \
	        		+ "the prices of bitcoin, litecoin, and ethereum on GDAX. Just type " \
	        		+ "`gdax` to get the prices in-line.", ParseMode.MARKDOWN)),

				InlineQueryResultArticle(
	        		id=uuid4(),
	        		title=("See global stats"),
	        		thumb_url="https://imgur.com/MyjXCmb.png",
	        		description='"global"',
	        		input_message_content=InputTextMessageContent("Type 'global' to" \
	        			+ "see a variety of up-to-the-minute global statistics." ,\
	        			 ParseMode.MARKDOWN)),

				InlineQueryResultArticle(
	        		id=uuid4(),
	        		title=("Compare multiple cryptocurrencies"),
	        		thumb_url="https://imgur.com/Gbnrtod.png",
	        		description='"btc, ltc, eth, dash, iota, ripple"',
	        		input_message_content=InputTextMessageContent("You can " \
	        		+ "search for multiple cryptocurrencies in a single "\
	        		+ "query by typing a selection of cryptocurrencies " \
	        		+ "(either their name, their symbol, or you can even " \
	        		+ "mix it up), separated by commas. For example, you " \
	        		+ "can type `btc, ethereum, omg, xrb, monero, ripple` to send the " \
	        		+ "prices, market capitalizations, or percent change " \
	        		+ "values of Bitcoin, Ethereum, OmiseGO, RaiBlocks, " \
	        		+ "Monero, and Ripple in one message.", ParseMode.MARKDOWN)),

				]

	# Cryptocurrency information
	else:

		if "," in query:

			try:
				results = generate_multi_currency_list(query)
			except:
				bot.answerInlineQuery(update.inline_query.id, results=[], \
					switch_pm_text='Invalid currencies entered. Please try again.', \
					switch_pm_parameter='do_something')

		else:

			coin = Coin(query, None, False)
			if coin.name == "None":
				bot.answerInlineQuery(update.inline_query.id, results=[], \
					switch_pm_text='No cryptocurrency found. Please try again.', \
					switch_pm_parameter='do_something')

			results = [
	    		# Summary
	    		InlineQueryResultArticle(
	            	id=uuid4(),
	            	title=(coin.name + " (" + coin.symbol + ")"),
	            	description="#" + coin.rank + " out of " + str(len(coin.data)),
	            	thumb_url='https://files.coinmarketcap.com/static/img/coins/128x128/' \
	            	+ coin.id + '.png',
	            	input_message_content=InputTextMessageContent(coin.summary, \
	            		ParseMode.MARKDOWN)),

	    		# USD Price
	    		InlineQueryResultArticle(
	        		id=uuid4(),
	        		title=("Price"),
	        		description="$" + coin.price_USD,
	        		thumb_url="https://imgur.com/7RCGCoc.png",
	        		input_message_content=InputTextMessageContent("1 " + coin.symbol + " = $" \
	        			+ coin.price_USD)),

	    		# Market Capitalization (USD)
	        	InlineQueryResultArticle(
	            	id=uuid4(),
	            	title=("Market Capitalization"),
	            	description="$" + coin.marketCap,
	            	thumb_url="https://i.imgur.com/UMczLVP.png",
	            	input_message_content=InputTextMessageContent("Market Capitalization of " \
	            		+ coin.name + " (" + coin.symbol + ")" + ": $" + coin.marketCap)),

	        	# Circulating Supply 
	        	InlineQueryResultArticle(
	            	id=uuid4(),
	            	title=("Circulating Supply"),
	            	description=coin.supply + " " + coin.symbol,
	            	thumb_url=("https://i.imgur.com/vXAN23U.png"),
	            	input_message_content=InputTextMessageContent("Circulating Supply of " \
	            		+ coin.name + " (" + coin.symbol + ")" + ": " + coin.supply + " " \
	            		+ coin.symbol)),

	        	# 24 Hour Percent Change
	        	InlineQueryResultArticle(
	            	id=uuid4(),
	            	title=("Percent Change (24 hours)"),
	            	description=coin.percentChange + "%",
	            	thumb_url=("https://imgur.com/iAoXFQc.png"),
	            	input_message_content=InputTextMessageContent("24 Hour Change in " \
	            		+ coin.name + " (" + coin.symbol + ")" + " Price: " + coin.percentChange \
	            		+ "%"))
        ]

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
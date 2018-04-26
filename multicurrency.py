from coin import *
from decimal import Decimal
from telegram import InlineQueryResultArticle, ParseMode,InputTextMessageContent
from telegram.ext import Updater, InlineQueryHandler, CommandHandler
from uuid import uuid4
import requests
from collections import OrderedDict

# Functions specifically for multi-currency search.

def convert_list_to_names(query):

	JSON_API_URL = 'https://api.coinmarketcap.com/v1/ticker/?limit=10000'

	currencyList = query.replace(", ", ",")
	currencyList = currencyList.split(",")

	data = requests.get(JSON_API_URL).json()
	newList = []

	for x in range (0, len(currencyList)):
		for y in range (0, len(data)):
			if currencyList[x].lower() == data[y]['name'].lower() \
			or currencyList[x].lower() == data[y]['symbol'].lower():
				newList.append(data[y]['name'])

	return list(OrderedDict.fromkeys(newList))


def get_prices(currencyList, data):

	prices = [None] * len(currencyList)

	for x in range (0, len(currencyList)):
		for y in range (0, len(data)):
			if currencyList[x] == data[y]['name']:
				if float(data[y]['price_usd']) < 1.00:
					price = str(data[y]['price_usd'])
					prices[x] = price
				else:
					price = Decimal((data[y]['price_usd'])).\
					quantize(Decimal('1.00'), rounding = 'ROUND_HALF_DOWN')
					price = str("{:,}".format(price))
					prices[x] = price

	allPrices = "***Selected Cryptocurrency Prices*** \n\n"

	for x in range (0, len(currencyList)):

		allPrices += "***" + currencyList[x] + ":*** $" + str(prices[x]) + "\n"

	return allPrices 

def get_market_capitalizations(currencyList, data):

	marketCaps = [None] * len(currencyList)

	for x in range (0, len(currencyList)):
		for y in range (0, len(data)):
			if currencyList[x] == data[y]['name']:
				cap = Decimal((data[y]['market_cap_usd'])).\
				quantize(Decimal('1.00'), rounding = 'ROUND_HALF_DOWN')
				cap = str("{:,}".format(cap))
				marketCaps[x] = cap

	allCaps = "***Selected Cryptocurrency Market Capitalizations*** \n\n"

	for x in range (0, len(currencyList)):

		allCaps += "***" + currencyList[x] + ":*** $" + str(marketCaps[x]) + "\n"

	return allCaps 

def get_percent_changes(currencyList, data):

	percentChanges = [None] * len(currencyList)

	for x in range (0, len(currencyList)):
		for y in range (0, len(data)):
			if currencyList[x] == data[y]['name']:
				change = Decimal((data[y]['percent_change_24h'])).\
				quantize(Decimal('1.00'), rounding = 'ROUND_HALF_DOWN')
				change = str("{:,}".format(change))
				percentChanges[x] = change

	allPercentChanges = "***Selected Cryptocurrency 24 Hour Percent Change Values*** \n\n"

	for x in range (0, len(currencyList)):

		allPercentChanges += "***" + currencyList[x] + ":*** " + str(percentChanges[x]) + "% \n"

	return allPercentChanges 

def generate_multi_currency_list(query):

	data = requests.get('https://api.coinmarketcap.com/v1/ticker/?limit=10000').json()

	if query.endswith(","):
		query = query[:-1]

	currencyList = convert_list_to_names(query)

	prices = get_prices(currencyList, data)
	marketCaps = get_market_capitalizations(currencyList, data)
	percentChanges = get_percent_changes(currencyList, data)

	if currencyList:

		results = [
			InlineQueryResultArticle(
	    		id=uuid4(),
	    		title=('Prices'),
	    		description='Tap to send.',
	    		thumb_url="https://imgur.com/7RCGCoc.png",
	    		input_message_content=InputTextMessageContent(prices, ParseMode.MARKDOWN)),

			InlineQueryResultArticle(
	    		id=uuid4(),
	    		title=('Market Capitalizations'),
	    		description='Tap to send.',
				thumb_url="https://i.imgur.com/UMczLVP.png",
	    		input_message_content=InputTextMessageContent(marketCaps, ParseMode.MARKDOWN)),

			InlineQueryResultArticle(
	    		id=uuid4(),
	    		title=('Percent Change Values'),
	    		description='Tap to send.',
	    		thumb_url=("https://imgur.com/iAoXFQc.png"),
	    		input_message_content=InputTextMessageContent(percentChanges, ParseMode.MARKDOWN)),
		]

	if len(currencyList) > 10:
		length = 10
	else:
		length = len(currencyList)

	for x in range (0, length):

		listEntry = Coin(currencyList[x], None, False)
		results.append(

			InlineQueryResultArticle(
				id=uuid4(),
				description=("$" + listEntry.price_USD),
				thumb_url='https://files.coinmarketcap.com/static/img/coins/' \
				+ '200x200/' + listEntry.id + '.png',
				title=(listEntry.name),
				input_message_content=InputTextMessageContent(listEntry.summary, \
					ParseMode.MARKDOWN)),
			)

	return results
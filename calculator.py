# -*- coding: utf-8 -*-

# Cryptora - Public Repository
# Provides conversion functionality between a cryptocurrency and U.S. dollars.

import requests
from decimal import Decimal
from coin import *
from telegram import InlineQueryResultArticle, ParseMode,InputTextMessageContent
from uuid import uuid4

def crypto_calculator(query, reverse):

	# Parse the query by splitting the spring and reconstructing it to separate the numerical value
	# from the cryptocurrency name/symbol
	
	queryArr = query.split(" ")
	currency = ""

	for x in range (1, len(queryArr)):
		currency += queryArr[x] + " "

	# Generate a Coin object.
	currency = currency[:-1]
	coin = Coin(currency, None)
	
	if not coin.exists:
		return []

	# Remove the commas from the already formatted value.
	price = coin.price_USD.replace(",", "")
	inputValue = queryArr[0]

	title = ""
	description = ""
	messageContent = ""

	# Reverse crypto calculator specific code.
	if reverse:
		inputValue = inputValue[1:]
		value = format_monetary_value(float(inputValue) / float(price), True)

		title = "Convert $" + inputValue + " to " + coin.symbol
		description = "Approximately " + value + " " + coin.symbol
		messageContent = "$" + inputValue + u" \u2248 " + value + " " + coin.symbol

	# Forward crypto calculator functionality.
	else:
		value = format_monetary_value(float(price) * float(inputValue), True)

		title = "Convert " + inputValue + " " + coin.symbol + " to USD"
		description = "Approximately $" + value
		messageContent = inputValue + " " + coin.symbol + u" \u2248 $" + value

	results = [
		InlineQueryResultArticle(
			id=uuid4(),
			thumb_url='https://s2.coinmarketcap.com/static/img/coins/' \
			+ '200x200/' + str(coin.ID) + '.png',
			title=title,
			description=description,
			input_message_content=InputTextMessageContent(messageContent))
	]

	return results
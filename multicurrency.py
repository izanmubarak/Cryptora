# Cryptora - Public Repository
''' These functions provide the functionality for Cryptora's multi-currency search functionality. Users
can type in a list of currencies (such as "btc, ltc, eth, dash") and receive an inline list that shows the price of each
coin, with the option to send all of the coins' prices, market capitalizations, and percent changes. '''

from coin import *
from retrieve_tokens import *
from decimal import Decimal
from telegram import InlineQueryResultArticle, ParseMode,InputTextMessageContent
from telegram.ext import Updater, InlineQueryHandler, CommandHandler
from uuid import uuid4
import requests
from collections import OrderedDict

# Create a list that holds Coin objects, with each Coin object corresponding to the entered cryptocurrency.
def initialize_multicurrency_query(query):

	token = get_token(True)
	coinMap = (requests.get('https://pro-api.coinmarketcap.com/v1/cryptocurrency/map?CMC_PRO_API_KEY=' + token).json())["data"]
	dataURL = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?CMC_PRO_API_KEY=' + token + "&id="

	# Parse the query, creating a list of strings that holds each individual entered cryptocurrency.	
	if query.endswith(","):
		query = query[:-1]
	if query.startswith(","):
		query = query[1:]

	currencyList = query.replace(", ", ",")
	currencyList = currencyList.split(",")

	coins = []

	# Replace the list of coin names with their IDs.
	for i in range (0, len(currencyList)):
		for j in range (0, len(coinMap)):
			if currencyList[i].lower() == coinMap[j]['name'].lower() or currencyList[i].upper() == coinMap[j]['symbol']:
				currencyList[i] = str(coinMap[j]['id'])

	# Generate the JSON file with all the requested currencies.
	for i in range (0, len(currencyList)):
		dataURL += currencyList[i] + ","

	# Remove the last comma from the URL and download the data
	dataURL = dataURL[:-1]
	data = requests.get(dataURL).json()["data"]

	# Generate a Coin object for each entered cryptocurrency and add it to a list of Coin objects.
	for i in range (0, len(currencyList)):
		coin = Coin(None, data[currencyList[i]])

		# Filter out invalid entries using the "exists" variable.
		if coin.exists:
			coins.append(coin)

	return coins

# Create the list of options that is displayed to the user when they type a multicurrency query.
def generate_multi_currency_list(query):

	# Build the message that is sent when the user chooses to send the list.
	coins = initialize_multicurrency_query(query)

	prices = "***Selected Cryptocurrency Prices***\n\n"
	capitalizations = "***Selected Cryptocurrency Market Capitalizations***\n\n"
	changes = "***Selected Cryptocurrency 24 Hour Percent Change Values***\n\n"

	for x in range (0, len(coins)):

		prices += "***" + coins[x].name + ":*** $" + coins[x].price_USD + "\n"
		capitalizations += "***" + coins[x].name + ":*** $" + coins[x].marketCap + "\n"
		changes += "***" + coins[x].name + ":*** " + coins[x].percentChange + "%\n"

	# Add the "Prices", "Market Capitalizations", and "Percent Change Values" options that are displayed at the top
	if coins:

		results = [

			# Prices
			InlineQueryResultArticle(
	    		id=uuid4(),
	    		title=('Prices'),
	    		description='Tap to send.',
	    		thumb_url="https://imgur.com/7RCGCoc.png",
	    		input_message_content=InputTextMessageContent(prices, ParseMode.MARKDOWN)),

			# Market Capitalizations
			InlineQueryResultArticle(
	    		id=uuid4(),
	    		title=('Market Capitalizations'),
	    		description='Tap to send.',
				thumb_url="https://i.imgur.com/UMczLVP.png",
	    		input_message_content=InputTextMessageContent(capitalizations, ParseMode.MARKDOWN)),

			# Percent Change Values
			InlineQueryResultArticle(
	    		id=uuid4(),
	    		title=('Percent Change Values'),
	    		description='Tap to send.',
	    		thumb_url=("https://imgur.com/iAoXFQc.png"),
	    		input_message_content=InputTextMessageContent(changes, ParseMode.MARKDOWN)),
		]

	# Cryptora allows users to put up to 10 coins in a multi-currency query.
	if len(coins) > 10:
		length = 10
	else:
		length = len(coins)

	# Add each individual coin to the list.
	for x in range (0, length):

		results.append(

			InlineQueryResultArticle(
				id=uuid4(),
				description=("$" + coins[x].price_USD),
				thumb_url=coins[x].imageURL,
				title=(coins[x].name),
				input_message_content=InputTextMessageContent(coins[x].summary, \
					ParseMode.MARKDOWN)),
		)

	return results
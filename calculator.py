import requests
from decimal import Decimal
from coin import *
from telegram import InlineQueryResultArticle, ParseMode,InputTextMessageContent
from uuid import uuid4

JSON_API_URL = 'https://api.coinmarketcap.com/v1/ticker/?limit=10000'

class CryptoCalculatorInstance:

	def __init__(self, query, symbol, reverse, coinPrice, dollarValue):

		if reverse == False:	
			self.inputValue = str((query.split(" "))[0])
			self.calculatedValue = str(self.calculate_price(query, symbol, self.inputValue))

		else:
			self.calculatedValue = self.calculate_crypto_quantity(symbol, \
				coinPrice, dollarValue)

	# CryptoCalculator specific function.

	def calculate_price(self, query, symbol, userInput):

		JSON_DATA = requests.get(JSON_API_URL).json()

		for x in range (0, len(JSON_DATA)): 
			if symbol == JSON_DATA[x]['symbol']:
				inputPrice = float(JSON_DATA[x]['price_usd'])
				calculatedPrice = (float(userInput) * inputPrice)
				return str("{:,}".format(Decimal(calculatedPrice).\
					quantize(Decimal('1.00'), rounding = 'ROUND_HALF_DOWN')))

	# Reverse CryptoCalculator specific function.

	def calculate_crypto_quantity(self, symbol, coinPrice, dollarValue):

		return str(round((float(dollarValue) / float(coinPrice)), 6))


def generate_cryptoCalculator_result(query):

	userInputName = ""	
	for x in range (1, len(query.split(" "))):
		userInputName += query.split(" ")[x] + " "

	inputCoin = Coin((userInputName[:-1]).title(), None, False)
	instance = CryptoCalculatorInstance(query, inputCoin.symbol, \
		False, None, None)

	if inputCoin.name == "None":

		bot.answerInlineQuery(update.inline_query.id, results=[], \
			switch_pm_text='No cryptocurrency found. Please try again.', \
			switch_pm_parameter='do_something')

		return

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

	return results

def generate_reverseCryptoCalculator_result(query):

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

		return results

	except:

		bot.answerInlineQuery(update.inline_query.id, results=[], \
			switch_pm_text='No cryptocurrency found. Please try again.', \
			switch_pm_parameter='do_something')
# Cryptogram_functions.py
# Helper functions for Cryptogram.py. 

from Cryptogram import *

# This class defines a cryptocurrency. It stores all of the relevant data.

class Coin:

	def __init__(self, query, rank, noCommas):
		if rank == None:
			self.name = str(self.get_name(query))
		else:
			self.name = str(self.get_name(rank))

		self.rank = str(self.get_rank(self.name))
		self.id = str(self.get_id(self.name))

		if noCommas == False:
			self.price_USD = str(self.get_price(self.name, False))
		else:
			self.price_USD = str(self.get_price(self.name, True))

		self.marketCap = str(self.get_market_cap(self.name))
		self.supply = str(self.get_supply(self.name))
		self.percentChange = str(self.get_percent_change(self.name))
		self.symbol = str(self.get_symbol(self.name))
		self.summary = str(self.generate_summary(self.price_USD, self.marketCap, self.supply, self.percentChange, self.name, self.symbol))

	def get_rank(self, query):

		for x in range (0, len(JSON_DATA)):
			if query.upper() == JSON_DATA[x]['symbol'] or \
			query.lower() == JSON_DATA[x]['id'] or \
			query.title() == JSON_DATA[x]['name'] or \
			query == JSON_DATA[x]['rank']:
				return int(x)

	def get_name(self, query):

		# With this function, a user can type in the symbol or the name of the cryptocurrency in any case (lower or upper case), and this function will return the properly formatted name. 
	    
		for x in range (0, len(JSON_DATA)): 
			if query.upper() == JSON_DATA[x]['symbol'] or \
			query.lower() == JSON_DATA[x]['id'] or \
			query.title() == JSON_DATA[x]['name'] or \
			query == JSON_DATA[x]['rank']:
				return JSON_DATA[x]['name']

	def get_symbol(self, query):

		# This function will retrieve the cryptocurrency symbol for the chosen currency.

		for x in range (0, len(JSON_DATA)): 
			if query.upper() == JSON_DATA[x]['symbol'] or \
			query.lower() == JSON_DATA[x]['id'] or \
			query.title() == JSON_DATA[x]['name'] or \
			query == JSON_DATA[x]['rank']:
				return JSON_DATA[x]['symbol']

	def get_id(self, query):

		# Retrieves cryptocurrency ID on CoinMarketCap.

		for x in range (0, len(JSON_DATA)):
			if query.upper() == JSON_DATA[x]['symbol'] or \
			query.lower() == JSON_DATA[x]['id'] or \
			query.title() == JSON_DATA[x]['name'] or \
			query == JSON_DATA[x]['rank']:
				return JSON_DATA[x]['id']

	def get_price(self, query, noCommas):

		# This function retrieves and properly formats the chosen cryptocurrency's price. If the price of the coin is above $0.01, it automatically rounds to two decimal places. It also intelligently adds comma separators.

		for x in range (0, len(JSON_DATA)): 
			if query.upper() == JSON_DATA[x]['symbol'] or \
			query.lower() == JSON_DATA[x]['id'] or \
			query.title() == JSON_DATA[x]['name'] or \
			query == JSON_DATA[x]['rank']:

				if noCommas == True or float(JSON_DATA[x]['price_usd']) < 1.00:
					return JSON_DATA[x]['price_usd']
				else:
					price = Decimal((JSON_DATA[x]['price_usd'])).quantize(Decimal('1.00'), rounding = 'ROUND_HALF_DOWN')
					return str("{:,}".format(price))

	def get_market_cap(self, query):

		# This function retrieves and properly formats the chosen cryptocurrency's market capitalization. 

		for x in range (0, len(JSON_DATA)):
			if query.upper() == JSON_DATA[x]['symbol'] or \
			query.lower() == JSON_DATA[x]['id'] or \
			query.title() == JSON_DATA[x]['name'] or \
			query == JSON_DATA[x]['rank']:
				return str("{:,}".format(Decimal(float(JSON_DATA[x]['market_cap_usd']))))

	def get_supply(self, query):

		# Retrieves and properly formats chosen cryptocurrency's circulating supply count.

		for x in range (0, len(JSON_DATA)):
			if query.upper() == JSON_DATA[x]['symbol'] or \
			query.lower() == JSON_DATA[x]['id'] or \
			query.title() == JSON_DATA[x]['name'] or \
			query == JSON_DATA[x]['rank']:
				return "{:,}".format(Decimal(float(JSON_DATA[x]['available_supply'])))

	def get_percent_change(self, query):

		# Retrieves and properly formats chosen cryptocurrency's change in value in
		# the last 24 hours.

		for x in range (0, len(JSON_DATA)):
			if query.upper() == JSON_DATA[x]['symbol'] or \
			query.lower() == JSON_DATA[x]['id'] or \
			query.title() == JSON_DATA[x]['name'] or \
			query == JSON_DATA[x]['rank']:
				return JSON_DATA[x]['percent_change_24h']

	def generate_summary(self, price, cap, supplyValue, percentChange, name, symbol):

		# Returns a summary of the cryptocurrency.

		return ("***" + name + "***" + " (" + symbol + ")" + '\n \n' + '***Price***: $' + price + '\n' + '***Market Capitalization***: $' + cap + '\n' + '***Circulating Supply***: ' + supplyValue + " " + symbol + '\n' + '***24 Hour Percent Change***: ' + percentChange + "% \n")

class CryptoCalculatorInstance:

	def __init__(self, query, symbol, reverse, coinPrice, dollarValue):

		if reverse == False:	
			self.inputValue = str((query.split(" "))[0])
			self.calculatedValue = str(self.calculate_price(query, symbol))

		else:
			self.calculatedValue = self.calculate_crypto_quantity(symbol, coinPrice, dollarValue)

	# CryptoCalculator specific function.

	def calculate_price(self, query, symbol):

		userInputValue = (query.split(" "))[0]

		for x in range (0, len(JSON_DATA)): 
			if symbol == JSON_DATA[x]['symbol']:
				inputPrice = float(JSON_DATA[x]['price_usd'])
				calculatedPrice = (float(userInputValue) * inputPrice)
				return str("{:,}".format(Decimal(calculatedPrice).quantize(Decimal('1.00'), rounding = 'ROUND_HALF_DOWN')))

	# Reverse CryptoCalculator specific function.

	def calculate_crypto_quantity(self, symbol, coinPrice, dollarValue):

		return str("{:,}".format(Decimal(float(dollarValue) / float(coinPrice)).quantize(Decimal('1.00'), rounding = 'ROUND_HALF_DOWN')))
			
'''class NewsArticle:
# Class under construction, will be fully implemented following FeedParser integration.
	def __init__(self, query):
		self.title 
		self.subtitle
		self.URL
		self.thumbnailURL
		self.dayPublished
		self.monthPublished
		self.yearPublished'''

'''def get_image(URL):
		page = requests.get(URL)
		soup = BeautifulSoup(page.content, 'html.parser')
		unformattedLink = str((soup.find_all('div', class_="article-top-image-section"))).split(">")[0]
		return unformattedLink[69:][:-3]'''

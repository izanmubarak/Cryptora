# Cryptora_functions.py
# Helper functions for Cryptora.py. 

from app import *

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

		self.JSON_DATA = requests.get(JSON_API_URL).json()

		self.marketCap = str(self.get_market_cap(self.name))
		self.supply = str(self.get_supply(self.name))
		self.percentChange = str(self.get_percent_change(self.name))
		self.symbol = str(self.get_symbol(self.name))
		self.summary = str(self.generate_summary(self.price_USD, \
			self.marketCap, self.supply, self.percentChange, self.name, \
			self.symbol))

	def get_rank(self, query):

		for x in range (0, len(self.JSON_DATA)):
			if query.upper() == self.JSON_DATA[x]['symbol'] or \
			query.lower() == self.JSON_DATA[x]['id'] or \
			query.title() == self.JSON_DATA[x]['name'] or \
			query == self.JSON_DATA[x]['rank']:
				return int(x)

	def get_name(self, query):

		# With this function, a user can type in the symbol or the name of the 
		# cryptocurrency in any case (lower or upper case), and this function 
		# will return the properly formatted name. 
	    
		for x in range (0, len(self.JSON_DATA)): 
			if query.upper() == self.JSON_DATA[x]['symbol'] or \
			query.lower() == self.JSON_DATA[x]['id'] or \
			query.title() == self.JSON_DATA[x]['name'] or \
			query == self.JSON_DATA[x]['rank']:
				return self.JSON_DATA[x]['name']

	def get_symbol(self, query):

		# This function will retrieve the cryptocurrency symbol for the chosen
		# currency.

		for x in range (0, len(self.JSON_DATA)): 
			if query.upper() == self.JSON_DATA[x]['symbol'] or \
			query.lower() == self.JSON_DATA[x]['id'] or \
			query.title() == self.JSON_DATA[x]['name'] or \
			query == self.JSON_DATA[x]['rank']:
				return self.JSON_DATA[x]['symbol']

	def get_id(self, query):

		# Retrieves cryptocurrency ID on CoinMarketCap.

		for x in range (0, len(self.JSON_DATA)):
			if query.upper() == self.JSON_DATA[x]['symbol'] or \
			query.lower() == self.JSON_DATA[x]['id'] or \
			query.title() == self.JSON_DATA[x]['name'] or \
			query == self.JSON_DATA[x]['rank']:
				return self.JSON_DATA[x]['id']

	def get_price(self, query, noCommas):

		# This function retrieves and properly formats the chosen 
		# cryptocurrency's price. If the price of the coin is above $0.01, 
		# it automatically rounds to two decimal places. It also intelligently
		# adds comma separators.

		for x in range (0, len(self.JSON_DATA)): 
			if query.upper() == self.JSON_DATA[x]['symbol'] or \
			query.lower() == self.JSON_DATA[x]['id'] or \
			query.title() == self.JSON_DATA[x]['name'] or \
			query == self.JSON_DATA[x]['rank']:

				if noCommas == True or float(self.JSON_DATA[x]['price_usd']) < 1.00:
					return self.JSON_DATA[x]['price_usd']
				else:
					price = Decimal((self.JSON_DATA[x]['price_usd'])).\
					quantize(Decimal('1.00'), rounding = 'ROUND_HALF_DOWN')
					return str("{:,}".format(price))

	def get_market_cap(self, query):

		# This function retrieves and properly formats the chosen 
		# cryptocurrency's market capitalization. 

		for x in range (0, len(self.JSON_DATA)):
			if query.upper() == self.JSON_DATA[x]['symbol'] or \
			query.lower() == self.JSON_DATA[x]['id'] or \
			query.title() == self.JSON_DATA[x]['name'] or \
			query == self.JSON_DATA[x]['rank']:
				return str("{:,}".format(Decimal(\
					float(self.JSON_DATA[x]['market_cap_usd']))))

	def get_supply(self, query):

		# Retrieves and properly formats chosen cryptocurrency's circulating
		# supply count.

		for x in range (0, len(self.JSON_DATA)):
			if query.upper() == self.JSON_DATA[x]['symbol'] or \
			query.lower() == self.JSON_DATA[x]['id'] or \
			query.title() == self.JSON_DATA[x]['name'] or \
			query == self.JSON_DATA[x]['rank']:
				return "{:,}".format(Decimal(float(\
					self.JSON_DATA[x]['available_supply'])))

	def get_percent_change(self, query):

		# Retrieves and properly formats chosen cryptocurrency's change in
		# value in the last 24 hours.

		for x in range (0, len(self.JSON_DATA)):
			if query.upper() == self.JSON_DATA[x]['symbol'] or \
			query.lower() == self.JSON_DATA[x]['id'] or \
			query.title() == self.JSON_DATA[x]['name'] or \
			query == self.JSON_DATA[x]['rank']:
				return self.JSON_DATA[x]['percent_change_24h']

	def generate_summary(self, price, cap, supplyValue, percentChange, \
		name, symbol):

		# Returns a summary of the cryptocurrency.

		return ("***" + name + "***" + " (" + symbol + ")" + '\n \n' + \
			'***Price***: $' + price + '\n' + '***Market Capitalization***: $' \
			 + cap + '\n' + '***Circulating Supply***: ' + supplyValue + " " + \
			  symbol + '\n' + '***24 Hour Percent Change***: ' + \
			   percentChange + "% \n")

class CryptoCalculatorInstance:

	def __init__(self, query, symbol, reverse, coinPrice, dollarValue):

		if reverse == False:	
			self.inputValue = str((query.split(" "))[0])
			self.calculatedValue = str(self.calculate_price(query, symbol))

		else:
			self.calculatedValue = self.calculate_crypto_quantity(symbol, \
				coinPrice, dollarValue)

	# CryptoCalculator specific function.

	def calculate_price(self, query, symbol):

		userInputValue = (query.split(" "))[0]

		for x in range (0, len(self.JSON_DATA)): 
			if symbol == self.JSON_DATA[x]['symbol']:
				inputPrice = float(self.JSON_DATA[x]['price_usd'])
				calculatedPrice = (float(userInputValue) * inputPrice)
				return str("{:,}".format(Decimal(calculatedPrice).\
					quantize(Decimal('1.00'), rounding = 'ROUND_HALF_DOWN')))

	# Reverse CryptoCalculator specific function.

	def calculate_crypto_quantity(self, symbol, coinPrice, dollarValue):

		return str(round((float(dollarValue) / float(coinPrice)), 6))
			
class NewsArticle:

	def __init__(self, rank, feed):

		self.title = self.get_article_title(rank, feed)
		self.subtitle = self.get_article_subtitle(rank, feed)
		self.URL = self.get_article_URL(rank, feed)
		self.thumbnailURL = self.get_image(self.URL)
		
	def get_article_URL(self, rank, feed):

		return feed['entries'][rank]['link']

	def get_article_title(self, rank, feed):

		return feed['entries'][rank]['title']

	def get_article_subtitle(self, rank, feed):

		return feed['entries'][rank]['description']

	def get_image(self, URL):
		
		page = requests.get(URL)
		soup = BeautifulSoup(page.content, 'html.parser')
		unformattedLink = str((soup.find_all('div', \
			class_="article-top-image-section"))).split(">")[0]
		return unformattedLink[69:][:-3]

class PriceOnDay:

	def __init__(self, ID, day, month, year):

		self.day = str('%02d' % int(day))
		self.month = str('%02d' % int(month))
		self.year = year
		self.URL = 'https://coinmarketcap.com/currencies/' + ID + \
		 '/historical-data/?start=' + self.year + self.month + self.day \
		 + "&end=" + self.year + self.month + self.day

		self.page = requests.get(self.URL)
		self.soup = BeautifulSoup(self.page.content, 'html.parser')

		self.open = str(((self.soup.find_all('td'))[1]))[4:][:-5]
		self.low = str(((self.soup.find_all('td'))[3]))[4:][:-5]
		self.marketCap = str(((self.soup.find_all('td'))[5]))[4:][:-5]
		self.high = str(((self.soup.find_all('td'))[2]))[4:][:-5]
		self.close = str(((self.soup.find_all('td'))[4]))[4:][:-5]


# Historical Pricing specific functions. Not in their own class.

def get_coin_word_count(string):

	string = string.title()
	string = string.split(" ")
	for x in range (0, len(string)):
		if "/" in string[x] \
		or string[x] == "January" \
		or string[x] == "February" \
		or string[x] == "March" \
		or string[x] == "April" \
		or string[x] == "May" \
		or string[x] == "June" \
		or string[x] == "July" \
		or string[x] == "August" \
		or string[x] == "September" \
		or string[x] == "October" \
		or string[x] == "November" \
		or string[x] == "December":
			return x

def get_coin_name_from_historical_query(wordCount, query):
	
	splitQuery = query.split(" ")

	name = ""
	for x in range (0, wordCount):
		name += splitQuery[x] + " "

	return name[:-1]

def convert_month_number_to_name(string):

	monthNumber = int(string)
	months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', \
	'August', 'September', 'October', 'November', 'December']

	return months[monthNumber - 1]

def determine_if_date_in_string(string):

	dates = list(datefinder.find_dates(string))
	if len(dates) > 0:
		return True
	else:
		return False

def get_day(string, dateInString):

	if dateInString == True:
		dates = list(datefinder.find_dates(string))
		return dates[0].day

def get_month(string, dateInString):

	if dateInString == True:
		dates = list(datefinder.find_dates(string))
		return dates[0].month

def get_year(string, dateInString):

	if dateInString == True:
		dates = list(datefinder.find_dates(string))
		return dates[0].year

# Function for GDAX price retrieval.

def get_GDAX_price(string):

	public_client = gdax.PublicClient()

	if string == "bitcoin":

		price = public_client.get_product_ticker(product_id='BTC-USD')['price']
		decimalizedPrice = Decimal(price).quantize(Decimal('1.00'), \
			rounding = 'ROUND_HALF_DOWN')
		priceWithCommas = str("{:,}".format(decimalizedPrice))

	elif string == "litecoin":

		price = public_client.get_product_ticker(product_id='LTC-USD')['price']
		decimalizedPrice = Decimal(price).quantize(Decimal('1.00'), \
			rounding = 'ROUND_HALF_DOWN')
		priceWithCommas = str("{:,}".format(decimalizedPrice))

	elif string == "ethereum":

		price = public_client.get_product_ticker(product_id='ETH-USD')['price']
		decimalizedPrice = Decimal(price).quantize(Decimal('1.00'), \
			rounding = 'ROUND_HALF_DOWN')
		priceWithCommas = str("{:,}".format(decimalizedPrice))

	elif string == "bitcoin_cash":

		price = public_client.get_product_ticker(product_id='BCH-USD')['price']
		decimalizedPrice = Decimal(price).quantize(Decimal('1.00'), \
			rounding = 'ROUND_HALF_DOWN')
		priceWithCommas = str("{:,}".format(decimalizedPrice))

	return priceWithCommas
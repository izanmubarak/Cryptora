from app import *

class Coin:

	def __init__(self, query, rank, noCommas):

		self.data = requests.get('https://api.coinmarketcap.com/v1/ticker/?limit=10000', headers={'Cache-Control': 'no-cache'}).json()

		if rank == None:
			self.name = str(self.get_name(query, self.data))
		else:
			self.name = str(self.get_name(rank, self.data))

		self.rank = str(self.get_rank(self.name, self.data))
		self.id = str(self.get_id(self.name, self.data))

		if noCommas == False:
			self.price_USD = str(self.get_price(self.name, False, self.data))
		else:
			self.price_USD = str(self.get_price(self.name, True, self.data))

		self.marketCap = str(self.get_market_cap(self.name, self.data))
		self.supply = str(self.get_supply(self.name, self.data))
		self.percentChange = str(self.get_percent_change(self.name, self.data))
		self.symbol = str(self.get_symbol(self.name, self.data))
		self.summary = str(self.generate_summary(self.price_USD, \
			self.marketCap, self.supply, self.percentChange, self.name, \
			self.symbol, self.rank, self.data))

	def get_rank(self, query, data):

		for x in range (0, len(data)):
			if query.upper() == data[x]['symbol'] or \
			query.lower() == data[x]['id'] or \
			query.lower() == (data[x]['name']).lower() or \
			query == data[x]['rank']:
				return int(x) + 1

	def get_name(self, query, data):

		# With this function, a user can type in the symbol or the name of the 
		# cryptocurrency in any case (lower or upper case), and this function 
		# will return the properly formatted name. 
	    
		for x in range (0, len(data)): 
			if query.upper() == data[x]['symbol'] or \
			query.lower() == data[x]['id'] or \
			query.lower() == (data[x]['name']).lower() or \
			query == data[x]['rank']:
				return data[x]['name']

	def get_symbol(self, query, data):

		# This function will retrieve the cryptocurrency symbol for the chosen
		# currency.

		for x in range (0, len(data)): 
			if query.upper() == data[x]['symbol'] or \
			query.lower() == data[x]['id'] or \
			query.lower() == (data[x]['name']).lower() or \
			query == data[x]['rank']:
				return data[x]['symbol']

	def get_id(self, query, data):

		# Retrieves cryptocurrency ID on CoinMarketCap.

		for x in range (0, len(data)):
			if query.upper() == data[x]['symbol'] or \
			query.lower() == data[x]['id'] or \
			query.lower() == (data[x]['name']).lower() or \
			query == data[x]['rank']:
				return data[x]['id']

	def get_price(self, query, noCommas, data):

		# This function retrieves and properly formats the chosen 
		# cryptocurrency's price. If the price of the coin is above $0.01, 
		# it automatically rounds to two decimal places. It also intelligently
		# adds comma separators.

		for x in range (0, len(data)): 
			if query.upper() == data[x]['symbol'] or \
			query.lower() == data[x]['id'] or \
			query.lower() == (data[x]['name']).lower() or \
			query == data[x]['rank']:

				if noCommas == True or float(data[x]['price_usd']) < 1.00:
					return data[x]['price_usd']
				else:
					price = Decimal((data[x]['price_usd'])).\
					quantize(Decimal('1.00'), rounding = 'ROUND_HALF_DOWN')
					return str("{:,}".format(price))

	def get_market_cap(self, query, data):

		# This function retrieves and properly formats the chosen 
		# cryptocurrency's market capitalization. 

		for x in range (0, len(data)):
			if query.upper() == data[x]['symbol'] or \
			query.lower() == data[x]['id'] or \
			query.lower() == (data[x]['name']).lower() or \
			query == data[x]['rank']:
				return str("{:,}".format(Decimal(\
					float(data[x]['market_cap_usd']))))

	def get_supply(self, query, data):

		# Retrieves and properly formats chosen cryptocurrency's circulating
		# supply count.

		for x in range (0, len(data)):
			if query.upper() == data[x]['symbol'] or \
			query.lower() == data[x]['id'] or \
			query.lower() == (data[x]['name']).lower() or \
			query == data[x]['rank']:
				return "{:,}".format(Decimal(float(\
					data[x]['available_supply'])))

	def get_percent_change(self, query, data):

		# Retrieves and properly formats chosen cryptocurrency's change in
		# value in the last 24 hours.

		for x in range (0, len(data)):
			if query.upper() == data[x]['symbol'] or \
			query.lower() == data[x]['id'] or \
			query.lower() == (data[x]['name']).lower() or \
			query == data[x]['rank']:
				return data[x]['percent_change_24h']

	def generate_summary(self, price, cap, supplyValue, percentChange, \
		name, symbol, rank, data):

		# Returns a summary of the cryptocurrency.

		return ("***" + name + "***" + " (" + symbol + ")" + '\n \n' + \

			'***Rank***: #' + str(rank) + " out of " + str(len(data)) + "\n" + \
			'***Price***: $' + price + '\n' + '***Market Capitalization***: $' \
			 + cap + '\n' + '***Circulating Supply***: ' + supplyValue + " " + \
			  symbol + '\n' + '***24 Hour Percent Change***: ' + \
			   percentChange + "% \n")

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

		self.open = self.get_data(str(((self.soup.find_all('td'))[1]))[43:][:-5])
		self.low = self.get_data(str(((self.soup.find_all('td'))[3]))[43:][:-5])
		self.marketCap = self.get_market_cap(str(((self.soup.find_all('td'))[6]))[49:][:-5])
		self.high = self.get_data(str(((self.soup.find_all('td'))[2]))[43:][:-5])
		self.close = self.get_data(str(((self.soup.find_all('td'))[4]))[43:][:-5])

	def get_data(self, string):

		listt = string.split('">')
		return str("{:,}".format(Decimal(listt[1]).\
					quantize(Decimal('1.00'), rounding = 'ROUND_HALF_DOWN')))

	def get_market_cap(self, string):

		listt = string.split('">')
		return str(listt[1])

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

class GeneralStats:

	def __init__(self):

		self.URL = 'https://api.coinmarketcap.com/v1/global/'
		self.data = requests.get(self.URL).json()

		self.activeCryptoCount = self.get_active_cryptos(self.data)
		self.dominanceBTC = self.get_BTC_dominance(self.data)
		self.marketCount = self.get_market_count(self.data)
		self.volume24h = self.get_volume_24h(self.data)
		self.marketCap = self.get_market_cap(self.data)

	def get_market_cap(self, data):

		unformatted = data['total_market_cap_usd']
		cap = Decimal(unformatted).quantize(Decimal('1.00'), rounding = 'ROUND_HALF_DOWN')
		cap = str("{:,}".format(cap))
		return cap

	def get_BTC_dominance(self, data):
 
		dominance = Decimal(data['bitcoin_percentage_of_market_cap']).quantize(Decimal('1.00'), rounding = 'ROUND_HALF_DOWN')
		dominance = str("{:,}".format(dominance))
		return dominance

	def get_active_cryptos(self, data):
 
		return data['active_currencies']

	def get_market_count(self, data):

		return data['active_markets']

	def get_volume_24h(self, data):

		volume = Decimal(data['total_24h_volume_usd']).quantize(Decimal('1.00'), rounding = 'ROUND_HALF_DOWN')
		volume = str("{:,}".format(volume))
		return volume

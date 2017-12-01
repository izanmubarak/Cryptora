# Cryptogram_functions.py
# Helper functions for Cryptogram.py. 

from Cryptogram import *

# This class defines a cryptocurrency. It stores all of the relevant data.

class Coin:
	def __init__(self, query, rank):
		if rank == None:
			self.name = str(convertToFullName(query))
		else:
			self.name = str(convertToFullName(rank))

		self.rank = str(retrieveRank(self.name))
		self.id = str(retrieveCryptoID(self.name))
		self.price_USD = str(retrieveAndFormatCryptoPrice(self.name))
		self.marketCap = str(retrieveAndFormatCryptoMarketCap(self.name))
		self.supply = str(retrieveAndFormatCirculatingSupply(self.name))
		self.percentChange = str(retrieveAndFormat24HourPercentChange(self.name))
		self.symbol = str(retrieveCryptoSymbol(self.name))
		self.summary = str(formattedSummary(self.price_USD, self.marketCap, self.supply, self.percentChange, self.name, self.symbol))

class CryptoCalculatorInstance:
	def __init__(self, query):
		self.input = str(retrieveConvertQueryUserInputValue(query))
		self.name = str(retrieveConvertQueryCryptoName(query))
		self.symbol = str(retrieveCryptoSymbol(self.name))
		self.id = str(retrieveCryptoID(self.name))
		self.price_USD = str(calculatePrice(query, self.symbol))

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
		if str(query).upper() == JSON_DATA[x]['symbol'] or \
		(str(query).lower() == JSON_DATA[x]['id']) or \
		(str(query).title() == JSON_DATA[x]['name']) or \
		(str(query) == JSON_DATA[x]['rank']):
			fullCryptoCurrencyName = JSON_DATA[x]['name']
			return fullCryptoCurrencyName

def retrieveCryptoSymbol(query):

	# This function will retrieve the cryptocurrency symbol for the chosen 
	# currency.

	for x in range (0, 1314): 
		if query.upper() == JSON_DATA[x]['symbol'] or \
		query.lower() == JSON_DATA[x]['id'] or \
		query.title() == JSON_DATA[x]['name']:
			return JSON_DATA[x]['symbol']

def retrieveCryptoID(query):

	# Retrieves cryptocurrency ID on CoinMarketCap.

	for x in range (0, 1314):
		if query.upper() == JSON_DATA[x]['symbol'] or \
		 query.lower() == JSON_DATA[x]['id'] or \
		 query.title() == JSON_DATA[x]['name'] or \
		 (query == JSON_DATA[x]['rank']):
			return JSON_DATA[x]['id']


def retrieveAndFormatCryptoPrice(query):

	# This function retrieves and properly formats the chosen cryptocurrency's
	# price. If the price of the coin is above $0.01, it automatically rounds. 
	# to two decimal places. It also intelligently adds comma separators.

	for x in range (0, 1314): 
		if query.upper() == JSON_DATA[x]['symbol'] or (query.lower() == JSON_DATA[x]['id']) or (query.title() == JSON_DATA[x]['name']) or query == JSON_DATA[x]['rank']:
			unformattedCryptoPrice = float(JSON_DATA[x]['price_usd'])
			if unformattedCryptoPrice > 0.01:
				unformattedCryptoPrice = round(unformattedCryptoPrice, 2)
			formattedCryptoPrice = "{:,}".format(unformattedCryptoPrice)
			return str(formattedCryptoPrice)

def retrieveAndFormatCryptoMarketCap(query):

	# This function retrieves and properly formats the chosen cryptocurrency's
	# market capitalization. 

	for x in range (0, 1314):
		if query.upper() == JSON_DATA[x]['symbol'] or \
		(query.lower() == JSON_DATA[x]['id']) or \
		(query.title() == JSON_DATA[x]['name']):
			unformattedMarketCap = float((JSON_DATA[x]['market_cap_usd']))
			unformattedMarketCap = Decimal(unformattedMarketCap)
			formattedMarketCap = "{:,}".format(unformattedMarketCap)
			return formattedMarketCap

def retrieveAndFormatCirculatingSupply(query):

	# Retrieves and properly formats chosen cryptocurrency's circulating supply 
	# count.

	for x in range (0, 1314):
		if query.upper() == JSON_DATA[x]['symbol'] or \
		(query.lower() == JSON_DATA[x]['id']) or \
		(query.title() == JSON_DATA[x]['name']):
			unformattedSupplyValue = float((JSON_DATA[x]['available_supply']))
			unformattedSupplyValue = Decimal(unformattedSupplyValue)
			formattedSupplyValue = "{:,}".format(unformattedSupplyValue)
			return formattedSupplyValue

def retrieveAndFormat24HourPercentChange(query):

	# Retrieves and properly formats chosen cryptocurrency's change in value in
	# the last 24 hours.

	for x in range (0, 1314):
		if query.upper() == JSON_DATA[x]['symbol'] or \
		(query.lower() == JSON_DATA[x]['id']) or \
		(query.title() == JSON_DATA[x]['name']):
			formattedPercentChange = JSON_DATA[x]['percent_change_24h']
			return formattedPercentChange

def formattedSummary(price, cap, supplyValue, percentChange, name, symbol):

	# Returns a summary of the cryptocurrency.

	summary = "***" + name + "***" + " (" + symbol + ")" + '\n \n' + '***Price***: $' + price + '\n' + '***Market Capitalization***: $' + cap + '\n' + '***Circulating Supply***: ' + supplyValue + " " + symbol + '\n' + '***24 Hour Percent Change***: ' + percentChange + "% \n"
	return summary

def calculatePrice(query, convertQuerySymbol):

	userInputValue = float(re.findall(r"[-+]?\d*\.\d+|\d+", query)[0])
	
	for x in range (0, 1314): 
		if convertQuerySymbol == JSON_DATA[x]['symbol']:
			userInputCryptoPrice = float(JSON_DATA[x]['price_usd'])
			calculatedPrice = (userInputValue * userInputCryptoPrice)
			formattedPrice = round(calculatedPrice, 2)
			formattedPrice = "{:,}".format(formattedPrice)
			return formattedPrice

def retrieveConvertQueryUserInputValue(query):

	return (re.findall(r"[-+]?\d*\.\d+|\d+", query)[0])

def retrieveConvertQueryCryptoName(query):

	convertQueryName = ""
	splitQueryLength = len(query.split(" "))
	for x in range (1, splitQueryLength):
		convertQueryName += query.split(" ")[x] + " "
	return convertQueryName[:-1]

def scrapeArticleTitle(order):

	page = requests.get(NEWS_URL)
	soup = BeautifulSoup(page.content, 'html.parser')
	unformattedTitle = str(soup.find_all('title')[order])
	title = unformattedTitle[7:][:-8]

	return title

# Deprecated code. Faster solution (FeedParser) incoming.

def scrapeArticleURL(order):

	page = requests.get(NEWS_URL)
	soup = BeautifulSoup(page.content, 'html.parser')
	unformattedLink = ((str(soup.find_all('item')[order])).split(">"))[4]
	return unformattedLink[:-11]

def scrapeArticleSubtitle(order):

	page = requests.get(NEWS_URL)
	soup = BeautifulSoup(page.content, 'html.parser')
	unformattedDescription = str(soup.find_all('description')[order])
	subtitle = unformattedDescription[22:][:-17]
	return subtitle

def scrapeArticleImage(URL):

	page = requests.get(URL)
	soup = BeautifulSoup(page.content, 'html.parser')

	unformattedLink = str((soup.find_all('div', class_="article-top-image-section"))).split(">")[0]

	return unformattedLink[69:][:-3]

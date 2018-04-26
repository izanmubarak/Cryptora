import datefinder
import dateparser
from coin import *
from bs4 import BeautifulSoup
import requests
from decimal import Decimal
from telegram import InlineQueryResultArticle, ParseMode,InputTextMessageContent
from telegram.ext import Updater, InlineQueryHandler, CommandHandler
from uuid import uuid4

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

def get_historical_pricing_list(query, bot, update, dateInString):

	results = []

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

		return results

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

			return results

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

			return results

		except:
			bot.answerInlineQuery(update.inline_query.id, results=[], \
				switch_pm_text='Invalid date entered. Please try again.', \
				switch_pm_parameter='do_something')

	return results

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
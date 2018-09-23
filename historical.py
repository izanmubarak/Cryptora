import datefinder
import dateparser
from bs4 import BeautifulSoup
import requests
from decimal import Decimal
from telegram import InlineQueryResultArticle, ParseMode,InputTextMessageContent
from telegram.ext import Updater, InlineQueryHandler, CommandHandler
from uuid import uuid4
from coin import *

# Constant variables for clarity.
OPEN = 3
HIGH = 5
LOW = 7
CLOSE = 9
VOLUME = 11
MARKETCAP = 13

# Represents a date.
class Date:

	def __init__(self, day, month, year, numWords):

		self.day = str(day).zfill(2)
		self.month = str(month).zfill(2)
		self.year = str(year)

		# This tells whether the date in the query was 3 words (i.e. August 17, 2018) or 1 word (i.e. 8/17/2018)
		self.numWords = numWords

# Represents a cryptocurrency's data on a certain day.
class PriceOnDay:

	def __init__(self, values):

		self.open = format_monetary_value(float(values[OPEN][:-4]), True)
		self.high = format_monetary_value(float(values[HIGH][:-4]), True)
		self.low = format_monetary_value(float(values[LOW][:-4]), True)
		self.close = format_monetary_value(float(values[CLOSE][:-4]), True)
		self.volume = values[VOLUME][:-4]
		self.marketCap = values[MARKETCAP][:-4]

# Uses Datefinder to parse the query for any dates present. However, because Datefinder doesn't
# find relative dates, it's necessary to include checks for "yesterday" and "ago" in the query.
def determine_if_date_in_string(query):

	dateList = list(datefinder.find_dates(query))

	if "yesterday" in query or "ago" in query or len(dateList) > 0:
		return True

	return False

# Finds the date in the query and returns a Date object.
def get_date_from_query(query):

	date = ""

	if "yesterday" in query:
		date = dateparser.parse("yesterday")
		return Date(date.day, date.month, date.year, 1)

	elif "/" in query or "." in query:

		date = query.split(" ")
		separatedDate = date[len(date) - 1]
		date = dateparser.parse(separatedDate)
		return Date(date.day, date.month, date.year, 1)

	else:
		date = query.split(" ")
		separatedDate = ""

		for x in range (len(date) - 3, len(date)):
			separatedDate += date[x] + " "

		date = dateparser.parse(separatedDate)
		return Date(date.day, date.month, date.year, 3)


# Converts a numbered month to its actual name
def convert_month_number_to_name(month):

	months = ["January", "February", "March", "April", "May", "June", "July", "August",\
	"September", "October", "November", "December"]

	return months[int(month) - 1]

# Constructs the historical pricing list.
def generate_historical_pricing_list(query):

	date = get_date_from_query(query)
	monthWord = convert_month_number_to_name(date.month)
	convertedDate = monthWord + " " + date.day + ", " + date.year

	splitQuery = query.split(" ")
	currency = ""
	currencySize = 0

	# Get the name of the currency from the query.
	for x in range (0, len(splitQuery) - date.numWords):
		currency += splitQuery[x] + " "
		currencySize += 1

	currency = currency[:-1]

	# Generate a Coin object to quickly grab the image URL and the slug
	coin = Coin(currency, None)

	# Construct the URL from where the data will be scraped
	currencyURL = (
		"https://coinmarketcap.com/currencies/" 
		+ coin.slug + "/historical-data/?start=" 
		+ date.year + date.month + date.day 
		+ "&end=" + date.year + date.month + date.day
	)

	# Download and scrape the page using BeautifulSoup4 and requests.
	page = requests.get(currencyURL)
	soup = BeautifulSoup(page.content, 'html.parser')

	values = str(soup.find_all('td'))
	values = values.split(">")
	values = PriceOnDay(values)

	summary = "***Price Data for " + coin.name + "***\n" + convertedDate + "\n\n"\
	+ "***Open:*** $" + values.open + "\n"\
	+ "***High:*** $" + values.high + "\n"\
	+ "***Low:*** $" + values.low + "\n"\
	+ "***Close:*** $" + values.close + "\n"\
	+ "***Volume:*** $" + values.volume + "\n"\
	+ "***Market Capitalization:*** $" + values.marketCap

	results = [

	        # Header (i.e., "Price Data for [Coin]")
            InlineQueryResultArticle(
                id=uuid4(),
                title="Price Data for " + coin.name + " (" + coin.symbol + ")",
                description=convertedDate,
                thumb_url=coin.imageURL,
                input_message_content=InputTextMessageContent(summary, \
                    ParseMode.MARKDOWN)),

            # Open
            InlineQueryResultArticle(
                id=uuid4(),
                title=("Open"),
                description="$" + values.open,
                thumb_url="https://imgur.com/EYOqB1W.png",
                input_message_content=InputTextMessageContent("***" + coin.name + " Opening Price***\n"
                	+ convertedDate + "\n\n" + "$" + values.open, ParseMode.MARKDOWN)),

            # High
            InlineQueryResultArticle(
                id=uuid4(),
                title=("High"),
                description="$" + values.high,
                thumb_url="https://imgur.com/ntXndWR.png",
                input_message_content=InputTextMessageContent("***" + coin.name + " High Price***\n"
                	+ convertedDate + "\n\n" + "$" + values.high, ParseMode.MARKDOWN)),

            # Low
            InlineQueryResultArticle(
                id=uuid4(),
                title=("Low"),
                description="$" + values.low,
                thumb_url=("https://imgur.com/zOfZSYj.png"),
                input_message_content=InputTextMessageContent("***" + coin.name + " Low Price***\n"
                	+ convertedDate + "\n\n" + "$" + values.low, ParseMode.MARKDOWN)),

            # Close
            InlineQueryResultArticle(
                id=uuid4(),
                title=("Close"),
                description="$" + values.close,
                thumb_url=("https://imgur.com/iQXqgYU.png"),
                input_message_content=InputTextMessageContent("***" + coin.name + " Closing Price***\n"
                	+ convertedDate + "\n\n" + "$" + values.close, ParseMode.MARKDOWN)),

            # Volume
            InlineQueryResultArticle(
                id=uuid4(),
                title=("Volume"),
                description="$" + values.volume,
                thumb_url=("https://imgur.com/qO0rcCI.png"),
                input_message_content=InputTextMessageContent("***" + coin.name + " Volume***\n"
                	+ convertedDate + "\n\n" + "$" + values.volume, ParseMode.MARKDOWN)),

            # Market Capitalization
            InlineQueryResultArticle(
                id=uuid4(),
                title=("Market Capitalization"),
                description="$" + values.marketCap,
                thumb_url=("https://i.imgur.com/UMczLVP.png"),
                input_message_content=InputTextMessageContent("***" + coin.name + " Market Capitalization***\n"
                	+ convertedDate + "\n\n" + "$" + values.marketCap, ParseMode.MARKDOWN))
	]

	return results
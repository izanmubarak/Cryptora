from telegram import InlineQueryResultArticle, ParseMode,InputTextMessageContent
from uuid import uuid4
import requests
from decimal import Decimal

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

def get_stats_list():

	data = GeneralStats()

	results = [

		InlineQueryResultArticle(
			id=uuid4(),
			title=("Total Market Capitalization"),
			thumb_url="https://i.imgur.com/UMczLVP.png",
			description=("$" + str(data.marketCap)),
			input_message_content=InputTextMessageContent("***Total Market Capitalization:*** " \
				+ "$" + str(data.marketCap), ParseMode.MARKDOWN)),

		InlineQueryResultArticle(
			id=uuid4(),
			title=("Total 24 Hour Volume"),
			thumb_url="https://imgur.com/Qw4y4Ed.png",
			description=("$" + str(data.volume24h)),
			input_message_content=InputTextMessageContent("***Total 24 Hour Volume:*** $" \
				+ str(data.volume24h),  ParseMode.MARKDOWN)),

		InlineQueryResultArticle(
			id=uuid4(),
			title=("Bitcoin Dominance"),
			description=(str(data.dominanceBTC) + "%"),
			thumb_url="https://imgur.com/tXiapTn.png",
			input_message_content=InputTextMessageContent("***Bitcoin Dominance:*** " \
				+ str(data.dominanceBTC) + "%",  ParseMode.MARKDOWN)),

		InlineQueryResultArticle(
    		id=uuid4(),
    		title=("Active Cryptocurrencies"),
    		thumb_url="https://imgur.com/g6YajTp.png",
    		description=(str(data.activeCryptoCount) + " active cryptocurrencies"),
    		input_message_content=InputTextMessageContent(str(data.activeCryptoCount) \
    			+ " active cryptocurrencies on CoinMarketCap.", ParseMode.MARKDOWN)),

		InlineQueryResultArticle(
    		id=uuid4(),
    		thumb_url="https://imgur.com/qO0rcCI.png",
    		title=("Markets"),
    		description=(str(data.marketCount) + " markets"),
    		input_message_content=InputTextMessageContent(str(data.marketCount) \
    			+ " markets on CoinMarketCap." , ParseMode.MARKDOWN)),

	]

	return results
import requests
from decimal import Decimal
from telegram import InlineQueryResultArticle, ParseMode,InputTextMessageContent
from uuid import uuid4

class Coin:

	def __init__(self, query, rank, noCommas):

		self.data = requests.get('https://api.coinmarketcap.com/v1/ticker/?limit=10000',
		 headers={'Cache-Control': 'no-cache'}).json()

		for x in range (0, len(self.data)):

			if query.upper() == self.data[x]['symbol'] or \
				query.lower() == self.data[x]['id'] or \
				query.lower() == (self.data[x]['name']).lower() or \
				query == self.data[x]['rank']:

				self.symbol = self.data[x]['symbol']
				self.id = self.data[x]['id']
				self.rank = str(int(x) + 1)
				self.name = self.data[x]['name']
				self.supply = str("{:,}".format(Decimal(float(self.data[x]['available_supply']))))
				self.percentChange = str(self.data[x]['percent_change_24h'])
				self.marketCap = str("{:,}".format(Decimal(\
					float(self.data[x]['market_cap_usd']))))

				if noCommas == True or float(self.data[x]['price_usd']) < 1.00:
					self.price_USD = str(self.data[x]['price_usd'])

				else:
					price = Decimal((self.data[x]['price_usd'])).\
					quantize(Decimal('1.00'), rounding = 'ROUND_HALF_DOWN')
					self.price_USD = str("{:,}".format(price))

				self.summary = ("***" + self.name + "***" + " (" + self.symbol + ")" + '\n \n' + \
					'***Rank***: #' + str(self.rank) + " out of " + str(len(self.data)) + "\n" + \
					'***Price***: $' + str(self.price_USD) + '\n' + '***Market Capitalization***: $' \
					+ str(self.marketCap) + '\n' + '***Circulating Supply***: ' + self.supply + " " + \
					self.symbol + '\n' + '***24 Hour Percent Change***: ' + \
					self.percentChange + "% \n")

def get_coin_info(query):

	coin = Coin(query, None, False)

	results = [

		# Summary
		InlineQueryResultArticle(
        	id=uuid4(),
        	title=(coin.name + " (" + coin.symbol + ")"),
        	description="#" + coin.rank + " out of " + str(len(coin.data)),
        	thumb_url='https://files.coinmarketcap.com/static/img/coins/128x128/' \
        	+ coin.id + '.png',
        	input_message_content=InputTextMessageContent(coin.summary, \
        		ParseMode.MARKDOWN)),

		# USD Price
		InlineQueryResultArticle(
    		id=uuid4(),
    		title=("Price"),
    		description="$" + coin.price_USD,
    		thumb_url="https://imgur.com/7RCGCoc.png",
    		input_message_content=InputTextMessageContent("1 " + coin.symbol + " = $" \
    			+ coin.price_USD)),

		# Market Capitalization (USD)
    	InlineQueryResultArticle(
        	id=uuid4(),
        	title=("Market Capitalization"),
        	description="$" + coin.marketCap,
        	thumb_url="https://i.imgur.com/UMczLVP.png",
        	input_message_content=InputTextMessageContent("Market Capitalization of " \
        		+ coin.name + " (" + coin.symbol + ")" + ": $" + coin.marketCap)),

    	# Circulating Supply 
    	InlineQueryResultArticle(
        	id=uuid4(),
        	title=("Circulating Supply"),
        	description=coin.supply + " " + coin.symbol,
        	thumb_url=("https://i.imgur.com/vXAN23U.png"),
        	input_message_content=InputTextMessageContent("Circulating Supply of " \
        		+ coin.name + " (" + coin.symbol + ")" + ": " + coin.supply + " " \
        		+ coin.symbol)),

    	# 24 Hour Percent Change
    	InlineQueryResultArticle(
        	id=uuid4(),
        	title=("Percent Change (24 hours)"),
        	description=coin.percentChange + "%",
        	thumb_url=("https://imgur.com/iAoXFQc.png"),
        	input_message_content=InputTextMessageContent("24 Hour Change in " \
        		+ coin.name + " (" + coin.symbol + ")" + " Price: " + coin.percentChange \
        		+ "%"))
	]

	return results
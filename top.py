import requests
from decimal import Decimal
from telegram import InlineQueryResultArticle, ParseMode, InputTextMessageContent
from uuid import uuid4

JSON_API_URL = 'https://api.coinmarketcap.com/v1/ticker/?limit=10000'

def get_top_cryptocurrencies(listSize):

	results = []
	data = requests.get(JSON_API_URL).json()

	for rank in range (1, listSize):
		
		ID = data[rank - 1]['id']
		symbol = data[rank - 1]['symbol']
		name = data[rank - 1]['name']
		supplyValue = "{:,}".format(Decimal(float(\
				data[rank - 1]['available_supply'])))
		ranking = int(rank)
		cap = str("{:,}".format(Decimal(\
				float(data[rank - 1]['market_cap_usd']))))
		percentChange = data[rank - 1]['percent_change_24h']

		if float(data[rank - 1]['price_usd']) < 1.00:		
			price = data[rank - 1]['price_usd']

		else:
			decimalizedPrice = Decimal(data[rank - 1]['price_usd']).quantize(\
				Decimal('1.00'), rounding = 'ROUND_HALF_DOWN')
			price = str("{:,}".format(decimalizedPrice))
			

		summary = ("***" + name + "***" + " (" + symbol + ")" + '\n \n' + \
			'***Rank***: #' + str(ranking) + " out of " + str(len(data)) + \
			 "\n" + '***Price***: $' + price + '\n' + '***Market Capitalization***: $' + \
			 str(cap) + '\n' + '***Circulating Supply***: ' + str(supplyValue) + \
			 " " + symbol + '\n' + '***24 Hour Percent Change***: ' + \
			 percentChange + "% \n")


		results.append(
			InlineQueryResultArticle(
				id=uuid4(),
				thumb_url='https://files.coinmarketcap.com/static/img/' \
				+ 'coins/128x128/' + ID + '.png',
				description=("$" + price),
				title=(str(rank) + ". " + name),
				input_message_content=InputTextMessageContent(\
					summary, ParseMode.MARKDOWN))
		)

	return results
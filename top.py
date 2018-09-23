import requests
from retrieve_tokens import *
from coin import *
from decimal import Decimal
from telegram import InlineQueryResultArticle, ParseMode, InputTextMessageContent
from uuid import uuid4

def get_top_cryptocurrencies(listSize):

	data = requests.get('https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest?CMC_PRO_API_KEY=' + get_token(True) + '&start=1&limit=50&convert=USD&sort=market_cap').json()

	data = data['data']
	topStr = "***Top " + str(listSize) + " Cryptocurrencies by Market Capitalization***\n\n"
	results = []
		
	for x in range (0, listSize):

		coin = Coin(None, data[x])

		topStr += "#" + str(x + 1) + ". ***" + coin.name + "***: $" + coin.marketCap + "\n"

		results.append(
			InlineQueryResultArticle(
				id=uuid4(),
				thumb_url=coin.imageURL,
				description=("$" + coin.price_USD),
				title=(str(coin.rank) + ". " + coin.name + " (" + coin.symbol + ")"),
				input_message_content=InputTextMessageContent(\
					coin.summary, ParseMode.MARKDOWN))
		)

	results.insert(0, 
		InlineQueryResultArticle(
				id=uuid4(),
				thumb_url='https://imgur.com/g6YajTp.png',
				description="Tap to send list.",
				title=("Top " + str(listSize) + " cryptocurrencies by market capitalization"),
				input_message_content=InputTextMessageContent(\
					topStr, ParseMode.MARKDOWN))
	)

	return results
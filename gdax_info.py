# Cryptora - Public Repository
# GDAX specific functions

import gdax
from decimal import Decimal
from telegram import InlineQueryResultArticle, ParseMode,InputTextMessageContent
from uuid import uuid4

def get_GDAX_prices():

	# Retrieves the GDAX pricing, using the GDAX Python API

	public_client = gdax.PublicClient()

	price = public_client.get_product_ticker(product_id='BTC-USD')['price']
	decimalizedPrice = Decimal(price).quantize(Decimal('1.00'), \
		rounding = 'ROUND_HALF_DOWN')
	bitcoin = str("{:,}".format(decimalizedPrice))

	price = public_client.get_product_ticker(product_id='LTC-USD')['price']
	decimalizedPrice = Decimal(price).quantize(Decimal('1.00'), \
		rounding = 'ROUND_HALF_DOWN')
	litecoin = str("{:,}".format(decimalizedPrice))


	price = public_client.get_product_ticker(product_id='ETH-USD')['price']
	decimalizedPrice = Decimal(price).quantize(Decimal('1.00'), \
		rounding = 'ROUND_HALF_DOWN')
	ethereum = str("{:,}".format(decimalizedPrice))


	price = public_client.get_product_ticker(product_id='BCH-USD')['price']
	decimalizedPrice = Decimal(price).quantize(Decimal('1.00'), \
		rounding = 'ROUND_HALF_DOWN')
	bitcoinCash = str("{:,}".format(decimalizedPrice))

	results = [

		InlineQueryResultArticle(
			id=uuid4(),
			title=("GDAX Pricing"),
			thumb_url="https://imgur.com/Eyh7KSb.png",
			description=("View summary..."),
			input_message_content=InputTextMessageContent((\
				"***GDAX Trading Prices*** \n \n***Bitcoin:*** $" \
				+ bitcoin + "\n***Litecoin:*** $" + litecoin + \
				"\n***Ethereum:*** $" + ethereum + "\n***Bitcoin Cash:*** $" + \
				bitcoinCash), ParseMode.MARKDOWN)),

		InlineQueryResultArticle(
			id=uuid4(),
			title=("Bitcoin"),
			thumb_url='https://files.coinmarketcap.com/static/' + \
			'img/coins/128x128/bitcoin.png',
			description=("$" + bitcoin),
			input_message_content=InputTextMessageContent((\
				"***GDAX Bitcoin Trading Price:*** $" + bitcoin),\
				 ParseMode.MARKDOWN)),

		InlineQueryResultArticle(
			id=uuid4(),
			title=("Litecoin"),
			description=("$" + litecoin),
			thumb_url='https://files.coinmarketcap.com/static/' + \
			'img/coins/128x128/litecoin.png',
			input_message_content=InputTextMessageContent((\
				"***GDAX Litecoin Trading Price:*** $" + litecoin), \
				 ParseMode.MARKDOWN)),

		InlineQueryResultArticle(
    		id=uuid4(),
    		title=("Ethereum"),
    		description=("$" + ethereum),
			thumb_url='https://files.coinmarketcap.com/static/' + \
			'img/coins/128x128/ethereum.png',
			input_message_content=InputTextMessageContent((\
				"***GDAX Ethereum Trading Price:*** $" + ethereum),\
				 ParseMode.MARKDOWN)),

		InlineQueryResultArticle(
    		id=uuid4(),
    		title=("Bitcoin Cash"),
    		description=("$" + bitcoinCash),
			thumb_url='https://files.coinmarketcap.com/static/' + \
			'img/coins/128x128/bitcoin-cash.png',
			input_message_content=InputTextMessageContent((\
				"***GDAX Bitcoin Cash Trading Price:*** $" + bitcoinCash),\
				 ParseMode.MARKDOWN))

	]

	return results


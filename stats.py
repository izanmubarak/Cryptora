# Cryptora - Public Repository
# All global statistics.

from telegram import InlineQueryResultArticle, ParseMode,InputTextMessageContent
from retrieve_tokens import *
from coin import *
from uuid import uuid4
import requests
from decimal import Decimal

data = requests.get('https://pro-api.coinmarketcap.com/v1/global-metrics/quotes/latest?CMC_PRO_API_KEY=' + get_token(True)).json()['data']

def get_stats_list():

	marketCap = format_monetary_value(data['quote']['USD']['total_market_cap'], True)
	volume = format_monetary_value(data['quote']['USD']['total_volume_24h'], True)
	activeCurrencies = str(data['active_cryptocurrencies'])
	activeExchanges = str(data['active_exchanges'])
	dominanceETH = format_monetary_value(data['eth_dominance'], True)
	dominanceBTC = format_monetary_value(data['btc_dominance'], True)

	# Generate a message that contains all of the global stats. Sendable by the user.
	globalStatsMessage = "***Global Cryptocurrency Statistics***\n\n" \
	+ "***Total Market Capitalization:*** $" + marketCap + "\n" \
	+ "***Total 24 Hour Volume:*** $" + volume + "\n" \
	+ "***Bitcoin Dominance:*** " + dominanceBTC + "%\n" \
	+ "***Ethereum Dominance:*** " + dominanceETH + "%\n" \
	+ "***Total Active Currencies:*** " + activeCurrencies + "\n" \
	+ "***Total Active Exchanges:*** " + activeExchanges

	results = [

		InlineQueryResultArticle(
			id=uuid4(),
			title=("Global Cryptocurrency Statistics"),
			thumb_url="https://imgur.com/g6YajTp.png",
			description="Tap to send list.",
			input_message_content=InputTextMessageContent(globalStatsMessage, ParseMode.MARKDOWN)),

		InlineQueryResultArticle(
			id=uuid4(),
			title=("Total Market Capitalization"),
			thumb_url="https://i.imgur.com/UMczLVP.png",
			description=("$" + marketCap),
			input_message_content=InputTextMessageContent("***Total Market Capitalization:*** " \
				+ "$" + marketCap, ParseMode.MARKDOWN)),

		InlineQueryResultArticle(
			id=uuid4(),
			title=("Total 24 Hour Volume"),
			thumb_url="https://imgur.com/Qw4y4Ed.png",
			description=("$" + volume),
			input_message_content=InputTextMessageContent("***Total 24 Hour Volume:*** $" \
				+ volume,  ParseMode.MARKDOWN)),

		InlineQueryResultArticle(
			id=uuid4(),
			title=("Bitcoin Dominance"),
			description=(dominanceBTC + "%"),
			thumb_url="https://imgur.com/tXiapTn.png",
			input_message_content=InputTextMessageContent("***Bitcoin Dominance:*** " \
				+ dominanceBTC + "%",  ParseMode.MARKDOWN)),

		InlineQueryResultArticle(
			id=uuid4(),
			title=("Ethereum Dominance"),
			description=(dominanceETH + "%"),
			thumb_url="https://i.imgur.com/EMEUTYl.jpg",
			input_message_content=InputTextMessageContent("***Bitcoin Dominance:*** " \
				+ dominanceETH + "%",  ParseMode.MARKDOWN)),

		InlineQueryResultArticle(
    		id=uuid4(),
    		title=("Active Cryptocurrencies"),
    		thumb_url="https://imgur.com/g6YajTp.png",
    		description=(activeCurrencies + " active cryptocurrencies"),
    		input_message_content=InputTextMessageContent(activeCurrencies \
    			+ " active cryptocurrencies on CoinMarketCap.", ParseMode.MARKDOWN)),

		InlineQueryResultArticle(
    		id=uuid4(),
    		thumb_url="https://imgur.com/qO0rcCI.png",
    		title=("Active Exchanges"),
    		description=(activeExchanges + " active exchanges"),
    		input_message_content=InputTextMessageContent(activeExchanges \
    			+ " active exchanges on CoinMarketCap." , ParseMode.MARKDOWN)),

	]

	return results
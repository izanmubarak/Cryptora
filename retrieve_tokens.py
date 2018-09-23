# Cryptora - Public Repository

# This file reads in a provided tokens.txt file to retrieve the API tokens for the Telegram Bot API and 
# the CoinMarketCap API.

def get_token(CMC):
	
	file = open("tokens.txt", "r")
	CMC_TOKEN = file.readline()[:-1][11:]
	BOT_TOKEN = file.readline()[11:]

	if CMC:
		return CMC_TOKEN

	return BOT_TOKEN
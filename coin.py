# Cryptora - Public Repository
''' The Coin class represents a cryptocurrency and its metadata.
Cryptora currently displays the requested cryptocurrency's symbol, name, supply, market cap, price,
and percent change. The Coin class holds this information, as well as the summary of the coin that
is printed when the user clicks on the crypto's name in the popup list that appears.'''

import requests
from decimal import Decimal
from retrieve_tokens import *
from telegram import InlineQueryResultArticle, ParseMode, InputTextMessageContent
from uuid import uuid4

''' Download the full list of coins from CoinMarketCap. This list is parsed to find the user's coin,
get the official name, symbol, and the coin's logo. The rest of the data is downloaded from a
separate JSON file (which is done in the download_coin_data() function)'''

token = get_token(True)
coinMap = (requests.get('https://pro-api.coinmarketcap.com/v1/cryptocurrency/map?CMC_PRO_API_KEY=' + token).json())\
["data"]

class Coin:

    # Constructor for the Coin class.
    def __init__(self, query, data):

        # Record whether the coin exists. Used for multicurrency to filter out invalid entries.
        self.exists = False

        # Stores the currencies with the same name or symbol as a comma separated list.
        self.currenciesWithSymbol = ""

        # Record the number of currencies found with the same symbol or name.
        self.occurrences = 0

        if data is None: 

            for item in range (0, len(coinMap)):

                # Cryptora supports both the name of the currency and its symbol for search.
                if query.upper() == coinMap[item]['symbol'] or query.lower() == coinMap[item]['name'].lower():

                    self.exists = True

                    # Get the coin's full name, ID, date of first historical data, and symbol from CMC
                    self.symbol = coinMap[item]['symbol']
                    self.name = coinMap[item]["name"]
                    self.slug = coinMap[item]['slug']
                    self.ID = coinMap[item]['id']
                    self.firstData = coinMap[item]["first_historical_data"]

                    # Store the IDs of each currency with the same symbol in a list.
                    self.currenciesWithSymbol += str(self.ID) + ","
                    self.occurrences += 1

                    # Get the coin's logo from CMC
                    self.imageURL = 'https://s2.coinmarketcap.com/static/img/coins/200x200/' + str(self.ID) + '.png'

                    # Get the metadata about the specific coin entered in JSON form
                    self.data = download_coin_data(self.ID)

                    # Parse and store the necessary data from self.data (supply, % change, mktcap, rank, and USD price)
                    self.rank = str(self.data['cmc_rank'])
                    self.supply = format_monetary_value(self.data['circulating_supply'], False)
                    self.marketCap = format_monetary_value(self.data['quote']['USD']['market_cap'], True)
                    self.price_USD = format_monetary_value(self.data['quote']['USD']['price'], True)

                    # Will always round percent changes to the hundredths place.
                    self.percentChange = str(Decimal(self.data['quote']['USD']['percent_change_24h'])\
                        .quantize(Decimal('1.00'), rounding = 'ROUND_HALF_DOWN'))

        else:

            ''' This block of code generates a Coin object with a passed in JSON array containing all of the coin's 
            metadata. This is primarily used in the "Top X"  and multicurrency functionality, but if a Coin object needs
            to be generated with preexisting or already retrieved data, then this will accomplish that. '''

            self.exists = True
            self.name = data['name']
            self.symbol = data['symbol']
            self.ID = data['id']
            self.firstData = data['date_added']
            self.imageURL = 'https://s2.coinmarketcap.com/static/img/coins/200x200/' + str(self.ID) + '.png'
            self.rank = str(data['cmc_rank'])
            self.supply = format_monetary_value(data['circulating_supply'], False)
            self.marketCap = format_monetary_value(data['quote']['USD']['market_cap'], True)
            self.price_USD = format_monetary_value(data['quote']['USD']['price'], True)
            self.percentChange = str(Decimal(data['quote']['USD']['percent_change_24h'])\
                .quantize(Decimal('1.00'), rounding = 'ROUND_HALF_DOWN'))

        if self.exists:

            '''Generate a summary that is displayed when the user clicks on the name of the coin in the list, 
            formatted using Markdown'''

            self.summary =  ("***" + self.name + "***" + " (" + self.symbol + ")" + '\n\n' \
                + "***Rank:*** #" + self.rank + " out of " + str(len(coinMap)) + '\n' \
                + '***Price***: $' + str(self.price_USD) + '\n' \
                + '***Market Capitalization***: $' + str(self.marketCap) + '\n' \
                + '***Circulating Supply***: ' + self.supply + " " + self.symbol + '\n' \
                + '***24 Hour Percent Change***: ' + self.percentChange + "% \n") 

    
# Download the JSON file that contains the data about the user's coin
def download_coin_data(ID):

    data = requests.get('https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?CMC_PRO_API_KEY=' + token + \
        '&id=' + str(ID)).json()
    return data['data'][str(ID)]

# Format monetary values and percents correctly (i.e. with commas and decimal rounding to two places).
def format_monetary_value(value, decmials):
    
    if value == None or value == 0:
        return "N/A"

    if abs(float(value)) >= 1.00:
        if decmials:
            value = Decimal(value).quantize(Decimal('1.00'), rounding = 'ROUND_HALF_DOWN')
        return str("{:,}".format(value))
    else:
        return str(Decimal(value).quantize(Decimal('1.00000000'), rounding = 'ROUND_HALF_DOWN'))

''' Generate the list displayed in the Telegram chat. This generates an array of object InlineQueryResultArticle
that is passed into Telegram for the user to see.'''
def get_coin_info(query):

    results = []
    coin = Coin(query, None)

    if coin.occurrences > 1:
        return generate_list_for_same_symbol_currencies(coin.currenciesWithSymbol)

    if not coin.exists:
        return False

    results = [

            # Summary
            InlineQueryResultArticle(
                id=uuid4(),
                title=(coin.name + " (" + coin.symbol + ")"),
                description="#" + coin.rank + " out of " + str(len(coinMap)),
                thumb_url=coin.imageURL,
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

''' Generate the list displayed in the Telegram chat, if a currency symbol is entered that corresponds to
multiple currencies.'''
def generate_list_for_same_symbol_currencies(currenciesWithSymbol):

    # Remove the last comma from the URL
    currenciesWithSymbol = currenciesWithSymbol[:-1]

    # Create a list with each currency stored
    currencyList = currenciesWithSymbol.split(",")

    results = []
    
    # The message that will be sent when the user taps the first option.
    allPricesList = "***Selected Cryptocurrency Prices***\n\n"

    # The data file that contains all the cryptocurrencies.
    data = requests.get('https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?CMC_PRO_API_KEY=' \
        + token + "&id=" + currenciesWithSymbol).json()["data"]

    # Build the list of currencies with the same symbol/name.
    for x in range (0, len(data)):

        coin = Coin(None, data[currencyList[x]])

        results.append(

            InlineQueryResultArticle(
                id=uuid4(),
                title=coin.name + " (" + coin.symbol + ")",
                description="$" + coin.price_USD,
                thumb_url=coin.imageURL,
                input_message_content=InputTextMessageContent(coin.summary, ParseMode.MARKDOWN)

            ))

        allPricesList += "***" + coin.name + "***: $" + coin.price_USD + "\n"

    # Preface the list with a "Multiple Currencies Found" message.
    results.insert(0, 
        InlineQueryResultArticle(
            id=uuid4(),
            title="Multiple Currencies Found",
            description="Tap to send prices.",
            thumb_url="https://imgur.com/g6YajTp.png",
            input_message_content=InputTextMessageContent(allPricesList, ParseMode.MARKDOWN)))


    return results
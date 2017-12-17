# -*- coding: utf-8 -*-
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from uuid import uuid4
import re
from telegram.utils.helpers import escape_markdown
from telegram import InlineQueryResultArticle, ParseMode,InputTextMessageContent
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
import os
import sys
import requests
from decimal import Decimal
from bs4 import BeautifulSoup
import feedparser
import datefinder
import dateparser
import gdax
from Cryptora_functions import *

# Constant variables. 
JSON_API_URL = 'https://api.coinmarketcap.com/v1/ticker/?limit=10000'
JSON_DATA = requests.get(JSON_API_URL).json()
NEWS_URL = "http://coindesk.com/feed"
token = '463277822:AAGhIn--7kELcYSB7MhVp-JUTkOOZtCWZUo'

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - \
 %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def inlinequery(bot, update):

    query = update.inline_query.query
    dateInString = determine_if_date_in_string(query)

    # CryptoCalculator
    if query[0].isdigit():

        userInputName = ""
        for x in range (1, len(query.split(" "))):
            userInputName += query.split(" ")[x] + " "

        inputCoin = Coin((userInputName[:-1]).title(), None, False)
        instance = CryptoCalculatorInstance(query, inputCoin.symbol, False, None, None)
        results = [
            InlineQueryResultArticle(
                id=uuid4(),
                thumb_url='https://files.coinmarketcap.com/static/img/coins/200x200/' + inputCoin.id + '.png',
                title=("Convert " + instance.inputValue + " " + inputCoin.symbol + " to USD"),
                description="$" + instance.calculatedValue,
                input_message_content=InputTextMessageContent(instance.inputValue + " " + inputCoin.symbol + " = $" + instance.calculatedValue))
        ]
    
    # Reverse CryptoCalculator
    elif query[0] == "$":   
        splitQuery = query.split(" ")
        length = len(splitQuery)
        inputDollarValue = (splitQuery[0])[1:]
        currency = ""

        if splitQuery[1] == "to":
            for x in range (2, length):
                currency += splitQuery[x] + " "
        else:
            for x in range (1, length):
                currency += splitQuery[x] + " "

        currency = currency[:-1]
        inputCoin = Coin(currency, None, True)
        value = CryptoCalculatorInstance(query, inputCoin.symbol, True, inputCoin.price_USD, inputDollarValue)

        results = [
            InlineQueryResultArticle(
                id=uuid4(),
                title=("Convert $" + inputDollarValue + " to " + inputCoin.symbol),
                thumb_url='https://files.coinmarketcap.com/static/img/coins/200x200/' + inputCoin.id + '.png',
                description=(str(value.calculatedValue) + " " + str(inputCoin.symbol)),
                input_message_content=InputTextMessageContent("$" + str(inputDollarValue) + " = " + str(value.calculatedValue) + " " + str(inputCoin.symbol)))
        ]

    # News
    elif "news" in query:
        results = []
        feed = feedparser.parse("http://coindesk.com/feed")
        for x in range (0, 9):
            article = NewsArticle(x, feed)
            results.append(
                InlineQueryResultArticle(
                    id=uuid4(),
                    description=(article.subtitle),
                    thumb_url=article.thumbnailURL,
                    title=(article.title),
                    input_message_content=InputTextMessageContent(article.URL)),
                )
    # Top X
    elif "top" in query:
        results = []
        listSize = (int(query.split(" ")[1]) + 1)
        for rank in range (1, listSize):
            listElement = Coin(query, str(rank), False) 
            results.append(
                InlineQueryResultArticle(
                    id=uuid4(),
                    thumb_url='https://files.coinmarketcap.com/static/img/coins/128x128/' + listElement.id + '.png',
                    description=("$" + listElement.price_USD),
                    title=(str(rank) + ". " + listElement.name),
                    input_message_content=InputTextMessageContent(listElement.summary, ParseMode.MARKDOWN))
                )

    elif query.upper() == "GDAX":

        public_client = gdax.PublicClient()

        bitcoin = str("{:,}".format(Decimal(public_client.get_product_ticker(product_id='BTC-USD')['price']).quantize(Decimal('1.00'), rounding = 'ROUND_HALF_DOWN')))

        ethereum = str("{:,}".format(Decimal(public_client.get_product_ticker(product_id='ETH-USD')['price']).quantize(Decimal('1.00'), rounding = 'ROUND_HALF_DOWN')))

        litecoin = str("{:,}".format(Decimal(public_client.get_product_ticker(product_id='LTC-USD')['price']).quantize(Decimal('1.00'), rounding = 'ROUND_HALF_DOWN')))

        results = [
                    InlineQueryResultArticle(
                        id=uuid4(),
                        title=("GDAX Pricing"),
                        thumb_url="https://imgur.com/Eyh7KSb.png",
                        description=("View summary..."),
                        input_message_content=InputTextMessageContent(("***GDAX Trading Prices*** \n \n ***Bitcoin:*** $" + bitcoin + "\n ***Litecoin:*** $" + litecoin + "\n ***Ethereum:*** $" + ethereum), ParseMode.MARKDOWN)),

                    InlineQueryResultArticle(
                        id=uuid4(),
                        title=("Bitcoin"),
                        thumb_url='https://files.coinmarketcap.com/static/img/coins/128x128/bitcoin.png',
                        description=("$" + bitcoin),
                        input_message_content=InputTextMessageContent(("***GDAX Bitcoin Trading Price:*** $" + bitcoin), ParseMode.MARKDOWN)),

                    InlineQueryResultArticle(
                        id=uuid4(),
                        title=("Litecoin"),
                        description=("$" + litecoin),
                        thumb_url='https://files.coinmarketcap.com/static/img/coins/128x128/litecoin.png',
                        input_message_content=InputTextMessageContent(("***GDAX Litecoin Trading Price:*** $" + litecoin), ParseMode.MARKDOWN)),

                    InlineQueryResultArticle(
                        id=uuid4(),
                        title=("Ethereum"),
                        description=("$" + ethereum),
                        thumb_url='https://files.coinmarketcap.com/static/img/coins/128x128/ethereum.png',
                        input_message_content=InputTextMessageContent(("***GDAX Ethereum Trading Price:*** $" + ethereum), ParseMode.MARKDOWN))
                    ]

    elif dateInString == True or "ago" in query:

        if "ago" in query:

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

            string = ("***Price Data for " + coin.name + "*** \n" + description + "\n \n" + "***High:*** $" + data.high + "\n***Low:*** $" + data.low + "\n***Open:*** $" + data.open + "\n***Close:*** $" + data.close)

            if len(data.year) != 4:
                results = [
                    InlineQueryResultArticle(
                        id=uuid4(),
                        title=(),
                        thumb_url=(),
                        input_message_content=InputTextMessageContent())
                    ]

            results = [
                    InlineQueryResultArticle(
                        id=uuid4(),
                        title=("View Price Data for " + coin.name),
                        thumb_url='https://files.coinmarketcap.com/static/img/coins/128x128/' + coin.id + '.png',
                        description=(description),
                        input_message_content=InputTextMessageContent(string, ParseMode.MARKDOWN)),

                    InlineQueryResultArticle(
                        id=uuid4(),
                        title=("High"),
                        description=("$" + data.high),
                        thumb_url="https://imgur.com/ntXndWR.png",
                        input_message_content=InputTextMessageContent("***" + coin.name + " High Price*** \n" + description + "\n \n$" + data.high,  ParseMode.MARKDOWN)),

                    InlineQueryResultArticle(
                        id=uuid4(),
                        title=("Low"),
                        description=("$" + data.low),
                        thumb_url="https://imgur.com/zOfZSYj.png",
                        input_message_content=InputTextMessageContent("***" + coin.name + " Low Price*** \n" + description + "\n \n$" +data.low, ParseMode.MARKDOWN)),

                    InlineQueryResultArticle(
                        id=uuid4(),
                        title=("Open"),
                        thumb_url="https://imgur.com/EYOqB1W.png",
                        description=("$" + data.open),
                        input_message_content=InputTextMessageContent("***" + coin.name + " Opening Price*** \n" + description + "\n \n$" + data.open, ParseMode.MARKDOWN)),

                    InlineQueryResultArticle(
                        id=uuid4(),
                        title=("Close"),
                        thumb_url="https://imgur.com/iQXqgYU.png",
                        description=("$" + data.close),
                        input_message_content=InputTextMessageContent("***" + coin.name + " Closing Price*** \n" + description + "\n \n$" + data.close, ParseMode.MARKDOWN))

                    ]

        else:
            name = get_coin_name_from_historical_query(get_coin_word_count(query), query)

            day = str(get_day(query, True))
            month = str(get_month(query, True))
            year = str(get_year(query, True))

            coin = Coin(name, None, True)
            data = PriceOnDay(coin.id, day, month, year)

            monthName = convert_month_number_to_name(data.month)

            description = monthName + " " + data.day + ", " + data.year

            string = ("***Price Data for " + coin.name + "*** \n" + description + "\n \n" + "***High:*** $" + data.high + "\n***Low:*** $" + data.low + "\n***Open:*** $" + data.open + "\n***Close:*** $" + data.close)

            if len(data.year) != 4:
                results = [
                    InlineQueryResultArticle(
                        id=uuid4(),
                        title=(),
                        thumb_url=(),
                        input_message_content=InputTextMessageContent())
                    ]

            results = [
                    InlineQueryResultArticle(
                        id=uuid4(),
                        title=("View Price Data for " + coin.name),
                        thumb_url='https://files.coinmarketcap.com/static/img/coins/128x128/' + coin.id + '.png',
                        description=(description),
                        input_message_content=InputTextMessageContent(string, ParseMode.MARKDOWN)),

                    InlineQueryResultArticle(
                        id=uuid4(),
                        title=("High"),
                        description=("$" + data.high),
                        thumb_url="https://imgur.com/ntXndWR.png",
                        input_message_content=InputTextMessageContent("***" + coin.name + " High Price*** \n" + description + "\n \n$" + data.high,  ParseMode.MARKDOWN)),

                    InlineQueryResultArticle(
                        id=uuid4(),
                        title=("Low"),
                        description=("$" + data.low),
                        thumb_url="https://imgur.com/zOfZSYj.png",
                        input_message_content=InputTextMessageContent("***" + coin.name + " Low Price*** \n" + description + "\n \n$" +data.low, ParseMode.MARKDOWN)),

                    InlineQueryResultArticle(
                        id=uuid4(),
                        title=("Open"),
                        thumb_url="https://imgur.com/EYOqB1W.png",
                        description=("$" + data.open),
                        input_message_content=InputTextMessageContent("***" + coin.name + " Opening Price*** \n" + description + "\n \n$" + data.open, ParseMode.MARKDOWN)),

                    InlineQueryResultArticle(
                        id=uuid4(),
                        title=("Close"),
                        thumb_url="https://imgur.com/iQXqgYU.png",
                        description=("$" + data.close),
                        input_message_content=InputTextMessageContent("***" + coin.name + " Closing Price*** \n" + description + "\n \n$" + data.close, ParseMode.MARKDOWN))

                    ]

    elif "help" == query.lower():

        results = [
                InlineQueryResultArticle(
                    id=uuid4(),
                    title=("Retrieve cryptocurrency prices"),
                    description="Type the name or the abbreviation of your favorite cryptocurrency.",
                    thumb_url="https://imgur.com/joQ2gGR.png",
                    input_message_content=InputTextMessageContent("To get information about a cryptocurrency, just type the name or the shorthand abbreviation. For example, if you want to see information about Ethereum, you can just type `ethereum` or `ETH` (case does not matter), and Cryptora will get up to the moment information about Ethereum for you. \n\nYou can also type the name of your cryptocurrency, followed by a date in MM/DD/YYYY format (or Month Day, Year format) to get historical pricing. Alternatively, you can type relative dates too – so typing `bitcoin 2 weeks ago` will get you the price of Bitcoin two weeks ago.", ParseMode.MARKDOWN)),

                InlineQueryResultArticle(
                    id=uuid4(),
                    title=("Convert between cryptocurrencies and U.S. dollars"),
                    description=("Type a U.S. dollar value followed by a cryptocurrency to convert to – or type in a cryptocurrency value to see its value in dollars"),
                    thumb_url="https://imgur.com/8XwhAWO.png",
                    input_message_content=InputTextMessageContent("Cryptora can convert cryptocurrency values to U.S. dollars. Just type in a cryptocurrency value – for instance, `50 ETH` – to see the USD value of that amount of cryptocurrency. \n\nYou can also type in a U.S. dollar amount and follow that with a cryptocurrency to convert from dollars to a cryptocurrency. For example, `$50 ETH` will retrieve the quantity of Ethereum that $50 will get you.", ParseMode.MARKDOWN)),

                InlineQueryResultArticle(
                    id=uuid4(),
                    title=("Read the latest cryptocurrency headlines"),
                    description=("Type 'news' to get the 10 latest headlines from CoinDesk."),
                    thumb_url="https://imgur.com/FUX10Vi.png",
                    input_message_content=InputTextMessageContent("You can type `news` to get the ten latest headlines from CoinDesk.com in-line. Tap a link to send to your chat.", ParseMode.MARKDOWN)),

                InlineQueryResultArticle(
                    id=uuid4(),
                    title=("See the top cryptocurrencies"),
                    thumb_url="https://imgur.com/g6YajTp.png",
                    description=("Type 'top x', (x can be up to 50), to see the top cryptocurrencies ranked by market cap value."),
                    input_message_content=InputTextMessageContent("To see the top 20 cryptocurrencies, you need only type `top 20` into Cryptora. You can see the rankings for up to the top 50 cryptocurrencies – just type `top` followed by the number of cryptocurrencies you'd like to see.", ParseMode.MARKDOWN)),

                InlineQueryResultArticle(
                    id=uuid4(),
                    title=("See real-time trading prices on GDAX"),
                    thumb_url="https://imgur.com/Eyh7KSb.png",
                    description="Type GDAX to see real-time ETH, BTC, and LTC trading prices.",
                    input_message_content=InputTextMessageContent("Need more up-to-the-minute prices than the standard cryptocurrency lookup? Cryptora can retrieve the prices of bitcoin, litecoin, and ethereum on GDAX. Just type `GDAX` to get the prices in-line.", ParseMode.MARKDOWN)),

                ]


    # Cryptocurrency information
    else:
        coin = Coin(query, None, False)
        if coin.name == "None":
            # Makes sure if the user types an invalid cryptocurrency name, it doesn't pop up with a "None" currency with "None" values. This essentially throws off the inline bot by feeding it junk it can't comprehend. 
            results = [
                InlineQueryResultArticle(
                    id=uuid4(),
                    title=(),
                    thumb_url=(),
                    input_message_content=InputTextMessageContent())
                ]

        results = [
            # Summary
            InlineQueryResultArticle(
                id=uuid4(),
                title=(coin.name + " (" + coin.symbol + ")"),
                description="View summary...",
                thumb_url='https://files.coinmarketcap.com/static/img/coins/128x128/' + coin.id + '.png',
                input_message_content=InputTextMessageContent(coin.summary, ParseMode.MARKDOWN)),

            # USD Price
            InlineQueryResultArticle(
                id=uuid4(),
                title=("Price"),
                description="$" + coin.price_USD,
                thumb_url="https://imgur.com/7RCGCoc.png",
                input_message_content=InputTextMessageContent("1 " + coin.symbol + " = $" + coin.price_USD)),

            # Market Capitalization (USD)
            InlineQueryResultArticle(
                id=uuid4(),
                title=("Market Capitalization"),
                description="$" + coin.marketCap,
                thumb_url="https://i.imgur.com/UMczLVP.png",
                input_message_content=InputTextMessageContent("Market Capitalization of " + coin.name + " (" + coin.symbol + ")" + ": $" + coin.marketCap)),

            # Circulating Supply 
            InlineQueryResultArticle(
                id=uuid4(),
                title=("Circulating Supply"),
                description=coin.supply + " " + coin.symbol,
                thumb_url=("https://i.imgur.com/vXAN23U.png"),
                input_message_content=InputTextMessageContent("Circulating Supply of " + coin.name + " (" + coin.symbol + ")" + ": " + coin.supply + " " + coin.symbol)),

            # 24 Hour Percent Change
            InlineQueryResultArticle(
                id=uuid4(),
                title=("Percent Change (24 hours)"),
                description=coin.percentChange + "%",
                thumb_url=("https://imgur.com/iAoXFQc.png"),
                input_message_content=InputTextMessageContent("24 Hour Change in " + coin.name + " (" + coin.symbol + ")" + " Price: " + coin.percentChange + "%"))
        ]

    update.inline_query.answer(results)

def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)

if __name__ == "__main__":
    # Set these variable to the appropriate values
    NAME = "cryptora"

    # Port is given by Heroku
    PORT = int(os.environ.get('PORT', '5000'))

    # Enable logging
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Set up the Updater
    updater = Updater(token)
    dp = updater.dispatcher

    # Start the webhook
    updater.start_polling()
    updater.start_webhook(listen="0.0.0.0",
                          port=PORT,
                          url_path=token)
    updater.bot.setWebhook("http://cryptora.herokuapp.com/" + token)
    updater.idle()
# Cryptora 1.0

Cryptora is an easy-to-use Telegram bot service that can retrieve cryptocurrency data and news on demand for you, or your Telegram group.

## Features

*Refer to "Supported Commands" to see how to use these features.*

- **Look up cryptocurrencies.** Find the price (and other useful data) of thousands of cryptocurrencies, just by typing the name or the shorthand abbreviation.
- **Get historical data.** Find the low, high, opening, and closing price of thousands of cryptocurrencies on a given date, as well as the market capitalization.
- **Get real-time exchange data from GDAX.** See the trading price of Bitcoin, Litecoin, Ethereum, and Bitcoin Cash on GDAX, one of the leading cryptocurrency exchanges.
- **Calculations made easy.** Instantly convert cryptocurrency amounts to U.S. dollars, and vice versa.
- **Browse the latest cryptocurrency news.** Read and share the 10 latest headlines from Coindesk.com.
- **View the rankings.** See the top cryptocurrencies and their prices at any given moment, sorted by market capitalization.

## Using Cryptora

Using Cryptora is easy. In any Telegram chat, simply type `@CryptoraBot` and then any of the commands below. The requested information will pop up as a list on your screen, and you can tap on a result to share it with your chat. You can also create a new private chat with Cryptora if you'd like to interact with it separately.

## Supported Commands

In a Telegram chat, type `@CryptoraBot` and then any of these commands to use Cryptora:

- `[cryptocurrency]` – Type the name of any cryptocurrency, and Cryptora will retrieve essential information (price, market cap, circulating supply, and 24 hour percent change) and display it in a list. You can also type the cryptocurrency's shorthand abbreviation. For example, you can type `bitcoin` or `BTC` to get essential information about Bitcoin. The bot is not case sensitive, so you can type in any valid cryptocurrency name or its symbol in lower case or upper case.

- `news` - Retrieve the latest 10 articles from CoinDesk.com and display them in a list. You can choose to share the article with your chat, or you can browse the latest cryptocurrency headlines. 

- `gdax` - Retrieve the trading price of Bitcoin, Bitcoin Cash, Litecoin, and Ethereum from the GDAX trading exchange.

- `[cryptocurrency] [date]` - Type this command, replacing `[cryptocurrency]` with your desired cryptocurrency, and `[date]` with a date formatted in `MM/DD/YYYY` format (or `Month Day, Year` format), and Cryptora will retrieve the high, low, opening, and closing price of the cryptocurrency on that date, if data is available. You can also type in relative dates, so typing `bitcoin 2 days ago` will get you historical pricing data for Bitcoin 2 days prior to whatever the current date is. You can do this for months, years, and days. If pricing data does not exist for a specified date, the bot will return nothing.

- `top [x]` - Type this command (replace `[x]` with any number less than or equal to 50) to see the top *x* cryptocurrencies, ranked by their market capitalization.

- `[x] [cryptocurrency]` - Type this command (replace `[x]` with any number, and `[cryptocurrency]` with your desired cryptocurrency) to instantly convert an amount of cryptocurrency to U.S. dollars.

- `$[x] [cryptocurrency]` - Type this command (replace `[x]` with any number, and `[cryptocurrency]` with your desired cryptocurrency) to instantly convert an amount of U.S. dollars to the desired cryptocurrency.

- `help` - You can type `help` in Cryptora to get a list of the supported commands there.

## How it was built

Cryptora was built using the [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) framework. Data is retrieved from a variety of sources, using a combination of API access and webscraping. News articles are retrieved from [CoinDesk](http://coindesk.com) through its RSS feed. The bot is hosted on RedHat OpenShift.
 
## Acknowledgements and Notes

Special thanks to Michael Yousif (@mjyousif) and Augustine Osagie (@osagie98) for testing my bot in its beta stages and helping me with the deployment process.

Cryptora's feature set would not have been possible without the following Python packages: Dateparser, Feedparser, BeautifulSoup4, Datefinder, and gdax. Thank you to the developers who have created and maintained these amazingly useful modules.

And finally, **please invest responsibly.**

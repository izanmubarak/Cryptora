# Cryptora

Cryptora is an easy-to-use Telegram bot that can retrieve cryptocurrency data and news on demand.

<p align="center">
  <img src="https://media.giphy.com/media/jRBB6gAu4PBSaXCyqw/giphy.gif">
</p>

## Status

Cryptora's codebase has been updated to Python 3.10+ and modern dependencies.

Pull requests are welcome for providing general improvements.

## Requirements

- Python 3.10 or higher
- A CoinMarketCap API key
- A CoinDesk API key
- A Telegram Bot API token

## Features

*Refer to "Supported Commands" to see how to use these features.*

- **Look up cryptocurrencies.** Find the price (and other useful data) of thousands of cryptocurrencies, just by typing the name or the shorthand abbreviation.
- **Get historical data.** Find the low, high, opening, and closing price of thousands of cryptocurrencies on a given date, as well as the market capitalization.
- **See global statistics.** See statistics across all cryptocurrencies, including the global market cap, Bitcoin's percentage share of the global market cap, the number of active currencies, and more.
- **Calculations made easy.** Instantly convert between cryptocurrency and U.S. dollars.
- **Browse the latest cryptocurrency news.** Read and share news from a variety of cryptocurrency news sites.
- **View the rankings.** See the top cryptocurrencies and their prices at any given moment, sorted by market capitalization.

## Usage

Once you have deployed Cryptora – or have created a local instance – type the username of the instance in a Telegram chat, followed by any of these commands to use Cryptora:

- `[cryptocurrency]` – Type the name of any cryptocurrency, and Cryptora will retrieve essential information (price, market cap, circulating supply, and 24 hour percent change) and display it in a list. You can also type the cryptocurrency's symbol. For example, you can type `bitcoin` or `BTC` to get essential information about Bitcoin. The bot is not case sensitive, so you can type in any valid cryptocurrency name or its symbol in lower case or upper case. You can also type multiple cryptocurrencies, separated by commas, and send a list of cryptocurrency prices, percent changes, or market capitalizations in a single message. Cryptora automatically filters out duplicate and invalid entries. So, typing `xrp, iota, xmr, nano, bitcoin` will get you a list of their prices, market capitalizations, and percent changes that you can share with a chat.

- `news` - Retrieve the latest headlines from a variety of cryptocurrency news sites - aggregated by CryptoCompare – and display them in a list. You can choose to share the article with your chat, or you can browse the latest cryptocurrency headlines.

- `global` - Retrieve global statistics from CoinMarketCap, including the total market capitalization, the total 24 hour volume, bitcoin's dominance, and the number of active cryptocurrencies and markets.

- `[cryptocurrency] [date]` - Type this command, replacing `[cryptocurrency]` with your desired cryptocurrency, and `[date]` with a date formatted in `MM/DD/YYYY` format (or `Month Day, Year` format), and Cryptora will retrieve the high, low, opening, and closing price - as well as the market capitalization - of the cryptocurrency on that date, if data is available. Relative dates work as well, so typing `ethereum 2 weeks ago` or `ethereum yesterday` will get you information about ethereum two weeks ago and yesterday, respectively. Note that for relative dates, your numerical value must be a numeral and not a word - for example, `ethereum two weeks ago` will not work, while `ethereum 2 weeks ago` will.

- `top [x]` - Type this command (replace `[x]` with any number less than or equal to 50) to see the top *x* cryptocurrencies, ranked by their market capitalization.

- `[x] [cryptocurrency]` - Type this command (replace `[x]` with any number, and `[cryptocurrency]` with your desired cryptocurrency) to instantly convert an amount of cryptocurrency to U.S. dollars.

- `$[x] [cryptocurrency]` - Type this command (replace `[x]` with any number, and `[cryptocurrency]` with your desired cryptocurrency) to instantly convert an amount of U.S. dollars to the desired cryptocurrency.

Cryptora will alert you if it detects an invalid command. A valid command will display a list of shareable entries on your screen.

## How it was built

Cryptora is a Python 3 program. It was built using the [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) framework (v21+). Data is retrieved from [CoinMarketCap](https://coinmarketcap.com), using a combination of API access and webscraping. News articles are retrieved from [CryptoCompare](https://cryptocompare.com). The bot can be hosted using a Docker container.

## Acknowledgements

Cryptora's feature set would not have been possible without the following Python packages: Dateparser, BeautifulSoup4, and Datefinder. Thank you to the developers who have created and maintained these super useful modules.

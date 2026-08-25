# Cryptora

Cryptora is an easy-to-use Telegram bot that can retrieve cryptocurrency data and news on demand.

## Status

Cryptora's codebase has been updated to Python 3.10+ and modern dependencies. Pull requests are welcome for providing general improvements.

The official instance of Cryptora is live (`@CryptoraBot`), and available for use on Telegram by anyone as an inline bot.

## Requirements

- Python 3.10 or higher
- A Telegram Bot API token
- A CoinMarketCap API key
- A Financial Modeling Prep API key
- A Mistral API key (Optional: required for natural language parsing including relative dates)

## Features

*Refer to "Supported Commands" to see how to use these features.*

- **(New) Ask naturally, in any language:** If a query doesn't match any of the commands below, Cryptora uses a fast and lightweight LLM to work out which feature you meant, so you don't have to remember the exact syntax. Works across languages.
- **(New) Live ticker:** Add Cryptora to a group chat and it can create and periodically update a "price ticker" of a list of cryptocurrencies. Pin the message so that you always have an eye on the latest prices.
- **Look up cryptocurrencies:** Find the price (and other useful data) of thousands of cryptocurrencies, just by typing the name or the shorthand abbreviation.
- **Get historical data:** Find the OHLCV data for select cryptocurrencies for a given date.
- **See global market statistics.** See statistics for the whole crypto market.
- **Quick USD-crypto calculations:** Convert between U.S. dollars and any cryptocurrency.
- **Browse the latest cryptocurrency news:** Read and share news from CoinDesk and CoinTelegraph.
- **View the rankings:** See the top cryptocurrencies sorted by market capitalization.

## Usage

Type `@CryptoraBot` (or the username of your local instance) into Telegram followed by any of these commands:

- `[cryptocurrency]` – Type the name of any cryptocurrency or its symbol, and Cryptora will retrieve essential information (price, market cap, circulating supply, and 24 hour percent change) and display it in a list. 
  - This is not case sensitive, so you can type in any valid cryptocurrency name or its symbol in lower case or upper case. 
  - You can also a comma-separated list of cryptocurrencies and send a list of their prices, 24-hour percent changes, or market capitalizations in a single message. Cryptora automatically filters out duplicate and invalid entries.

- `ticker [cryptocurrencies]` - Cryptora can create and update a message every minute with the latest price of a list of cryptocurrencies. Pin the message for easy access. 
  - If using in a group chat, this requires you to add Cryptora as a member. Only admins may start or stop the ticker.

- `news` - Retrieve the latest headlines from CoinDesk and CoinTelegraph and display them in a list. Tapping on any of the articles sends the article's URL in the chat.

- `global` - Retrieve global crypto market statistics from CoinMarketCap, including the total market capitalization, the total 24 hour volume, Bitcoin and Ethereum's dominance, and the number of active cryptocurrencies and markets.

- `[cryptocurrency] [date]` - If available, Cryptora will retrieve the cryptocurrency's OHLCV data for the specified date. Most date formats are supported, as are relative dates (e.g. `ethereum 2 weeks ago` or `bitcoin yesterday`)

- `top [x]` - Type this command (replace `[x]` with any number less than or equal to 50) to see the top *x* cryptocurrencies ranked by market capitalization.

- `[x] [cryptocurrency]` - Type this command (replace `[x]` with any number, and `[cryptocurrency]` with your desired cryptocurrency) to convert an amount of cryptocurrency to U.S. dollars.
  - The reverse works as well: typing `$[x] [cryptocurrency]` will convert an amount of U.S. dollars to the desired cryptocurrency.
  - These are estimates only and should not be used for serious calculations.

- **Anything else** - If your query doesn't match any of the commands above, Cryptora passes it to an LLM (Ministral 3B) to figure out which feature you're asking for. So `how much is half a bitcoin worth`, `what was ethereum trading at yesterday`, `show me the 20 biggest coins`, and `how is the market doing` all work. 
  - The first result tells you how your question was interpreted. This requires a `MISTRAL_TOKEN` in your environment or `.env` file; without one, Cryptora falls back to the typed commands above and reports that the currency was not found for anything else.

Cryptora will alert you if it detects an invalid command. A valid command will display a list of shareable entries on your screen.

## How it was built

Cryptora is a Python 3 program. It was built using the [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) framework (v21+). 

Data is retrieved from a variety of sources:
- Current pricing and market stats: [CoinMarketCap](https://coinmarketcap.com)
- Historical pricing: [FinancialModelingPrep](https://site.financialmodelingprep.com)
- News: [CoinDesk](https://www.coindesk.com) and [CoinTelegraph](https://cointelegraph.com)
- Natural language parsing: [Mistral AI](https://mistral.ai) (Ministral 3 3B)

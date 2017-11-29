# Cryptogram (beta 0.5.0)

Cryptogram is a Telegram bot service that can retrieve cryptocurrency prices on demand for you, or your Telegram group. 

**How it was built**

Cryptogram was built using the [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) framework, a powerful, easy-to-use platform for building Telegram bots in Python. Prices are retrieved from [CoinMarketCap](http://coinmarketcap.com) using the CoinMarketCap API. News articles are retrieved from the [CoinDesk](http://coindesk.com) RSS feed. The bot pulls the latest price of the chosen cryptocurrency from CoinMarketCap when it receives a request from the user.
 
**Using Cryptogram**

Using Cryptogram is super simple. In any Telegram chat, simply type `@Crypto_Messenger_Bot` and then your command. You will receive the requested information in-line, and you can tap on a result to share it with your chat if you wish. You can also create a new private chat with Cryptogram if you'd like to interact with it separately.

**Features**

*Refer to "Supported Commands" to see how to use these features.*

- **Cryptocurrency Lookup.** Find the price (and other useful data) of thousands of cryptocurrencies, just by typing the name or the shorthand abbreviation.
- **CryptoCalculator.** Instantly convert cryptocurrency amounts to U.S. dollars, and vice versa.
- **News Feed.** Read and share the 10 latest headlines from Coindesk.com.
- **Rankings.** See the top cryptocurrencies, sorted by market capitalization.

**Supported Commands**

Type `@Crypto_Messenger_Bot` and then any of these commands (no need to press send) to use Cryptogram:

- `[Cryptocurrency Name]` – Type the name of any cryptocurrency, and Cryptogram will retrieve essential information (price, market cap, circulating supply, and 24 hour percent change) and display it in a list. You can also type the cryptocurrency's shorthand abbreviation. For example, you can type `bitcoin` or `BTC` to get essential information about Bitcoin.

- `news` - Cryptogram will retrieve the latest 10 articles from CoinDesk.com and display them in a list. You can choose to share the article with your chat, or you can peruse through the headlines.

- `top x` - Type this command (replace x with any number less than or equal to 50) to see the top *x* cryptocurrencies, ranked by their market capitalization.

- `x [Cryptocurrency Name]` - Type this command (replace x with any number, and `[Cryptocurrency Name]` with your desired cryptocurrency) to instantly convert an amount of cryptocurrency to U.S. dollars.

- `$[x] [Cryptocurrency Name]` - Type this command (replace x with any number, and `[Cryptocurrency Name]` with your desired cryptocurrency) to instantly convert an amount of U.S. dollars to the desired cryptocurrency.



# Cryptogram (beta 0.2.0)

Cryptogram is a Telegram bot service that can retrieve cryptocurrency prices (Bitcoin, Litecoin, and Ethereum) on demand for you, or your Telegram group. 

**How it was built**

Cryptogram was built using the [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) framework, a powerful, easy-to-use platform for building Telegram bots in Python. Prices are retrieved from [CoinMarketCap](coinmarketcap.com) using a web-scraper implemented in BeautifulSoup4. The bot pulls the latest price of the chosen cryptocurrency from CoinMarketCap when it receives a request from the user.
 
**Adding Cryptogram to your group chat**

Adding Cryptogram to your group chat is easy. Search for the username *@Crypto_Messenger_Bot* and add the bot titled "Cryptogram." Once added, you can immediately begin asking the bot commands (which are listed when you type the forward slash character) and see the prices of your favorite cryptocurrency.

Alternatively, if you'd like to interact with Cryptogram on your own, you can also create a new private chat with Cryptogram.

**Supported Commmands**

- `/btc`: Will retrieve the price of one bitcoin (BTC).
- `/ltc`: Will retrieve the price of one litecoin (LTC).
- `/eth`: Will retrieve the price of one ethereum (ETH).

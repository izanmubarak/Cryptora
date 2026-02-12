# Hosting Cryptora 

This document provides some guidance on how to host Cryptora.

## The `tokens.txt` file

Hosting Cryptora – locally or on a server platform such as AWS – requires you to generate a `tokens.txt` file which contains two token strings: the token that Telegram generated for you when you created your bot through BotFather, and the token that CoinMarketCap generates for you in order for you to use their API. In this folder, you'll see a `tokens_sample.txt` file that you can use as a template, but the format for `tokens.txt` is below:

```
CMC_TOKEN==Your_CMC_API_token_here
BOT_TOKEN==Your_BotFather_token_here
COINDESK_TOKEN==Your_CoinDesk_Data_API_token_here
```

You need only copy and paste the respective tokens after `CMC_TOKEN==`, `BOT_TOKEN==`, and `COINDESK_TOKEN==`. Do not put quotation marks or anything around the tokens. Also, ensure that there is **no newline** at the end of the file - this will throw errors when you attempt to run the program.

Make sure that `tokens.txt` is in the root Cryptora folder, not the "Deployment" folder that `tokens_sample.txt` is in.

## Running Cryptora 

Once you have created your `tokens.txt` file and placed it in the root Cryptora folder, you can start the bot by typing `python app.py`. The bot will automatically retrieve and use the tokens from the `tokens.txt` file if you have provided valid tokens. If it doesn't, you may get a `KeyError` saying that the bot cannot find a `[data]` dictionary (this is usually if you have provided an invalid CoinMarketCap API token). python-telegram-bot will throw a self-explanatory error if you provide an invalid bot token.

The bot will run indefinitely within the terminal, until you force stop it (Ctrl-C).

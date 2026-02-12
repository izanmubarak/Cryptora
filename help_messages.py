# Cryptora - Public Repository
# Displays help messages to the user.

from telegram import InlineQueryResultArticle, ParseMode, InputTextMessageContent
from uuid import uuid4


def get_help_messages():
    results = [
        InlineQueryResultArticle(
            id=uuid4(),
            title="Retrieve cryptocurrency prices",
            description='"BTC", "bitcoin"',
            thumb_url="https://imgur.com/joQ2gGR.png",
            input_message_content=InputTextMessageContent(
                "To get information about a cryptocurrency, just type "
                "the name or the shorthand abbreviation. For example, "
                "if you want to see information about Ethereum, you "
                "can just type `ethereum` or `ETH` (case does not "
                "matter), and Cryptora will get up to the moment "
                "information about Ethereum for you. \n\nYou can "
                "also type the name of your cryptocurrency, followed "
                "by a date in MM/DD/YYYY format (or Month Day, Year "
                "format) to get historical pricing. Alternatively, "
                "you can type relative dates too \u2013 so typing "
                "`bitcoin 2 weeks ago` will get you the price of "
                "Bitcoin two weeks ago.",
                ParseMode.MARKDOWN,
            ),
        ),
        InlineQueryResultArticle(
            id=uuid4(),
            title="Convert between cryptocurrencies and U.S. dollars",
            description='"$2000 BTC", "50 BTC"',
            thumb_url="https://imgur.com/8XwhAWO.png",
            input_message_content=InputTextMessageContent(
                "Cryptora can convert cryptocurrency values to U.S. dollars. Just "
                "type in a cryptocurrency value \u2013 for instance, `50 ETH` "
                "\u2013 to see the USD value of 50 ETH. "
                "\n\nYou can also type in a U.S. dollar amount and follow "
                "that with a cryptocurrency to convert from dollars to a "
                "cryptocurrency. For example, `$50 ETH` will retrieve the "
                "quantity of Ethereum that $50 will get you.",
                ParseMode.MARKDOWN,
            ),
        ),
        InlineQueryResultArticle(
            id=uuid4(),
            title="Read the latest cryptocurrency headlines",
            description='"news"',
            thumb_url="https://imgur.com/FUX10Vi.png",
            input_message_content=InputTextMessageContent(
                "You can type `news` to get the ten latest headlines from CoinDesk.com "
                "in-line. Tap a link to send to your chat.",
                ParseMode.MARKDOWN,
            ),
        ),
        InlineQueryResultArticle(
            id=uuid4(),
            title="See the top cryptocurrencies",
            thumb_url="https://imgur.com/g6YajTp.png",
            description='"top"',
            input_message_content=InputTextMessageContent(
                "Type `top` to see the top 50 cryptocurrencies, ranked by "
                "their market capitalization. If you'd like to see "
                "a specific number of cryptocurrencies, you can type "
                "`top x` (where x \u2264 50) \u2013 so typing `top 20` will display "
                "the top 20 cryptocurrencies.",
                ParseMode.MARKDOWN,
            ),
        ),
        InlineQueryResultArticle(
            id=uuid4(),
            title="See global stats",
            thumb_url="https://imgur.com/MyjXCmb.png",
            description='"global", "stats"',
            input_message_content=InputTextMessageContent(
                "Type `global` or `stats` to see a variety of up-to-the-minute global "
                "statistics, including the dominance of Bitcoin and Ethereum, the global "
                "cryptocurrency market capitalization, the number of cryptocurrencies on "
                "CoinMarketCap, and more.",
                ParseMode.MARKDOWN,
            ),
        ),
        InlineQueryResultArticle(
            id=uuid4(),
            title="Compare multiple cryptocurrencies",
            thumb_url="https://imgur.com/Gbnrtod.png",
            description='"btc, ltc, eth, dash, iota, xrp"',
            input_message_content=InputTextMessageContent(
                "You can search for multiple cryptocurrencies in a single "
                "query by typing a selection of cryptocurrencies "
                "(either their name, their symbol, or you can even "
                "mix it up), separated by commas. For example, you "
                "can type `btc, ethereum, omg, xrb, monero, ripple` to send the "
                "prices, market capitalizations, or percent change "
                "values of Bitcoin, Ethereum, OmiseGO, RaiBlocks, "
                "Monero, and Ripple in one message.",
                ParseMode.MARKDOWN,
            ),
        ),
    ]

    return results

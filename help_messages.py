from uuid import uuid4

from telegram import InlineQueryResultArticle, InputTextMessageContent


def get_help_messages():
    results = [
        InlineQueryResultArticle(
            id=uuid4(),
            title="New: Ask naturally",
            thumbnail_url="https://i.ibb.co/7JSfhJHX/Screenshot-2026-08-21-at-8-58-28-PM.png",
            description='"how much is half a bitcoin worth", "ethereum price today"',
            input_message_content=InputTextMessageContent(
                "If you don't remember the exact command, just describe what you want. "
                "Cryptora will work out which of its features you're asking for. Try "
                "`how much is half a bitcoin worth`, `show me the 20 biggest coins`, "
                "or `how is the market doing`. Cryptora will show you how it understood "
                "your question at the top of the results, so you can tell whether it got "
                "you right. Works with most languages.",
                "Markdown",
            ),
        ),
        InlineQueryResultArticle(
            id=uuid4(),
            title="Retrieve cryptocurrency prices",
            description='"BTC", "bitcoin"',
            thumbnail_url="https://imgur.com/joQ2gGR.png",
            input_message_content=InputTextMessageContent(
                "To get information about a cryptocurrency, just type "
                "the name or the symbol. For example, "
                "type `ethereum` or `ETH` to get up-to-date information about Ethereum.\n\nYou can "
                "also type the name of your cryptocurrency, followed "
                "by a date (in any format) to get OHLCV data for that coin where available. "
                "Relative dates work too, such as `bitcoin two weeks ago`.",
                "Markdown",
            ),
        ),
        InlineQueryResultArticle(
            id=uuid4(),
            title="Convert between cryptocurrencies and U.S. dollars",
            description='"$2000 BTC", "50 BTC"',
            thumbnail_url="https://imgur.com/8XwhAWO.png",
            input_message_content=InputTextMessageContent(
                "Convert cryptocurrency values to U.S. dollars by "
                "typing in a cryptocurrency value. For instance, `50 ETH` "
                "will calculate the value of 50 ETH in U.S. dollars. "
                "\n\nThe reverse works as well: `$50 ETH` will retrieve the "
                "quantity of Ethereum that $50 will get you.\n\n ***Note:*** These are estimates and"
                " shouldn't be used for serious calculations.",
                "Markdown",
            ),
        ),
        InlineQueryResultArticle(
            id=uuid4(),
            title="Read the latest cryptocurrency headlines",
            description='"news"',
            thumbnail_url="https://imgur.com/FUX10Vi.png",
            input_message_content=InputTextMessageContent(
                "Type `news` to retrieve headlines from CoinDesk and CoinTelegraph. "
                "Tap a link to send to your chat.",
                "Markdown",
            ),
        ),
        InlineQueryResultArticle(
            id=uuid4(),
            title="See the top cryptocurrencies",
            thumbnail_url="https://imgur.com/g6YajTp.png",
            description='"top"',
            input_message_content=InputTextMessageContent(
                "Type `top` to see the top 50 cryptocurrencies, ranked by "
                "their market capitalization. If you'd like to see "
                "a specific number of cryptocurrencies, you can type "
                "`top x` (where x \u2264 50).",
                "Markdown",
            ),
        ),
        InlineQueryResultArticle(
            id=uuid4(),
            title="See global stats",
            thumbnail_url="https://imgur.com/MyjXCmb.png",
            description='"global", "stats"',
            input_message_content=InputTextMessageContent(
                "Type `global` or `stats` to see global cryptocurrency market "
                "statistics, including the dominance of Bitcoin and Ethereum, the global "
                "market capitalization, the number of cryptocurrencies on "
                "CoinMarketCap, and more.",
                "Markdown",
            ),
        ),
        InlineQueryResultArticle(
            id=uuid4(),
            title="Compare multiple cryptocurrencies",
            thumbnail_url="https://imgur.com/Gbnrtod.png",
            description='"btc, ltc, eth, dash, iota, xrp"',
            input_message_content=InputTextMessageContent(
                "You can search for multiple cryptocurrencies in a single "
                "query by typing a selection of cryptocurrencies "
                "(either their name, their symbol, or you can even "
                "mix it up), separated by commas. For example, you "
                "can type `btc, ethereum, litecoin`.",
                "Markdown",
            ),
        ),
    ]

    return results

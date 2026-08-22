import html
from datetime import datetime
from uuid import uuid4

import feedparser
from telegram import InlineQueryResultArticle, InputTextMessageContent, LinkPreviewOptions

ARTICLE_LIMIT = 45
DIGEST_SIZE = 5
DIGEST_THUMBNAIL_URL = "https://imgur.com/FUX10Vi.png"
COINDESK_RSS = "https://www.coindesk.com/arc/outboundfeeds/rss/"
COINTELEGRAPH_RSS = "https://cointelegraph.com/rss"
INPUT_TIMESTAMP_FORMAT = "%a, %d %b %Y %H:%M:%S %z"
OUTPUT_TIMESTAMP_FORMAT = "%B %d, %Y %H:%M:%S %Z"


class NewsArticle:
    def __init__(self, data, source):
        self.title = data["title"]
        self.source = source
        self.published = datetime.strptime(data["published"], INPUT_TIMESTAMP_FORMAT)
        self.authors = ", ".join(
            [author["name"].removeprefix("Cointelegraph by ") for author in data["authors"]]
        )
        self.thumbnail_url = data["media_content"][0]["url"] if "media_content" in data else None
        self.url = data["link"]


# Headlines are arbitrary text, so the digest is constructed in HTML instead of Markdown
def build_digest(articles):
    lines = ["<b>Latest Cryptocurrency News</b>", ""]
    for index, article in enumerate(articles[:DIGEST_SIZE], start=1):
        title = html.escape(html.unescape(article.title))
        url = html.escape(article.url, quote=True)
        byline = f"{html.escape(article.authors)} ({html.escape(article.source)})"
        published = html.escape(article.published.strftime(OUTPUT_TIMESTAMP_FORMAT))
        lines.append(f'{index}. <a href="{url}">{title}</a> \u2022 {byline} \u2022 {published}')
    return "\n".join(lines)


def build_digest_result(articles):
    return InlineQueryResultArticle(
        id=uuid4(),
        title="Latest cryptocurrency news from CoinDesk and CoinTelegraph",
        description=f"Tap to send the top {min(len(articles), DIGEST_SIZE)} headlines.",
        thumbnail_url=DIGEST_THUMBNAIL_URL,
        input_message_content=InputTextMessageContent(
            build_digest(articles),
            "HTML",
            link_preview_options=LinkPreviewOptions(is_disabled=True),
        ),
    )


def get_news_list():
    coindesk_news = feedparser.parse(COINDESK_RSS)["entries"]
    cointelegraph_news = feedparser.parse(COINTELEGRAPH_RSS)["entries"]
    articles = [NewsArticle(article_metadata, "CoinDesk") for article_metadata in coindesk_news]
    articles += [
        NewsArticle(article_metadata, "CoinTelegraph") for article_metadata in cointelegraph_news
    ]
    articles.sort(key=lambda article: article.published, reverse=True)
    if not articles:
        return []

    results = [build_digest_result(articles)]
    for article in articles:
        results.append(
            InlineQueryResultArticle(
                id=uuid4(),
                description=f"{article.authors} ({article.source}) \u2022 {article.published.strftime(OUTPUT_TIMESTAMP_FORMAT)}",
                thumbnail_url=article.thumbnail_url,
                title=article.title,
                input_message_content=InputTextMessageContent(article.url),
            )
        )
    return results[:ARTICLE_LIMIT]

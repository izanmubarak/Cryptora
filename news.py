# Cryptora - Public Repository
# This file downloads news articles from the CryptoCompare API and displays them to the user.

from telegram import InlineQueryResultArticle, ParseMode, InputTextMessageContent
from uuid import uuid4
import requests


def get_news_data():
    """Fetch news data from the CryptoCompare API."""
    return requests.get("https://min-api.cryptocompare.com/data/v2/news/?lang=EN").json()["Data"]


class NewsArticle:

    def __init__(self, data):
        self.title = data["title"]
        self.subtitle = data["body"]
        self.url = data["url"]
        self.thumbnail_url = data["imageurl"]


def get_news_list():
    news_data = get_news_data()
    results = []
    for x in range(50):
        article = NewsArticle(news_data[x])
        results.append(
            InlineQueryResultArticle(
                id=uuid4(),
                description=article.subtitle,
                thumb_url=article.thumbnail_url,
                title=article.title,
                input_message_content=InputTextMessageContent(article.url),
            )
        )

    return results

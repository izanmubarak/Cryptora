# Cryptora - Public Repository
# This file downloads news articles from the CryptoCompare API and displays them to the user.

from telegram import InlineQueryResultArticle, ParseMode,InputTextMessageContent
from uuid import uuid4
import requests

newsData = (requests.get('https://min-api.cryptocompare.com/data/v2/news/?lang=EN').json())["Data"]

class NewsArticle:

	def __init__(self, rank):

		self.title = newsData[rank]['title']
		self.subtitle = newsData[rank]['body']
		self.URL = newsData[rank]['url']
		self.thumbnailURL = newsData[rank]['imageurl']

def get_news_list():

	results = []
	for x in range (0, 50):
		article = NewsArticle(x)
		results.append(
			InlineQueryResultArticle(
				id=uuid4(),
				description=(article.subtitle),
				thumb_url=article.thumbnailURL,
				title=(article.title),
				input_message_content=InputTextMessageContent(article.URL)),
		)

	return results


import feedparser
from telegram import InlineQueryResultArticle, ParseMode,InputTextMessageContent
from uuid import uuid4
import requests
from bs4 import BeautifulSoup

class NewsArticle:

	def __init__(self, rank, feed):

		self.title = self.get_article_title(rank, feed)
		self.subtitle = self.get_article_subtitle(rank, feed)
		self.URL = self.get_article_URL(rank, feed)
		self.thumbnailURL = self.get_image(self.URL)
		
	def get_article_URL(self, rank, feed):

		return feed['entries'][rank]['link']

	def get_article_title(self, rank, feed):

		return feed['entries'][rank]['title']

	def get_article_subtitle(self, rank, feed):

		return feed['entries'][rank]['description']

	def get_image(self, URL):
		
		page = requests.get(URL)
		soup = BeautifulSoup(page.content, 'html.parser')
		unformattedLink = str((soup.find_all('div', \
			class_="article-top-image-section"))).split(">")[0]
		return unformattedLink[69:][:-3]


def get_news_list():

	results = []
	feed = feedparser.parse("http://coindesk.com/feed")
	for x in range (0, 10):
		article = NewsArticle(x, feed)
		results.append(
			InlineQueryResultArticle(
				id=uuid4(),
				description=(article.subtitle),
				thumb_url=article.thumbnailURL,
				title=(article.title),
				input_message_content=InputTextMessageContent(article.URL)),
		)

	return results


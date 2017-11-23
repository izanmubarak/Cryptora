import requests, sys
import urllib2
from bs4 import BeautifulSoup
URL = "https://coinmarketcap.com"
page = requests.get(URL)
soup = BeautifulSoup(page.content, 'html.parser')

imgURL = str((soup.find_all('img', class_="sparkline")[4]))
print imgURL[44:-3]

import urllib
import urllib.parse

import requests
from bs4 import BeautifulSoup

from libs.core.databaseCore import databaseCore
from libs.core.databaseHelper import databaseHelper


class hdtrailersCore:

    def __init__(self, core, config):
        self._core = core
        self._config = config

        self._baseurl = 'http://www.hd-trailers.net/'

    def run(self):

        con = databaseHelper.getConnection(self._config, databaseCore.DB_NAME)
        self.getLatest(con)

        con.close()

    def getContent(self, url):
        url = urllib.parse.urljoin(self._baseurl, url)
        page = requests.get(url)
        return BeautifulSoup(page.content, 'html.parser')

    def getLatest(self, con):
        url = '/page/1/'

        while url is not None:
            url = self.parseLatestSite(con, url)

    def parseLatestSite(self, con, url):
        content = self.getContent(url)

        items = content.find_all('td', class_='indexTableTrailerImage')
        if items is not None:
            for item in items:
                link = item.find('a')
                if link is not None:
                    self.parseMovieSite(con, link['href'])

        navigation = content.find('div', class_='libraryLinks nav-links-top')
        nav_items = navigation.find_all('a', class_='startLink')
        if nav_items is not None:
            nav_item = filter(lambda p: 'Next' in p.getText() , nav_items)
            if nav_item is not None:
                return next(nav_item)['href']

        return None

    def parseMovieSite(self, con, url):
        if url is not None:
            content = self.getContent(url)

            movie_id = content.find('meta', name='movie_id')
            print(movie_id)

            link_block = content.find('table', class_='bottomTable')
            link_content = link_block.find_all(
                lambda tag: (tag.name == 'tr' and tag.has_attr('itemprop') and tag['itemprop'] == 'trailer') or
                            (tag.name == 'td' and tag.has_attr('class') and tag['class'][0] == 'bottomTableSet') or
                            (tag.name == 'td' and tag.has_attr('class') and tag['class'][0] == 'bottomTableFileSize')





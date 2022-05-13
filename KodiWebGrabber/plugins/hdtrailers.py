import random
import time
import urllib
import urllib.parse
import hashlib
import requests

from bs4 import BeautifulSoup
from decimal import Decimal, InvalidOperation

from KodiWebGrabber.libs.common import tools
from KodiWebGrabber.libs.core.Datalayer.DL_itemTags import DL_itemTags
from KodiWebGrabber.libs.core.Datalayer.DL_projects import DL_projects
from KodiWebGrabber.libs.core.Datalayer.DL_subitemTags import DL_subitemTags
from KodiWebGrabber.libs.core.databaseHelper import databaseHelper
from KodiWebGrabber.libs.core.databaseCore import databaseCore
from KodiWebGrabber.libs.core.Datalayer.DL_items import DL_items
from KodiWebGrabber.libs.core.Datalayer.DL_subItems import DL_subItems

__VERSION__ = '0.1.0'
__TYPE__ = 'plugin'
__TEMPLATE__ = 'hdtrailers'
__PID__ = 'HDTrailers.pid'


def register():
    if __TYPE__ == 'plugin':
        return {
            'name': __name__,
            'file': __file__,
            'template': __TEMPLATE__,
            'version': __VERSION__,
            'type': __TYPE__,
            'pid': __PID__
        }


class core:

    def __init__(self, config, addArgs):
        self._project_id = 0
        self._core_id = 'HDTRAILERS'
        self._config = config
        self._verbose = addArgs['verbose']
        self._page_begin = addArgs['page_begin']
        self._page_count = addArgs['page_count']
        self._suppressSkip = addArgs['suppress_skip']
        self._minWaittime = 0.5
        self._maxWaittime = 3.5
        waittime = addArgs['wait_time']
        if waittime is not None:
            self._minWaittime = waittime[0]
            self._maxWaittime = waittime[1]

        self._con = None
        self._requests_session = None

        self._addedShows = 0
        self._editedShows = 0
        self._addedTrailers = 0
        self._deletedTrailers = 0
        self._addedListItems = 0
        self._deletedListItems = 0

        self._itemTagDict = {}
        self._subitemTagDict = {}

        self._baseurl = 'http://www.hd-trailers.net/'

    def run(self):
        self._con = databaseHelper.getConnection(self._config, databaseCore.DB_NAME)

        self._project_id = DL_projects.getOrInsertItem(self._con, self._core_id)
        self._itemTagDict = self._getItemTags()
        self._subitemTagDict = self._getSubitemTags()
        self._requests_session = requests.Session()
        if self._getLatest():
            for url in ('/most-watched/', '/top-movies/', '/opening-this-week/', '/coming-soon/'):
                self._getList(url)

        self._con.close()

        if self._verbose:
            print(f'Added Shows: {self._addedShows}')
            print(f'Edited Shows: {self._editedShows}')
            print(f'Added Trailers: {self._addedTrailers}')
            print(f'Deleted Trailers: {self._deletedTrailers}')

    def _getLatest(self):
        url = f'/page/{self._page_begin}/'
        i = 0

        while url is not None:
            url = self._parseLatestSite(url)
            i += 1
            if self._page_count is not None:
                if i > self._page_count:
                    return False

        return True

    def _parseLatestSite(self, url):
        _hash, content = self._getContent(url)

        items = content.find_all('td', class_='indexTableTrailerImage')
        if items is not None:
            for item in items:
                link = item.find('a')
                if link is not None:
                    if not self._parseMovieSite(link['href']):
                        return None

        navigation = content.find('div', class_='libraryLinks nav-links-top')
        nav_items = navigation.find_all('a', class_='startLink')
        if nav_items is not None:
            nav_item = filter(lambda p: 'Next' in p.getText(), nav_items)
            if nav_item is not None:
                _item = next(nav_item, None)
                if _item is not None:
                    return _item['href']

        return None

    def _getContent(self, url):

        conn_tries = 0
        while True:

            try:
                wt = round(random.uniform(self._minWaittime, self._maxWaittime), 2)
                if wt > 0:
                    time.sleep(wt)
                url = urllib.parse.urljoin(self._baseurl, url)

                headers = {
                    'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
                }

                page = self._requests_session.get(url, timeout=10, headers=headers)
                _hash = hashlib.md5(page.content).hexdigest()
                content = BeautifulSoup(page.content, 'lxml')
                return _hash, content
            except requests.exceptions.ConnectionError as e:
                conn_tries += 1
                if conn_tries > 4:
                    print('exit [max retries are reached]')
                    raise e

                time.sleep(60)

    def _parseMovieSite(self, url):
        if url is not None:
            _hash, content = self._getContent(url)

            movie_id = self._getMovieId(content)
            movie = DL_items.getItem(self._con, self._project_id, str(movie_id))
            if not self._suppressSkip:
                if movie is not None and movie[1] == _hash:
                    return False

            _movie = self._getMovieDetails(movie_id, _hash, content)
            if _movie is not None:
                if movie is None:
                    item_id = self._insertMovie(_movie)
                    self._insertTrailers(item_id, _movie['trailers'])

                else:
                    item_id = movie[0]
                    self._deletedTrailers += DL_subItems.deleteSubItemByItemId(self._con, item_id)

                    self._updateMovie(item_id, _movie)
                    self._insertTrailers(item_id, _movie['trailers'])

            return True

    @staticmethod
    def _getMovieId(content):
        c = content.find('meta', attrs={'name': 'movie_id'})
        if c is not None:
            return c['content']

        return None

    def _getMovieDetails(self, movie_id, _hash, content):
        plot = None
        info = content.find('td', class_='topTableInfo')
        if info is not None:
            title = str(info.find('h1', class_='previewTitle').getText()).strip()
            plot_block = info.find('p', class_='previewDescription')
            if plot_block is not None:
                plot = str(plot_block.find('span').getText()).strip()
            poster = urllib.parse.urljoin("http:", info.find('img')['src'])
            latestDate, trailerCollection = self._getTrailerCollection(content)

            if tools.getLength(trailerCollection) > 0:
                return {
                    'movie_id': movie_id,
                    'hash': _hash,
                    'title': title,
                    'plot': plot,
                    'poster': poster,
                    'date': latestDate,
                    'trailers': trailerCollection
                }

    def _getTrailerCollection(self, content):
        trailer_collection = []
        trailer_links = []
        trailer_type = ''
        trailer_name = ''
        trailer_date = ''
        latest_date = None

        i = 0

        link_block = content.find('table', class_='bottomTable')
        link_content = link_block.find_all(
            lambda tag: (tag.name == 'tr' and tag.has_attr('itemprop') and tag['itemprop'] == 'trailer') or
                        (tag.name == 'td' and tag.has_attr('class') and tag['class'][0] == 'bottomTableSet') or
                        (tag.name == 'td' and tag.has_attr('class') and tag['class'][0] == 'bottomTableFileSize')
        )

        for link in link_content:
            if link.name == 'td' and link.has_attr('class') and link['class'][0] == 'bottomTableSet':
                if tools.getLength(trailer_links) > 0:
                    latest_date = tools.maxDate(trailer_date, latest_date)
                    trailer_collection.append(
                        {
                            'name': trailer_name,
                            'type': trailer_type,
                            'date': trailer_date,
                            'links': trailer_links
                        }
                    )
                    trailer_links = []

                trailer_type = self._getTrailerType(link)

            elif link.name == 'tr' and link.has_attr('itemprop') and link['itemprop'] == 'trailer':
                if tools.getLength(trailer_links) > 0:
                    latest_date = tools.maxDate(trailer_date, latest_date)
                    trailer_collection.append(
                        {
                            'name': trailer_name,
                            'type': trailer_type,
                            'date': trailer_date,
                            'links': trailer_links
                        }
                    )

                trailer_name = self._getTrailerName(link)
                trailer_date = self._getTrailerDate(link)
                trailer_links = self._getTrailerLinks(link)
                i = 0

            elif link.name == 'td' and link.has_attr('class') and link['class'][0] == 'bottomTableFileSize':
                size = self._getSize(link.getText())
                if size is not None and tools.getLength(trailer_links) > i:
                    trailer_links[i]['size'] = size
                    i += 1

        if tools.getLength(trailer_links) > 0:
            latest_date = tools.maxDate(trailer_date, latest_date)
            trailer_collection.append(
                {
                    'name': trailer_name,
                    'type': trailer_type,
                    'date': trailer_date,
                    'links': trailer_links
                }
            )

        if tools.getLength(trailer_collection) > 0:
            return latest_date, trailer_collection

        return None, None

    # TODO: _getTrailerType
    @staticmethod
    def _getTrailerType(link):
        return 'None'
        # trailer_type_block = link.find('h2')
        # if trailer_type_block is not None:
        #     _type = trailer_type_block.getText()
        #     if _type == 'Trailers':
        #         return subItemTagEnum.TRAILER
        #     elif _type == 'Clips':
        #         return subItemTagEnum.CLIP
        #
        # return subItemTagEnum.NONE

    @staticmethod
    def _getTrailerName(link):
        trailer_name_block = link.find('td', class_='bottomTableName')
        if trailer_name_block is not None:
            span_tag = trailer_name_block.find('span')
            if span_tag is not None:
                return span_tag.getText()

    @staticmethod
    def _getTrailerDate(link):
        trailer_date_block = link.find('td', class_='bottomTableDate')
        if trailer_date_block is not None:
            return tools.getDateTime(trailer_date_block.getText(), '%Y-%m-%d')

    def _getTrailerLinks(self, link):
        link_collection = []

        links = link.find_all('td', class_='bottomTableResolution')
        for trailer_link in links:
            a_tag = trailer_link.find('a')
            if a_tag is not None:
                url = a_tag['href']
                if self._validHoster(url):
                    link_collection.append(
                        {
                            'title': str(a_tag['title']).strip(),
                            'quality': a_tag.getText(),
                            'best_quality': False,
                            'size': None,
                            'url': url
                        }
                    )

        if tools.getLength(link_collection) > 0:
            link_collection[-1]['best_quality'] = True
            return link_collection

    @staticmethod
    def _validHoster(url):
        if 'yahoo-redir.php' in url:
            return False
        if 'www.youtube.com' in url:
            return False
        if 'cdn.videos.dolimg.com' in url:
            return False
        if 'avideos.5min.com' in url:
            return False

        return True

    @staticmethod
    def _getSize(value):
        if 'MB' in value:
            value = value.replace('MB', '')
            try:
                d = Decimal(value)
                return int(d * 1024 * 1024)
            except InvalidOperation:
                return 0

    def _insertMovie(self, movie):
        item = (
            self._project_id,
            movie['movie_id'],
            movie['hash'],
            movie['title'],
            movie['plot'],
            self._itemTagDict['None'],
            movie['poster'],
            tools.datetimeToString(movie['date'], '%Y-%m-%d %H:%M:%S')
        )

        row_count, item_id = DL_items.insertItem(self._con, item)
        self._addedShows += row_count
        return item_id

    def _addItemTag(self, _dict, tag):
        tag_id = DL_itemTags.getOrInsertItem(self._con, tag)
        _dict[tag] = tag_id

        return _dict

    def _getItemTags(self):
        _dict = {}
        _dict = self._addItemTag(_dict, 'None')

        return _dict

    def _addSubitemTag(self, _dict, tag):
        tag_id = DL_subitemTags.getOrInsertItem(self._con, tag)
        _dict[tag] = tag_id

        return _dict

    def _getSubitemTags(self):
        _dict = {}
        _dict = self._addSubitemTag(_dict, 'None')

        return _dict

import random
import time
import urllib
import urllib.parse
import hashlib
import requests

from bs4 import BeautifulSoup
from decimal import Decimal, InvalidOperation

from ..common import tools
from ..common.enums import *
from .Datalayer.DL_items import *
from .Datalayer.DL_subItems import *
from .Datalayer.DL_links import DL_links
from .databaseCore import databaseCore
from .databaseHelper import databaseHelper


def _getMovieId(content):
    c = content.find('meta', attrs={'name': 'movie_id'})
    if c is not None:
        return c['content']

    return None


def _getTrailerType(link):
    trailer_type_block = link.find('h2')
    if trailer_type_block is not None:
        _type = trailer_type_block.getText()
        if _type == 'Trailers':
            return subItemTagEnum.TRAILER
        elif _type == 'Clips':
            return subItemTagEnum.CLIP

    return subItemTagEnum.NONE


def _getTrailerName(link):
    trailer_name_block = link.find('td', class_='bottomTableName')
    if trailer_name_block is not None:
        span_tag = trailer_name_block.find('span')
        if span_tag is not None:
            return span_tag.getText()


def _getTrailerDate(link):
    trailer_date_block = link.find('td', class_='bottomTableDate')
    if trailer_date_block is not None:
        return tools.getDateTime(trailer_date_block.getText(), '%Y-%m-%d')


def _getTrailerLinks(link):
    link_collection = []

    links = link.find_all('td', class_='bottomTableResolution')
    for trailer_link in links:
        a_tag = trailer_link.find('a')
        if a_tag is not None:
            url = a_tag['href']
            if _validHoster(url):
                link_collection.append(
                    {
                        'title': a_tag['title'],
                        'quality': a_tag.getText(),
                        'best_quality': False,
                        'size': None,
                        'url': url
                    }
                )

    if tools.getLength(link_collection) > 0:
        link_collection[-1]['best_quality'] = True
        return link_collection


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


def _getSize(value):
    if 'MB' in value:
        value = value.replace('MB', '')
        try:
            d = Decimal(value)
            return int(d * 1024 * 1024)
        except InvalidOperation:
            return 0


def _getTrailerCollection(content):
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
            trailer_type = _getTrailerType(link)

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

            trailer_name = _getTrailerName(link)
            trailer_date = _getTrailerDate(link)
            trailer_links = _getTrailerLinks(link)
            i = 0

        elif link.name == 'td' and link.has_attr('class') and link['class'][0] == 'bottomTableFileSize':
            size = _getSize(link.getText())
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


def _getMovieDetails(movie_id, _hash, content):
    plot = None
    info = content.find('td', class_='topTableInfo')
    if info is not None:
        title = info.find('h1', class_='previewTitle').getText()
        plot_block = info.find('p', class_='previewDescription')
        if plot_block is not None:
            plot = plot_block.find('span').getText()
        poster = urllib.parse.urljoin("http:", info.find('img')['src'])
        latestDate, trailerCollection = _getTrailerCollection(content)

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


def _getList(item):
    t = item.find(lambda tag: tag.name == 'div')
    if t is not None:
        tagText = t.getText()

        if 'Most Watched Trailers This Week' == tagText:
            return listEnum.HDT_MOSTWATCHEDWEEK
        elif 'Most Watched Trailers Today' == tagText:
            return listEnum.HDT_MOSTWATCHEDTODAY
        elif 'Box Office Top 10 Movies' == tagText:
            return listEnum.HDT_TOPTEN
        elif 'Opening This Week' == tagText:
            return listEnum.HDT_OPENING
        elif 'Coming Soon' == tagText:
            return listEnum.HDT_COMINGSOON


class hdtrailersCore:

    def __init__(self, core, config, addArgs):
        self._core = core
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

        self._baseurl = 'http://www.hd-trailers.net/'

    def run(self):

        self._con = databaseHelper.getConnection(self._config, databaseCore.DB_NAME)
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
                    print('exit [max reties are reached]')
                    raise e

                time.sleep(60)

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

    def _getList(self, url):
        _hash, content = self._getContent(url)

        indexTable = content.find('table', class_='indexTable')
        if indexTable is not None:
            trItems = indexTable.find_all(lambda tag: tag.name == 'tr')
            if trItems is not None:
                lst = None
                count = 0
                for trItem in trItems:
                    if trItem.find('th', class_='mainHeading'):
                        lst = _getList(trItem)
                        self._deletedListItems += DL_lists.deleteList(self._con, lst.name)
                        count = 0

                    elif lst is not None:
                        items = trItem.find_all('td', class_='indexTableTrailerImage')
                        if items is not None:
                            for item in items:
                                link = item.find('a')
                                url = link['href']
                                _hash, _content = self._getContent(url)
                                movie_id = _getMovieId(_content)
                                item = DL_items.getItem(self._con, self._core.name, str(movie_id), _hash)
                                if item is not None:
                                    count += 1
                                    listItem = (
                                        lst.name,
                                        item[0],
                                        count
                                    )
                                    self._addedListItems += DL_lists.insertList(self._con, listItem)

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
                return next(nav_item)['href']

        return None

    def _parseMovieSite(self, url):
        if url is not None:
            _hash, content = self._getContent(url)

            movie_id = _getMovieId(content)
            movie = DL_items.getItem(self._con, self._core.name, str(movie_id))
            if not self._suppressSkip:
                if movie is not None and movie[1] == _hash:
                    return False

            _movie = _getMovieDetails(movie_id, _hash, content)
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

    def _insertMovie(self, movie):
        item = (
            self._core.name,
            movie['movie_id'],
            movie['hash'],
            movie['title'],
            movie['plot'],
            tagEnum.NONE.name,
            movie['poster'],
            tools.datetimeToString(movie['date'], '%Y-%m-%d %H:%M:%S')
        )

        row_count, item_id = DL_items.insertItem(self._con, item)
        self._addedShows += row_count
        return item_id

    def _updateMovie(self, item_id, movie):
        item = (
            movie['hash'],
            movie['title'],
            movie['plot'],
            tagEnum.NONE.name,
            movie['poster'],
            tools.datetimeToString(movie['date'], '%Y-%m-%d %H:%M:%S')
        )

        self._editedShows += DL_items.updateItem(self._con, item_id, item)

    def _insertTrailers(self, item_id, trailers):
        for trailer in trailers:
            item = (
                item_id,
                trailer['name'],
                trailer['type'].name,
                tools.datetimeToString(trailer['date'], '%Y-%m-%d %H:%M:%S'),
                None,
                None
            )

            row_count, subItem_id = DL_subItems.insertSubItem(self._con, item)
            self._addedTrailers += row_count

            for link in trailer['links']:
                item = (
                    subItem_id,
                    link['quality'],
                    link['best_quality'],
                    tools.getHoster(link['url']),
                    link['size'],
                    link['url'],
                )

                DL_links.insertLink(self._con, item)

import urllib
import urllib.parse

import requests
from bs4 import BeautifulSoup
import lxml
import cchardet
import hashlib
from decimal import Decimal, InvalidOperation

from libs.common import tools
from libs.common.enums import tagEnum, subItemTagEnum
from libs.core.Datalayer.DL_items import DL_items
from libs.core.Datalayer.DL_links import DL_links
from libs.core.Datalayer.DL_subItems import DL_subItems
from libs.core.databaseCore import databaseCore
from libs.core.databaseHelper import databaseHelper


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

    if len(link_collection) > 0:
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
            if len(trailer_links) > 0:
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
            if size is not None:
                trailer_links[i]['size'] = size
                i += 1

    if len(trailer_links) > 0:
        latest_date = tools.maxDate(trailer_date, latest_date)
        trailer_collection.append(
            {
                'name': trailer_name,
                'type': trailer_type,
                'date': trailer_date,
                'links': trailer_links
            }
        )

    if len(trailer_collection) > 0:
        return latest_date, trailer_collection


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

        if trailerCollection is not None and len(trailerCollection) > 0:
            return {
                'movie_id': movie_id,
                'hash': _hash,
                'title': title,
                'plot': plot,
                'poster': poster,
                'date': latestDate,
                'trailers': trailerCollection
            }


def _insertMovie(con, core, movie):
    item = (
        core.name,
        movie['movie_id'],
        movie['hash'],
        movie['title'],
        movie['plot'],
        tagEnum.NONE.name,
        movie['poster'],
        tools.datetimeToString(movie['date'], '%Y-%m-%d %H:%M:%S')
    )

    return DL_items.insertItem(con, item)


def _updateMovie(con, item_id, movie):
    item = (
        movie['hash'],
        movie['title'],
        movie['plot'],
        tagEnum.NONE.name,
        movie['poster'],
        tools.datetimeToString(movie['date'], '%Y-%m-%d %H:%M:%S')
    )

    DL_items.updateItem(con, item_id, item)


def _insertTrailers(con, item_id, trailers):
    for trailer in trailers:
        item = (
            item_id,
            trailer['name'],
            trailer['type'].name,
            tools.datetimeToString(trailer['date'], '%Y-%m-%d %H:%M:%S'),
            None,
            None
        )

        subItem_id = DL_subItems.insertSubItem(con, item)

        for link in trailer['links']:
            item = (
                subItem_id,
                link['quality'],
                link['best_quality'],
                tools.getHoster(link['url']),
                link['size'],
                link['url'],
            )

            DL_links.insertLink(con, item)


class hdtrailersCore:

    def __init__(self, core, config):
        self._core = core
        self._config = config

        self._baseurl = 'http://www.hd-trailers.net/'

    def run(self):

        con = databaseHelper.getConnection(self._config, databaseCore.DB_NAME)
        requests_session = requests.Session()
        self.getLatest(con, requests_session)

        con.close()

    def getContent(self, requests_session, url):
        url = urllib.parse.urljoin(self._baseurl, url)
        page = requests_session.get(url)
        _hash = hashlib.md5(page.content).hexdigest()
        content = BeautifulSoup(page.content, 'lxml')
        return _hash, content

    def getLatest(self, con, requests_session):
        url = '/page/1/'

        while url is not None:
            url = self.parseLatestSite(con, requests_session, url)

    def parseLatestSite(self, con, requests_session, url):
        _hash, content = self.getContent(requests_session, url)

        items = content.find_all('td', class_='indexTableTrailerImage')
        if items is not None:
            for item in items:
                link = item.find('a')
                if link is not None:
                    if not self.parseMovieSite(con, requests_session, link['href']):
                        return None

        navigation = content.find('div', class_='libraryLinks nav-links-top')
        nav_items = navigation.find_all('a', class_='startLink')
        if nav_items is not None:
            nav_item = filter(lambda p: 'Next' in p.getText(), nav_items)
            if nav_item is not None:
                return next(nav_item)['href']

        return None

    def parseMovieSite(self, con, requests_session, url):
        if url is not None:
            _hash, content = self.getContent(requests_session, url)

            movie_id = _getMovieId(content)
            movie = DL_items.getItem(con, self._core.name, str(movie_id))
            if movie is not None and movie[1] == _hash:
                return False

            _movie = _getMovieDetails(movie_id, _hash, content)
            if _movie is not None:
                if movie is None:
                    item_id = _insertMovie(con, self._core, _movie)
                    _insertTrailers(con, item_id, _movie['trailers'])

                else:
                    item_id = movie[0]
                    DL_subItems.deleteSubItemByItemId(con, item_id)

                    _updateMovie(con, item_id, _movie)
                    _insertTrailers(con, item_id, _movie['trailers'])

            return True


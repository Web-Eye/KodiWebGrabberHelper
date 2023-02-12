# -*- coding: utf-8 -*-
# Copyright 2022 WebEye
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import random
import time
import urllib
import urllib.parse
import hashlib

import requests

from bs4 import BeautifulSoup
from decimal import Decimal, InvalidOperation

from libs.common import tools
from libs.core.databaseHelper import databaseHelper
from libs.core.Datalayer.DL_itemTags import DL_itemTags
from libs.core.Datalayer.DL_links import DL_links
from libs.core.Datalayer.DL_listIdentifiers import DL_listIdentifiers
from libs.core.Datalayer.DL_lists import DL_lists
from libs.core.Datalayer.DL_projects import DL_projects
from libs.core.Datalayer.DL_qualities import DL_qualities
from libs.core.Datalayer.DL_subitemTags import DL_subitemTags
from libs.core.Datalayer.DL_items import DL_items
from libs.core.Datalayer.DL_subItems import DL_subItems
from libs.core.tmdbCore import tmdbCore

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

        self._tmdb = None

        self._itemTagDict = {}
        self._subitemTagDict = {}
        self._qualityDict = {}

        self._baseurl = 'http://www.hd-trailers.net/'

    def run(self):
        self._con = databaseHelper.getConnection(self._config)

        self._project_id = DL_projects.getOrInsertItem(self._con, self._core_id)
        self._itemTagDict = self._getItemTags()
        self._subitemTagDict = self._getSubitemTags()
        self._qualityDict = self._getQualityDict()
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
        order_id = 0

        while url is not None:
            url, order_id = self._parseLatestSite(url, order_id)
            i += 1
            if self._page_count is not None:
                if i > self._page_count:
                    return False

        return True

    def _parseLatestSite(self, url, order_id):
        _hash, content = self._getContent(url)

        items = content.find_all('td', class_='indexTableTrailerImage')
        if items is not None:
            for item in items:
                link = item.find('a')
                if link is not None:
                    success, order_id = self._parseMovieSite(link['href'], order_id)
                    if not success:
                        return None, None

        navigation = content.find('div', class_='libraryLinks nav-links-top')
        nav_items = navigation.find_all('a', class_='startLink')
        if nav_items is not None:
            nav_item = filter(lambda p: 'Next' in p.getText(), nav_items)
            if nav_item is not None:
                _item = next(nav_item, None)
                if _item is not None:
                    return _item['href'], order_id

        return None, None

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

    def _parseMovieSite(self, url, order_id):
        if url is not None:
            _hash, content = self._getContent(url)

            movie_id = self._getMovieId(content)
            movie = DL_items.getItem(self._con, self._project_id, str(movie_id))
            if not self._suppressSkip:
                if movie is not None and movie[1] == _hash:
                    return False, order_id

            _movie = self._getMovieDetails(movie_id, _hash, content)
            if _movie is not None:
                order_id += 1
                if movie is None:
                    item_id = self._insertMovie(_movie, order_id)
                    self._insertTrailers(item_id, _movie['trailers'])

                else:
                    item_id = movie[0]
                    self._deletedTrailers += DL_subItems.deleteSubItemByItemId(self._con, item_id)
                    self._updateMovie(item_id, _movie, order_id)
                    self._insertTrailers(item_id, _movie['trailers'])

            return True, order_id

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
            latestDate, lastestTrailerDate, trailerCollection = self._getTrailerCollection(content)
            _, poster = self._getAlternatePoster(title, plot, lastestTrailerDate, poster)

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
        latest_trailer_date = None

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
                    if trailer_type == 'TRAILER':
                        latest_trailer_date = tools.maxDate(trailer_date, latest_trailer_date)
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
                    if trailer_type == 'TRAILER':
                        latest_trailer_date = tools.maxDate(trailer_date, latest_trailer_date)
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
            if trailer_type == 'TRAILER':
                latest_trailer_date = tools.maxDate(trailer_date, latest_trailer_date)
            trailer_collection.append(
                {
                    'name': trailer_name,
                    'type': trailer_type,
                    'date': trailer_date,
                    'links': trailer_links
                }
            )

        if tools.getLength(trailer_collection) > 0:
            return latest_date, latest_trailer_date, trailer_collection

        return None, None, None

    @staticmethod
    def _getTrailerType(link):
        trailer_type_block = link.find('h2')
        if trailer_type_block is not None:
            _type = trailer_type_block.getText()
            if _type == 'Trailers':
                return 'TRAILER'
            elif _type == 'Clips':
                return 'CLIP'
        return 'NONE'

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

    def _insertMovie(self, movie, order_id):
        item = (
            self._project_id,
            movie['movie_id'],
            movie['hash'],
            movie['title'],
            movie['plot'],
            self._itemTagDict['None'],
            movie['poster'],
            tools.datetimeToString(movie['date'], '%Y-%m-%d %H:%M:%S'),
            order_id
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
        _dict = self._addSubitemTag(_dict, 'NONE')
        _dict = self._addSubitemTag(_dict, 'TRAILER')
        _dict = self._addSubitemTag(_dict, 'CLIP')

        return _dict

    def _addQualityEntity(self, _dict, entity):
        entity_id = DL_qualities.getOrInsertItem(self._con, entity)
        _dict[entity] = entity_id

        return _dict

    def _getQualityDict(self):
        _dict = {}
        _dict = self._addQualityEntity(_dict, '480p')
        _dict = self._addQualityEntity(_dict, '720p')
        _dict = self._addQualityEntity(_dict, '1080p')

        return _dict

    def _insertTrailers(self, item_id, trailers):
        for trailer in trailers:
            item = (
                item_id,
                trailer['name'],
                self._subitemTagDict[trailer['type']],
                tools.datetimeToString(trailer['date'], '%Y-%m-%d %H:%M:%S'),
                None,
                None
            )

            row_count, subItem_id = DL_subItems.insertSubItem(self._con, item)
            self._addedTrailers += row_count

            for link in trailer['links']:
                item = (
                    subItem_id,
                    self._qualityDict[link['quality']],
                    link['best_quality'],
                    tools.getHoster(link['url']),
                    link['size'],
                    link['url'],
                )

                DL_links.insertLink(self._con, item)

    def _updateMovie(self, item_id, movie, order_id):
        item = (
            movie['hash'],
            movie['title'],
            movie['plot'],
            self._itemTagDict['None'],
            movie['poster'],
            tools.datetimeToString(movie['date'], '%Y-%m-%d %H:%M:%S'),
            order_id
        )

        self._editedShows += DL_items.updateItem(self._con, item_id, item)

    def _getList(self, url):
        _hash, content = self._getContent(url)

        indexTable = content.find('table', class_='indexTable')
        if indexTable is not None:
            trItems = indexTable.find_all(lambda tag: tag.name == 'tr')
            if trItems is not None:
                lst_id = None
                count = 0
                for trItem in trItems:
                    if trItem.find('th', class_='mainHeading'):
                        lst_id = self._getListId(trItem)
                        self._deletedListItems += DL_lists.deleteList(self._con, self._project_id, lst_id)
                        count = 0

                    elif lst_id is not None:
                        items = trItem.find_all('td', class_='indexTableTrailerImage')
                        if items is not None:
                            for item in items:
                                link = item.find('a')
                                url = link['href']
                                _hash, _content = self._getContent(url)
                                movie_id = self._getMovieId(_content)
                                item = DL_items.getItem(self._con, self._project_id, str(movie_id), _hash)
                                if item is not None:
                                    count += 1
                                    listItem = (
                                        self._project_id,
                                        lst_id,
                                        item[0],
                                        count
                                    )
                                    self._addedListItems += DL_lists.insertList(self._con, listItem)

    def _getListId(self, item):
        t = item.find(lambda tag: tag.name == 'div')
        if t is not None:
            tagText = t.getText()

            lstName = None

            if 'Most Watched Trailers This Week' == tagText:
                lstName = 'MOSTWATCHEDWEEK'
            elif 'Most Watched Trailers Today' == tagText:
                lstName = 'MOSTWATCHEDTODAY'
            elif 'Box Office Top 10 Movies' == tagText:
                lstName = 'TOPTEN'
            elif 'Opening This Week' == tagText:
                lstName = 'OPENING'
            elif 'Coming Soon' == tagText:
                lstName = 'COMINGSOON'

            if lstName is not None:
                return DL_listIdentifiers.getOrInsertItem(self._con, lstName)

        return None

    def _getAlternatePoster(self, title, plot, order_date, default):

        if self._tmdb is None:
            self._tmdb = tmdbCore()

        movie = self._tmdb.searchMovie(title)
        if movie is not None and movie['success']:
            posterPath = self._tmdb.getPosterPath(movie, title, plot, order_date)
            if posterPath is not None:
                url = self._tmdb.getPosterUrl(posterPath)
                if url is not None:
                    return True, url

        return False, default

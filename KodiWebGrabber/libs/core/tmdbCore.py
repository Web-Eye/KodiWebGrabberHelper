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

import json
import requests

from libs.common import tools

_API_KEY = 'af3a53eb387d57fc935e9128468b1899'

_BASE_URL = 'https://api.themoviedb.org/3/{}'
_CONFIGURATION_URL = _BASE_URL.format('configuration{}')
_MOVIE_SEARCH_URL = _BASE_URL.format('search/movie/{}')

_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
}


class tmdbCore:

    def __init__(self):
        self._configuration = self._getConfiguration()
        self._posterBaseUrl = self._getPosterBaseUrl()

    @staticmethod
    def _getConfiguration():
        url = _CONFIGURATION_URL.format('?api_key={}').format(_API_KEY)

        page = requests.get(url, headers=_HEADERS)
        return json.loads(page.content)

    @staticmethod
    def searchMovie(title):
        url = _MOVIE_SEARCH_URL.format('?query={}').format(title) + '&api_key={}'.format(_API_KEY)

        page = requests.get(url, headers=_HEADERS)
        return json.loads(page.content)

    @staticmethod
    def getPosterPath(page, title, plot, order_date):

        valid_movies = list(filter(lambda item: 'title' in item and 'overview' in item, page['results']))
        if len(valid_movies) > 0:
            exact_list = list(filter(lambda item: item['title'].lower() == title.lower(), valid_movies))
            if len(exact_list) == 0:
                exact_list = valid_movies

            valid_movies = exact_list
            exact_list = list(
                filter(lambda item: 'release_date' not in item or item['release_date'] == '' or
                                abs(order_date - tools.getDateTime(item['release_date'], '%Y-%m-%d')).days < 271,
                       valid_movies))

            size = len(exact_list)
            if size == 0:
                return tmdbCore._getPosterPath(valid_movies, plot)
            elif size == 1:
                return exact_list[0]['poster_path']
            else:
                return tmdbCore._getPosterPath(exact_list, plot)

        return None

    @staticmethod
    def _getPosterPath(movie_list, plot):
        resItem = None

        for item in movie_list:
            resItem = tmdbCore._getHighestItem(item, plot, resItem)

        if resItem is not None:
            return resItem['poster_path']

        return None

    @staticmethod
    def _getHighestItem(item, plot, compareItem):
        plot = plot.lower()
        item_plot = item['overview'].lower()
        score = tmdbCore._compare_content(plot, item_plot)
        score += tmdbCore._compare_words(plot, item_plot)
        item['score'] = score

        if score > 0:
            if compareItem is None:
                return item

            if score > compareItem['score']:
                return item

        return compareItem

    @staticmethod
    def _compare_content(plot1, plot2):
        retValue = 0
        plot1_cleared = tmdbCore._clearString(plot1)
        plot2_cleared = tmdbCore._clearString(plot2)

        plot1_words = plot1_cleared.split(' ')
        plot1_count = len(plot1_words)

        idx = 0

        while idx < plot1_count:
            word_idx = 0
            sequence = plot1_words[idx]
            if sequence in plot2_cleared:
                while sequence in plot2_cleared:
                    if idx + word_idx + 1 < plot1_count:
                        sequence += ' ' + plot1_words[idx + word_idx + 1]
                        if sequence in plot2_cleared:
                            word_idx += 1
                    else:
                        break

                retValue += 2 * word_idx
                idx += word_idx + 1

            else:
                idx += 1

        if retValue < 14:
            retValue = 0

        return retValue

    @staticmethod
    def _clearString(plot):
        plot = plot.replace(',', '')
        plot = plot.replace('.', '')
        plot = plot.replace(';', '')
        plot = plot.replace('-', '')

        plot = tools.removeBrackets(plot)
        return plot

    @staticmethod
    def _compare_words(plot1, plot2):
        retValue = 0
        plot1_cleared = tmdbCore._clearString1(plot1)
        plot2_cleared = ' ' + tmdbCore._clearString1(plot2) + ' '

        plot1_words = plot1_cleared.split(' ')
        plot2_words = plot2_cleared.split(' ')

        plot1_count = 0
        plot2_count = 0

        for word in plot1_words:
            word = ' ' + word + ' '
            if word in ' is a an and with of to he she it his her for be because about this when that but are ' \
                       'aren\'t in ':
                continue

            plot1_count += 1
            if word in plot2_cleared:
                retValue += 0.5

        if retValue > 0:

            for word in plot2_words:
                word = ' ' + word + ' '
                if word in ' is a an and with of to he she it his her for be because about this when that but are ' \
                           'aren\'t in ':
                    continue

                plot2_count += 1

            count = min(plot1_count, plot2_count)
            if (retValue * 2) / count < 0.35:
                retValue = 0

        return retValue

    @staticmethod
    def _clearString1(plot):
        plot = plot.replace(',', '')
        plot = plot.replace('.', '')
        plot = plot.replace(';', '')
        plot = plot.replace('-', '')
        plot = plot.replace('(', '')
        plot = plot.replace(')', '')
        plot = plot.replace('[', '')
        plot = plot.replace(']', '')

        while plot.find('  ') > -1:
            plot = plot.replace('  ', ' ')

        return plot

    def _getPosterBaseUrl(self):
        if self._configuration is not None:
            images = self._configuration['images']
            if images is not None:
                base_url = images['base_url']
                return base_url + 'w500'

    def getPosterUrl(self, posterPath):
        if posterPath is not None:
            return self._posterBaseUrl + posterPath

        return None

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
    def getPosterPath(page):
        if page['results'] is not None and len(page['results']) > 0:
            return page['results'][0]['poster_path']

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

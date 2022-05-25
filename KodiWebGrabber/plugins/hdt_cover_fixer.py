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

__VERSION__ = '0.1.0'
__TYPE__ = 'plugin'
__TEMPLATE__ = 'hdtcf'
__PID__ = 'HDTCF.pid'

from libs.core.Datalayer.DL_projects import DL_projects
from libs.core.Datalayer.DL_subitemTags import DL_subitemTags
from libs.core.databaseCore import databaseCore
from libs.core.databaseHelper import databaseHelper
from libs.core.tmdbCore import tmdbCore


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
        self._core_id = 'HDTRAILERS'
        self._config = config
        self._con = None
        self._tmdb = None

    def run(self):
        self._con = databaseHelper.getConnection(self._config, databaseCore.DB_NAME)
        project_id = DL_projects.getOrInsertItem(self._con, self._core_id)
        tag_id = DL_subitemTags.getOrInsertItem(self._con, 'TRAILER')

        query = 'SELECT i.item_id, i.title, plot, poster_url, MAX(su.broadcastOn_date) FROM items i ' \
                'INNER JOIN sub_items su ON i.item_id = su.item_id ' \
                'WHERE project_id = ? and su.tag_id = ? GROUP BY i.item_id ' \
                'ORDER BY order_date DESC, order_id ASC'

        cursor = databaseHelper.executeReader(self._con, query, (project_id, tag_id, ))

        if cursor is not None:
            rowCollection = cursor.fetchall()
            for row in rowCollection:
                item_id = row[0]
                title = row[1]
                plot = row[2]
                poster = row[3]
                order_date = row[4]

                result, poster = self._getAlternatePoster(title, plot, order_date, poster)
                pass
                if result:
                    databaseHelper.executeNonQuery(self._con, 'UPDATE items SET poster_url = ? WHERE item_id = ?;',
                                                   (poster, item_id, ))

        self._con.close()

    def _getAlternatePoster(self, title, plot, order_date, default):

        if self._tmdb is None:
            self._tmdb = tmdbCore()

        movie = self._tmdb.searchMovie(title)
        if movie is not None:
            posterPath = self._tmdb.getPosterPath(movie, title, plot, order_date)
            if posterPath is not None:
                url = self._tmdb.getPosterUrl(posterPath)
                if url is not None:
                    return True, url

        return False, default

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

from ..databaseHelper import databaseHelper


class DL_qualities:

    @staticmethod
    def getItem(con, quality):
        query = 'SELECT quality_id FROM qualities WHERE name = ?;'
        quality_id = databaseHelper.executeScalar(con, query, (quality, ))
        if quality_id is None:
            quality_id = 0
        return quality_id

    @staticmethod
    def insertItem(con, quality):
        statement = 'INSERT INTO qualities (name) VALUES (?);'

        return databaseHelper.executeNonQuery(con, statement, (quality, ))

    @staticmethod
    def getOrInsertItem(con, quality):
        _quality_id = DL_qualities.getItem(con, quality)
        if _quality_id == 0:
            _, _quality_id = DL_qualities.insertItem(con, quality)

        return _quality_id

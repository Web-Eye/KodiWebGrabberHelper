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


class DL_subitemTags:

    @staticmethod
    def getItem(con, tag):
        query = 'SELECT tag_id FROM subitem_tags WHERE name = ?;'
        tag_id = databaseHelper.executeScalar(con, query, (tag, ))
        if tag_id is None:
            tag_id = 0
        return tag_id

    @staticmethod
    def insertItem(con, tag):
        statement = 'INSERT INTO subitem_tags (name) VALUES (?);'

        return databaseHelper.executeNonQuery(con, statement, (tag, ))

    @staticmethod
    def getOrInsertItem(con, tag):
        _tag_id = DL_subitemTags.getItem(con, tag)
        if _tag_id == 0:
            _, _tag_id = DL_subitemTags.insertItem(con, tag)

        return _tag_id

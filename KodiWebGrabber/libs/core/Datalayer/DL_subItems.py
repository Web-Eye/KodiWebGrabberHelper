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


class DL_subItems:

    @staticmethod
    def existsSubItem(con, item_id, title):
        query = 'SELECT subItem_id FROM sub_items WHERE item_id = ? AND title = ?;'
        subItem_id = databaseHelper.executeScalar(con, query, (item_id, title,))
        return subItem_id

    @staticmethod
    def insertSubItem(con, item):
        statement = 'INSERT INTO sub_items (item_id, title, tag_id, broadcastOn_date, availableTo_date, duration, poster_url) ' \
                    'VALUES (?, ?, ?, ?, ?, ?, ?);'

        return databaseHelper.executeNonQuery(con, statement, item)

    @staticmethod
    def deleteSubItemByItemId(con, item_id):
        statement = 'DELETE FROM sub_items WHERE item_id = ?'
        row_count, _id = databaseHelper.executeNonQuery(con, statement, (item_id,))
        return row_count

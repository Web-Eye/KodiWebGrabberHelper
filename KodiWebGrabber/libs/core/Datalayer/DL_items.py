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


class DL_items:

    @staticmethod
    def existsItem(con, project_id, identifier):
        query = 'SELECT item_id FROM items WHERE project_id = ? AND identifier = ?;'
        item_id = databaseHelper.executeScalar(con, query, (project_id, identifier,))
        return item_id

    @staticmethod
    def insertItem(con, item):
        statement = 'INSERT INTO items (project_id, identifier, hash, title, plot, tag_id, poster_url, order_date, ' \
                    'order_id) VALUES (?, ?, UNHEX(?), ?, ?, ?, ?, ?, ?);'

        return databaseHelper.executeNonQuery(con, statement, item)

    @staticmethod
    def getItem(con, project_id, identifier, _hash=None):

        if _hash is None:
            cursor = databaseHelper.executeReader(con, 'SELECT item_id, HEX(hash) FROM items WHERE project_id = ? AND '
                                                       'identifier = ?', (project_id, identifier, ))

        else:
            cursor = databaseHelper.executeReader(con, 'SELECT item_id, HEX(hash) FROM items WHERE project_id = ? AND '
                                                       'identifier = ? AND hash = UNHEX(?)',
                                                  (project_id, identifier, _hash,))

        row = cursor.fetchone()
        if row is not None:

            item = (
                row[0],
                row[1].lower()
            )

            return item

        return None

    @staticmethod
    def updateItem(con, item_id, item):
        statement = 'UPDATE items ' \
                    '   SET' \
                    '       hash = UNHEX(?)' \
                    '      ,title = ?' \
                    '      ,plot = ?' \
                    '      ,tag_id = ?' \
                    '      ,poster_url = ?' \
                    '      ,order_date = ?' \
                    '      ,order_id = ?' \
                    '   WHERE item_id = ?'

        item = item + (item_id,)
        row_count, _id = databaseHelper.executeNonQuery(con, statement, item)
        return row_count

    @staticmethod
    def deleteItem(con, item_id):
        statement = 'DELETE FROM items WHERE item_id = ?;'

        return databaseHelper.executeNonQuery(con, statement, (item_id, ))

    @staticmethod
    def deleteExpiredItems(con, project_id):
        statement = 'UPDATE items SET identifier = -1 WHERE item_id IN (' \
                    '   SELECT i.item_id FROM items  AS i' \
                    '   LEFT JOIN sub_items AS si ON i.item_id = si.item_id ' \
                    '   WHERE project_id = ? AND si.availableTo_date IS NOT Null AND si.availableTo_date < NOW()' \
                    ');'

        databaseHelper.executeNonQuery(con, statement, (project_id,))

        statement = 'DELETE FROM items WHERE project_id = ? AND identifier = -1;'

        row_count, _id = databaseHelper.executeNonQuery(con, statement, (project_id,))
        return row_count

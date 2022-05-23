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


class DL_lists:

    @staticmethod
    def deleteList(con, project_id, identifier_id):
        statement = 'DELETE FROM lists WHERE project_id = ? AND identifier_id = ?'
        row_count, _id = databaseHelper.executeNonQuery(con, statement, (project_id, identifier_id,))
        return row_count

    @staticmethod
    def insertList(con, item):
        statement = 'INSERT INTO lists (project_id, identifier_id, item_id, order_id) VALUES (?, ?, ?, ?)'
        row_count, _id = databaseHelper.executeNonQuery(con, statement, item)
        return row_count

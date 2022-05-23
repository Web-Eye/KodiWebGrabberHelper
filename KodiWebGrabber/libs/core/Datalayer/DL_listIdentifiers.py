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


class DL_listIdentifiers:

    @staticmethod
    def getItem(con, entity):
        query = 'SELECT identifier_id FROM list_identifier WHERE name = ?;'
        identifier_id = databaseHelper.executeScalar(con, query, (entity, ))
        if identifier_id is None:
            identifier_id = 0
        return identifier_id

    @staticmethod
    def insertItem(con, entity):
        statement = 'INSERT INTO list_identifier (name) VALUES (?);'

        return databaseHelper.executeNonQuery(con, statement, (entity, ))

    @staticmethod
    def getOrInsertItem(con, entity):
        identifier_id = DL_listIdentifiers.getItem(con, entity)
        if identifier_id == 0:
            _, identifier_id = DL_listIdentifiers.insertItem(con, entity)

        return identifier_id

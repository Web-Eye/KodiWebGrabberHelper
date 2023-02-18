# -*- coding: utf-8 -*-
# Copyright 2023 WebEye
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


class DL_projects:

    @staticmethod
    def getItem(con, project):
        query = 'SELECT IFNULL(project_id, 0) FROM projects WHERE name = ?;'
        project_id = databaseHelper.executeScalar(con, query, (project,))
        if project_id is None:
            project_id = 0
        return project_id

    @staticmethod
    def getItemDetails(con, project_id):
        cursor = databaseHelper.executeReader(con, 'SELECT name, description, parent_id, plot, icon_url FROM projects '
                                                   'WHERE project_id = ?', (project_id,))

        row = cursor.fetchone()
        if row is not None:
            item = {
                'name': row[0],
                'description': row[1],
                'parent_id': row[2],
                'plot': row[3],
                'icon_url': row[4]
            }

            return item

        return None

    @staticmethod
    def updateItem(con, project_id, item):
        statement = 'UPDATE projects ' \
                    '   SET' \
                    '       name = ?' \
                    '      ,description = ?' \
                    '      ,parent_id = ?' \
                    '      ,plot = ?' \
                    '      ,icon_url = ?' \
                    '   WHERE project_id = ?'

        item = item + (project_id,)
        row_count, _id = databaseHelper.executeNonQuery(con, statement, item)
        return row_count

    @staticmethod
    def insertItem(con, project, description=None, parent_id=None, plot=None, icon_url=None):
        statement = 'INSERT INTO projects (name, description, parent_id, plot, icon_url) VALUES (?, ?, ?, ?, ?);'

        return databaseHelper.executeNonQuery(con, statement, (project, description, parent_id, plot, icon_url))

    @staticmethod
    def getOrInsertItem(con, project, description=None, parent_id=None, plot=None, icon_url=None):
        _project_id = DL_projects.getItem(con, project)
        if _project_id == 0:
            _, _project_id = DL_projects.insertItem(con, project, description, parent_id, plot, icon_url)

        return _project_id

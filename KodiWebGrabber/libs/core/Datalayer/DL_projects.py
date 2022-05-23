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


class DL_projects:

    @staticmethod
    def getItem(con, project):
        query = 'SELECT IFNULL(project_id, 0) FROM projects WHERE name = ?;'
        project_id = databaseHelper.executeScalar(con, query, (project, ))
        if project_id is None:
            project_id = 0
        return project_id

    @staticmethod
    def insertItem(con, project):
        statement = 'INSERT INTO projects (name) VALUES (?);'

        return databaseHelper.executeNonQuery(con, statement, (project, ))

    @staticmethod
    def getOrInsertItem(con, project):
        _project_id = DL_projects.getItem(con, project)
        if _project_id == 0:
            _, _project_id = DL_projects.insertItem(con, project)

        return _project_id

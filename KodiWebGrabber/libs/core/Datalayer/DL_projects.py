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

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
        identifier_id = DL_projects.getItem(con, entity)
        if identifier_id == 0:
            _, identifier_id = DL_projects.insertItem(con, entity)

        return identifier_id

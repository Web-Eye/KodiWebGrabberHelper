from libs.core.databaseHelper import databaseHelper


class DL_lists:

    @staticmethod
    def deleteList(con, identifier):
        statement = 'DELETE FROM lists WHERE identifier = ?'
        databaseHelper.executeNonQuery(con, statement, (identifier,))

    @staticmethod
    def insertList(con, item):
        statement = 'INSERT INTO lists (identifier, item_id, order_id) VALUES (?, ?, ?)'

        databaseHelper.executeNonQuery(con, statement, item)

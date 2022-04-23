from ..databaseHelper import databaseHelper


class DL_lists:

    @staticmethod
    def deleteList(con, identifier):
        statement = 'DELETE FROM lists WHERE identifier = ?'
        row_count, _id = databaseHelper.executeNonQuery(con, statement, (identifier,))
        return row_count

    @staticmethod
    def insertList(con, item):
        statement = 'INSERT INTO lists (identifier, item_id, order_id) VALUES (?, ?, ?)'
        row_count, _id = databaseHelper.executeNonQuery(con, statement, item)
        return row_count

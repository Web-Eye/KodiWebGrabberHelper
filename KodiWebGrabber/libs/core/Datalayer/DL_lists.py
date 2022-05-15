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

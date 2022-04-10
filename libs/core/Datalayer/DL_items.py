from libs.core.databaseHelper import databaseHelper


class DL_items:

    @staticmethod
    def existsItem(con, project, identifier):
        query = 'SELECT COUNT(*) FROM items WHERE project = ? AND identifier = ?;'
        c = databaseHelper.executeScalar(con, query, (project, identifier,))
        return c != 0

    @staticmethod
    def insertItem(con, item):
        statement = 'INSERT INTO items (project, identifier, title, plot, tag, poster_url, order_date) VALUES ' \
                    '(?, ?, ?, ?, ?, ?, ?);'

        rowCount, item_id = databaseHelper.executeNonQuery(con, statement, item)
        return item_id


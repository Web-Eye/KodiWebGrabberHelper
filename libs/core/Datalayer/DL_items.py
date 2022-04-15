from libs.core.databaseHelper import databaseHelper


class DL_items:

    @staticmethod
    def existsItem(con, project, identifier):
        query = 'SELECT COUNT(*) FROM items WHERE project = ? AND identifier = ?;'
        c = databaseHelper.executeScalar(con, query, (project, identifier,))
        return c != 0

    @staticmethod
    def insertItem(con, item):
        statement = 'INSERT INTO items (project, identifier, hash, title, plot, tag, poster_url, order_date) VALUES ' \
                    '(?, ?, UNHEX(?), ?, ?, ?, ?, ?);'

        rowCount, item_id = databaseHelper.executeNonQuery(con, statement, item)
        return item_id

    @staticmethod
    def getItem(con, project, identifier, _hash=None):

        if _hash is None:
            cursor = databaseHelper.executeReader(con, 'SELECT item_id, HEX(hash) FROM items WHERE project = ? AND '
                                                       'identifier = ?', (project, identifier, ))

        else:
            cursor = databaseHelper.executeReader(con, 'SELECT item_id, HEX(hash) FROM items WHERE project = ? AND '
                                                       'identifier = ? AND hash = ?', (project, identifier, _hash,))

        row = cursor.fetchone()
        if row is not None:

            item = (
                row[0],
                row[1].lower()
            )

            return item

        return None

    @staticmethod
    def updateItem(con, item_id, item):
        statement = 'UPDATE items ' \
                    '   SET' \
                    '       hash = UNHEX(?)' \
                    '      ,title = ?' \
                    '      ,plot = ?' \
                    '      ,tag = ?' \
                    '      ,poster_url = ?' \
                    '      ,order_date = ?' \
                    '   WHERE item_id = ?'

        item = item + (item_id,)
        databaseHelper.executeNonQuery(con, statement, item)


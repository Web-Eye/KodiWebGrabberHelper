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

        return databaseHelper.executeNonQuery(con, statement, item)


    @staticmethod
    def getItem(con, project, identifier, _hash=None):

        if _hash is None:
            cursor = databaseHelper.executeReader(con, 'SELECT item_id, HEX(hash) FROM items WHERE project = ? AND '
                                                       'identifier = ?', (project, identifier, ))

        else:
            cursor = databaseHelper.executeReader(con, 'SELECT item_id, HEX(hash) FROM items WHERE project = ? AND '
                                                       'identifier = ? AND hash = UNHEX(?)',
                                                  (project, identifier, _hash,))

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
        row_count, _id = databaseHelper.executeNonQuery(con, statement, item)
        return row_count

    @staticmethod
    def deleteExpiredItems(con, project):
        statement = 'UPDATE items SET identifier = -1 WHERE item_id IN (' \
                    '   SELECT i.item_id FROM items  AS i' \
                    '   LEFT JOIN sub_items AS si ON i.item_id = si.item_id ' \
                    '   WHERE project = ? AND si.availableTo_date IS NOT Null AND si.availableTo_date < NOW()' \
                    ');'

        databaseHelper.executeNonQuery(con, statement, (project,))

        statement = 'DELETE FROM items WHERE project = ? AND identifier = -1;'

        row_count, _id = databaseHelper.executeNonQuery(con, statement, (project,))
        return row_count



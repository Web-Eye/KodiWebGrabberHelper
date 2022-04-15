from libs.core.databaseHelper import databaseHelper


class DL_subItems:

    @staticmethod
    def insertSubItem(con, item):
        statement = 'INSERT INTO sub_items (item_id, title, tag, broadcastOn_date, availableTo_date, duration) ' \
                    'VALUES (?, ?, ?, ?, ?, ?);'

        rowCount, item_id = databaseHelper.executeNonQuery(con, statement, item)
        return item_id

    @staticmethod
    def deleteSubItemByItemId(con, item_id):
        statement = 'DELETE FROM sub_items WHERE item_id = ?'
        databaseHelper.executeNonQuery(con, statement, (item_id,))


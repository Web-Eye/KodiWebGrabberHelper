from ..databaseHelper import databaseHelper


class DL_subItems:

    @staticmethod
    def insertSubItem(con, item):
        statement = 'INSERT INTO sub_items (item_id, title, tag, broadcastOn_date, availableTo_date, duration) ' \
                    'VALUES (?, ?, ?, ?, ?, ?);'

        return databaseHelper.executeNonQuery(con, statement, item)

    @staticmethod
    def deleteSubItemByItemId(con, item_id):
        statement = 'DELETE FROM sub_items WHERE item_id = ?'
        row_count, _id = databaseHelper.executeNonQuery(con, statement, (item_id,))
        return row_count


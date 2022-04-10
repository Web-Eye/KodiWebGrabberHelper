from libs.core.databaseHelper import databaseHelper


class DL_subItems:

    @staticmethod
    def insertItem(con, item):
        statement = 'INSERT INTO sub_items (item_id, title, tag, broadcastOn_date, availableTo_date, duration) ' \
                    'VALUES (?, ?, ?, ?, ?, ?);'

        rowCount, item_id = databaseHelper.executeNonQuery(con, statement, item)
        return item_id


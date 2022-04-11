from libs.core.databaseHelper import databaseHelper


class DL_links:

    @staticmethod
    def insertLink(con, item):
        statement = 'INSERT INTO links (subItem_id, quality, best_quality, hoster, size, url) ' \
                    'VALUES (?, ?, ?, ?, ?, ?);'

        rowCount, link_id = databaseHelper.executeNonQuery(con, statement, item)
        return link_id


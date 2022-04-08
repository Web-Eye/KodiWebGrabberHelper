from libs.core.databaseHelper import databaseHelper


class DL_show_links:

    @staticmethod
    def linkExists(con, show_id, quality_id):
        c = databaseHelper.executeScalar(con, 'SELECT COUNT(*) FROM show_links WHERE show_id = ? AND quality_id = ?', (show_id, quality_id,))
        return c != 0

    @staticmethod
    def insertLink(con, item):
        statement = 'INSERT INTO show_links (show_id, quality_id, url) VALUES (?, ?, ?)'
        databaseHelper.executeNonQuery(con, statement, item)

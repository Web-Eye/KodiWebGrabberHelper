from libs.core.databaseHelper import databaseHelper


class DL_shows:

    @staticmethod
    def showExists(con, API_id):
        c = databaseHelper.executeScalar(con, 'SELECT COUNT(*) FROM shows WHERE API_id = ?', (API_id,))
        return c != 0

    @staticmethod
    def insertShow(con, item):
        statement = 'INSERT INTO shows (API_id, title, plot, poster_url, broadcasted_date, available_to_date, duration) VALUES (?, ?, ?, ?, ?, ?, ?)'

        rowCount, show_id = databaseHelper.executeNonQuery(con, statement, item)
        return show_id

    @staticmethod
    def UpdatePlot(con, show_id, plot):
        statement = 'UPDATE shows SET plot = ? WHERE show_id = ?'
        databaseHelper.executeNonQuery(con, statement, (plot, show_id,))

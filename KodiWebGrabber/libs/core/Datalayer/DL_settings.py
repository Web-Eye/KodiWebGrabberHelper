from ..databaseHelper import databaseHelper


class DL_settings:

    @staticmethod
    def existsSetting(con, name):
        c = databaseHelper.executeScalar(con, 'SELECT COUNT(*) FROM settings WHERE name = ?', (name, ))
        return c != 0

    @staticmethod
    def getSetting(con, name):
        cursor = databaseHelper.executeReader(con, 'SELECT value FROM settings WHERE name = ?', (name, ))
        row = cursor.fetchone()
        if row is not None:
            return row[0]

        return None

    @staticmethod
    def setSetting(con, name, value):
        if DL_settings.existsSetting(con, name):
            databaseHelper.executeNonQuery(con, 'UPDATE settings SET value = ? WHERE name = ?', (value, name,))
        else:
            databaseHelper.executeNonQuery(con, 'INSERT INTO settings (name, value) VALUES (?, ?)', (name, value,))

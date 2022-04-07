from libs.core.databaseHelper import databaseHelper


class DL_settings:

    def __init__(self, config):
        self._config = config

    def settingExists(self, con, name):
        c = databaseHelper.executeScalar(con, 'SELECT COUNT(*) FROM settings WHERE name = ?', (name,))
        return c != 0

    def getSetting(self, con, name):
        pass

    def setSetting(self, con, name, value):
        if self.settingExists(con, name):
            databaseHelper.executeNonQuery(con, 'UPDATE settings SET value = ? WHERE name = ?', (value, name,))
        else:
            databaseHelper.executeNonQuery(con, 'INSERT INTO settings (name, value) VALUES (?, ?)', (name, value,))

from libs.core.databaseCore import _executeScalar, _executeNonQuery


class DL_settings:

    # def __init__(self, config):
    #     self._config = config

    def settingExists(self, con, name):
        c = _executeScalar(con, 'SELECT COUNT(*) FROM settings WHERE name = ?', (name,))
        return c != 0

    def getSetting(self, con, name):
        pass

    def setSetting(self, con, name, value):
        if self.settingExists(con, name):
            _executeNonQuery(con, 'UPDATE settings SET value = ? WHERE name = ?', (value, name,))
        else:
            _executeNonQuery(con, 'INSERT INTO settings (name, value) VALUES (?, ?)', (name, value,))

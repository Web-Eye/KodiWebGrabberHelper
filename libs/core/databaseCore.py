import mariadb
from libs.core.Datalayer.DL_settings import DL_settings
from libs.core.databaseHelper import databaseHelper


class databaseCore:

    def __init__(self, config, db_name):
        self._config = config
        self._db_name = db_name

    def DBName(self):
        return self._db_name

    def getConnection(self, database_name=None):
        return mariadb.connect(
            host=self._config['host'],
            port=self._config['port'],
            user=self._config['user'],
            password=self._config['password'],
            database=database_name
        )

    def create_database(self):

        retValue = True

        try:

            con = self.getConnection()
            if not databaseHelper.database_exists(con, self._db_name):
                retValue = databaseHelper.create_database(con, self._db_name)

            con.close()
            return retValue

        except mariadb.Error as e:
            print(f"Error connecting to MariaDB Platform: {e}")
            return False

    def get_database_version(self, con):
        if not databaseHelper.tableExists(con, self._db_name, 'settings'):
            return 0

        retValue = DL_settings.getSetting(con, 'database_version')
        if retValue is not None:
            return int(retValue)

        return 0

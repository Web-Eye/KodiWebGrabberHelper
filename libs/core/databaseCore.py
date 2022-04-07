import mariadb
from libs.core.Datalayer.DL_settings import DL_settings


def _executeScalar(con, query, parameters=None):
    retValue = None

    try:
        cursor = con.cursor()
        cursor.execute(query, parameters)
        row = cursor.fetchone()
        retValue = None
        if row is not None:
            retValue = row[0]

        cursor.close()
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")

    return retValue


def _executeNonQuery(con, statement, parameters=None):
    row_count = None
    last_row_id = None

    try:
        cursor = con.cursor()
        cursor.execute(statement, parameters)

        last_row_id = cursor.lastrowid
        con.commit()
        row_count = cursor.rowcount

        cursor.close()

    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")

    return row_count, last_row_id


def _database_exists(con, databasename):
    result = _executeScalar(con, 'SELECT COUNT(*) FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = ?',
                            (databasename,))
    if result == 1:
        return True

    return False


def _create_database(con, databasename):
    rows = _executeNonQuery(con, f'CREATE DATABASE {databasename}')
    return rows[0] == 1


def _tableExists(con, tablename):
    result = _executeScalar(con, 'SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = ?', (tablename,))
    if result == 1:
        return True

    return False


class databaseCore:

    def __init__(self, config, db_name):
        self._config = config
        self._db_name = db_name

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
            if not _database_exists(con, self._db_name):
                retValue = _create_database(con, self._db_name)

            con.close()
            return retValue

        except mariadb.Error as e:
            print(f"Error connecting to MariaDB Platform: {e}")
            return False

    def get_database_version(self, con):
        if not _tableExists(con, 'settings'):
            return 0

        dl = DL_settings()
        return dl.getSetting(con, 'database_version')

import mariadb


class databaseHelper:

    @staticmethod
    def getConnection(config, database_name=None):
        return mariadb.connect(
            host=config['host'],
            port=config['port'],
            user=config['user'],
            password=config['password'],
            database=database_name
        )

    @staticmethod
    def executeScalar(con, query, parameters=None):
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

    @staticmethod
    def executeNonQuery(con, statement, parameters=None):
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

    @staticmethod
    def executeReader(con, query, parameters=None):

        try:
            cursor = con.cursor()
            cursor.execute(query, parameters)
            return cursor

        except mariadb.Error as e:
            print(f"Error connecting to MariaDB Platform: {e}")
            return None

    @staticmethod
    def database_exists(con, databasename):
        result = databaseHelper.executeScalar(con, 'SELECT COUNT(*) FROM INFORMATION_SCHEMA.SCHEMATA WHERE '
                                                   'SCHEMA_NAME = ?', (databasename,))
        if result == 1:
            return True

        return False

    @staticmethod
    def create_database(con, databasename):
        rows = databaseHelper.executeNonQuery(con, f'CREATE DATABASE {databasename}')
        return rows[0] == 1

    @staticmethod
    def tableExists(con, databasename, tablename):
        result = databaseHelper.executeScalar(con, 'SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA '
                                                   '= ? AND TABLE_NAME = ?', (databasename, tablename,))
        if result == 1:
            return True

        return False

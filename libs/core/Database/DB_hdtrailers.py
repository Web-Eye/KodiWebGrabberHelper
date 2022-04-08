from libs.core.Datalayer.DL_settings import DL_settings
from libs.core.databaseCore import databaseCore
from libs.core.databaseHelper import databaseHelper


class DB_hdtrailers(databaseCore):
    CURRENT_DB_VERSION = 1
    DB_NAME = 'wghHDTRAILERS'

    def __init__(self, config):
        super().__init__(config, DB_hdtrailers.DB_NAME)

    def check_database(self):
        if self.create_database():
            if self.update_database():
                return True

        return False

    def update_database(self):
        con = self.getConnection(self._db_name)
        dbVersion = self.get_database_version(con)

        while dbVersion < DB_hdtrailers.CURRENT_DB_VERSION:
            dbVersion = self._update_database(con, dbVersion)

        con.close()
        return True

    def _update_database(self, con, dbVersion):

        if dbVersion == 0:
            statement = 'CREATE TABLE IF NOT EXISTS movies (' \
                        '   movie_id INT NOT NULL AUTO_INCREMENT,' \
                        '   title VARCHAR(255) NOT NULL,' \
                        '   plot VARCHAR(4096),' \
                        '   poster_url VARCHAR(255),' \
                        '   last_date DATETIME,' \
                        '   PRIMARY KEY (`movie_id`)' \
                        ');'

            databaseHelper.executeNonQuery(con, statement)

            statement = 'CREATE TABLE IF NOT EXISTS trailers (' \
                        '   trailer_id INT NOT NULL AUTO_INCREMENT,' \
                        '   movie_id INT NOT NULL,' \
                        '   name VARCHAR(255) NOT NULL,' \
                        '   aired_date DATETIME,' \
                        '   PRIMARY KEY (`trailer_id`)' \
                        ');'

            databaseHelper.executeNonQuery(con, statement)

            statement = 'CREATE TABLE IF NOT EXISTS trailer_links (' \
                        '   link_id INT NOT NULL AUTO_INCREMENT,' \
                        '   trailer_id INT,' \
                        '   quality_id INT,' \
                        '   hoster VARCHAR(255),' \
                        '   size INT,' \
                        '   url VARCHAR(255),' \
                        '   PRIMARY KEY (`link_id`)' \
                        ');'

            databaseHelper.executeNonQuery(con, statement)

            statement = 'CREATE TABLE IF NOT EXISTS movie_list_items (' \
                        '   item_id INT NOT NULL AUTO_INCREMENT,' \
                        '   list VARCHAR(20) NOT NULL,' \
                        '   list_number INT NOT NULL,' \
                        '   movie_id INT NOT NULL,' \
                        '   PRIMARY KEY (`item_id`)' \
                        ');'

            databaseHelper.executeNonQuery(con, statement)

            statement = 'CREATE TABLE IF NOT EXISTS settings (' \
                        '   setting_id INT NOT NULL AUTO_INCREMENT,' \
                        '   name VARCHAR(100),' \
                        '   value VARCHAR(100),' \
                        '   PRIMARY KEY (`setting_id`)' \
                        ');'

            databaseHelper.executeNonQuery(con, statement)

            DL_settings.setSetting(con, 'database_version', '1')
            return 1

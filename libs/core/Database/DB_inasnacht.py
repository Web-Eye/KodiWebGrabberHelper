from libs.core.Datalayer.DL_settings import DL_settings
from libs.core.databaseCore import databaseCore
from libs.core.databaseHelper import databaseHelper


class DB_inasnacht(databaseCore):

    CURRENT_DB_VERSION = 1
    DB_NAME = 'wghINASNACHT'

    def __init__(self, config):
        super().__init__(config, DB_inasnacht.DB_NAME)

    def check_database(self):
        if self.create_database():
            if self.update_database():
                return True

        return False

    def update_database(self):
        con = self.getConnection(self._db_name)
        dbVersion = self.get_database_version(con)

        while dbVersion < DB_inasnacht.CURRENT_DB_VERSION:
            dbVersion = self._update_database(con, dbVersion)

        con.close()
        return True

    def _update_database(self, con, dbVersion):

        if dbVersion == 0:

            statement = 'CREATE TABLE IF NOT EXISTS shows (' \
                        '   show_id INT NOT NULL AUTO_INCREMENT,' \
                        '   API_id VARCHAR(100) NOT NULL,' \
                        '   title VARCHAR(255) NOT NULL,' \
                        '   plot VARCHAR(4096),' \
                        '   poster_url VARCHAR(255),' \
                        '   broadcasted_date DATETIME,' \
                        '   available_to_date DATETIME,' \
                        '   duration BIGINT,' \
                        '   sign_language BIT,' \
                        '   music_clip BIT,' \
                        '   PRIMARY KEY (`show_id`)' \
                        ');'

            databaseHelper.executeNonQuery(con, statement)

            statement = 'CREATE TABLE IF NOT EXISTS show_links (' \
                        '   link_id INT NOT NULL AUTO_INCREMENT,' \
                        '   show_id INT,' \
                        '   quality_id INT,' \
                        '   url VARCHAR(255),' \
                        '   PRIMARY KEY (link_id)' \
                        ');'

            databaseHelper.executeNonQuery(con, statement)

            statement = 'CREATE TABLE IF NOT EXISTS settings (' \
                        '   setting_id INT NOT NULL AUTO_INCREMENT,' \
                        '   name VARCHAR(100),' \
                        '   value VARCHAR(100),' \
                        '   PRIMARY KEY (setting_id)' \
                        ');'

            databaseHelper.executeNonQuery(con, statement)

            DL_settings.setSetting(con, 'database_version', '1')
            return 1





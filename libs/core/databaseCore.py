import mariadb
from libs.core.Datalayer.DL_settings import DL_settings
from libs.core.databaseHelper import databaseHelper


class databaseCore:

    CURRENT_DB_VERSION = 1
    DB_NAME = 'KodiWebGrabber'

    def __init__(self, config):
        self._config = config

    def create_database(self):

        retValue = True

        try:

            con = databaseHelper.getConnection(self._config)
            if not databaseHelper.database_exists(con, databaseCore.DB_NAME):
                retValue = databaseHelper.create_database(con, databaseCore.DB_NAME)

            con.close()
            return retValue

        except mariadb.Error as e:
            print(f"Error connecting to MariaDB Platform: {e}")
            return False

    def get_database_version(self, con):
        if not databaseHelper.tableExists(con, databaseCore.DB_NAME, 'settings'):
            return 0

        retValue = DL_settings.getSetting(con, 'database_version')
        if retValue is not None:
            return int(retValue)

        return 0

    def check_database(self):
        if self.create_database():
            if self.update_database():
                return True

        return False

    def update_database(self):
        con = databaseHelper.getConnection(self._config, databaseCore.DB_NAME)
        dbVersion = self.get_database_version(con)

        while dbVersion < databaseCore.CURRENT_DB_VERSION:
            dbVersion = self._update_database(con, dbVersion)

        con.close()
        return True

    def _update_database(self, con, dbVersion):

        if dbVersion == 0:

            statement = 'CREATE TABLE IF NOT EXISTS items (' \
                        '   item_id INT NOT NULL AUTO_INCREMENT,' \
                        '   project ENUM(\'HARTABERFAIR\', \'INASNACHT\', \'ROCKPALAST\', \'HDTRAILERS\') NOT NULL,' \
                        '   identifier VARCHAR(128) NOT NULL,' \
                        '   title VARCHAR(255) NOT NULL,' \
                        '   plot VARCHAR(4096),' \
                        '   tag ENUM(\'NONE\', \'SIGNLANGUAGE\', \'MUSICCLIP\', \'INTERVIEW\', \'UNPLUGGED\', ' \
                        '   \'LIVEPREVIEW\') NOT NULL,' \
                        '   poster_url VARCHAR(255),' \
                        '   order_date DATETIME NOT NULL,' \
                        '   PRIMARY KEY (`item_id`)' \
                        ');'

            databaseHelper.executeNonQuery(con, statement)

            statement = 'CREATE TABLE IF NOT EXISTS sub_items (' \
                        '   subItem_id INT NOT NULL AUTO_INCREMENT,' \
                        '   item_id INT NOT NULL,' \
                        '   title VARCHAR(255) NOT NULL,' \
                        '   tag ENUM (\'NONE\', \'TRAILER\', \'TEASER\', \'CLIP\') NOT NULL,' \
                        '   broadcastOn_date DATETIME,' \
                        '   availableTo_date DATETIME ,' \
                        '   duration INT,' \
                        '   PRIMARY KEY (`subItem_id`)' \
                        ');'

            databaseHelper.executeNonQuery(con, statement)

            statement = 'CREATE TABLE IF NOT EXISTS links (' \
                        '   link_id INT NOT NULL AUTO_INCREMENT,' \
                        '   subItem_id INT NOT NULL,' \
                        '   quality ENUM (\'270p\', \'360p\', \'480p\', \'540p\', \'720p\', \'1080p\') NOT NULL,' \
                        '   hoster VARCHAR(64),' \
                        '   size INT,' \
                        '   URL VARCHAR(255) NOT NULL,' \
                        '   PRIMARY KEY (`link_id`)' \
                        ');'

            databaseHelper.executeNonQuery(con, statement)

            statement = 'CREATE TABLE IF NOT EXISTS lists (' \
                        '   list_id INT NOT NULL AUTO_INCREMENT,' \
                        '   identifier ENUM(\'HDT_MOSTWATCHEDWEEK\', \'HDT_MOSTWATCHEDTODAY\', \'HDT_TOPTEN\', ' \
                        '   \'HDT_OPENING\', \'HDT_COMINGSOON\') NOT NULL,' \
                        '   item_id INT NOT NULL,' \
                        '   order_id INT NOT NULL,' \
                        '   PRIMARY KEY (`list_id`)' \
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


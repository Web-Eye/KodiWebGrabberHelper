from libs.common.enums import cores
from libs.core.Database.DB_hdtrailers import DB_hdtrailers


class hdtrailersCore():

    def __init__(self, core, config):
        self._core = core
        self._config = config


    def run(self):
        print("start")
        db = None

        if self._core == cores.HDTRAILERS:
            db = DB_hdtrailers(self._config)


        if db.check_database():
            pass
        else:
            print('can''t connect to database')


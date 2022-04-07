from libs.common.enums import cores
from libs.core.Database.DB_hartaberfair import DB_hartaberfair


class ardmediathekCore():

    def __init__(self, core, channel, mediathek_id, config):
        self._core = core
        self._channel = channel
        self._mediathek_id = mediathek_id
        self._config = config


    def run(self):
        print("start")
        db = None

        if self._core == cores.HARTABERFAIR:
            db = DB_hartaberfair(self._config)

        if db.check_database():
            pass
        else:
            print('can''t connect to database')




        pass


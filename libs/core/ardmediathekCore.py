import json

import requests

from libs.common import tools
from libs.common.enums import cores
from libs.core.Database.DB_hartaberfair import DB_hartaberfair
from libs.core.Database.DB_inasnacht import DB_inasnacht
from libs.core.Database.DB_rockpalast import DB_rockpalast
from libs.core.Datalayer.DL_shows import DL_shows

class ardmediathekCore():

    def __init__(self, core, channel, mediathek_id, config):
        self._core = core
        self._channel = channel
        self._mediathek_id = mediathek_id
        self._config = config
        self._db = None

        self._baseurl = f'https://api.ardmediathek.de/page-gateway/widgets/{channel}/asset/{mediathek_id}' \
                        '?pageNumber={pageNumber}&pageSize={pageSize}&embedded=true&seasoned=false&seasonNumber=' \
                        '&withAudiodescription=false&withOriginalWithSubtitle=false&withOriginalversion=false '


    def run(self):
        print("start")

        if self._core == cores.HARTABERFAIR:
            self._db = DB_hartaberfair(self._config)
        elif self._core == cores.INASNACHT:
            self._db = DB_inasnacht(self._config)
        elif self._core == cores.ROCKPALAST:
            self._db = DB_rockpalast(self._config)

        if self._db.check_database():
            self.GrabShows()
        else:
            print('can''t connect to database')


    def GrabShows(self):

        pagenumber = 0
        pagesize = 48
        totalelements = 1

        while totalelements > (pagenumber * pagesize):

            url = self._baseurl
            url = url.replace('{pageNumber}', str(pagenumber))
            url = url.replace('{pageSize}', str(pagesize))

            page = requests.get(url)
            content = json.loads(page.content)
            if content is None:
                break

            shows = content['teasers']
            if not self.getShows(shows):
                break

            pagination = content['pagination']
            if pagination is None:
                break

            pagenumber = pagenumber + 1
            totalelements = int(pagination['totalElements'])

    def getShows(self, shows):

        if shows is None:
            return False

        con = self._db.getConnection(self._db.DBName())

        for show in shows:
            API_id = show['id']
            if DL_shows.showExists(con, API_id):
                con.close()
                return False

            title = show['longTitle']
            sign_language = ('(mit Gebärdensprache)' in title)

            item = (
                API_id,
                title,
                None,
                show['images']['aspect16x9']['src'],
                tools.convertDateTime(show['broadcastedOn'], '%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%d %H:%M:%S'),
                tools.convertDateTime(show['availableTo'], '%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%d %H:%M:%S'),
                show['duration'],
                sign_language,
            )

            detail_url = show['links']['target']['href']
            show_id = DL_shows.insertShow(con, item)

            page = requests.get(detail_url)
            content = json.loads(page.content)
            if content is None:
                break

            item = content['widgets'][0]
            plot = item['synopsis']
            DL_shows.UpdatePlot(con, show_id, plot)

        con.close()

        return True

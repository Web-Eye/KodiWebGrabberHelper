import json

import requests

from libs.common import tools
from libs.common.enums import tagEnum, coreEnum, subItemTagEnum
from libs.core.Datalayer.DL_items import DL_items
from libs.core.Datalayer.DL_subItems import DL_subItems
from libs.core.databaseCore import databaseCore
from libs.core.databaseHelper import databaseHelper


class ardmediathekCore:

    def __init__(self, core, channel, mediathek_id, config):
        self._core = core
        self._channel = channel
        self._mediathek_id = mediathek_id
        self._config = config
        self._baseurl = f'https://api.ardmediathek.de/page-gateway/widgets/{channel}/asset/{mediathek_id}' \
                        '?pageNumber={pageNumber}&pageSize={pageSize}&embedded=true&seasoned=false&seasonNumber=' \
                        '&withAudiodescription=false&withOriginalWithSubtitle=false&withOriginalversion=false '

    def run(self):

        con = databaseHelper.getConnection(self._config, databaseCore.DB_NAME)

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
            if not self.getShows(con, shows):
                break

            pagination = content['pagination']
            if pagination is None:
                break

            pagenumber = pagenumber + 1
            totalelements = int(pagination['totalElements'])

        con.close()

    def getShows(self, con, shows):

        if shows is None:
            return False

        for show in shows:
            identifier = show['id']
            if DL_items.existsItem(con, self._core.name, identifier):
                return False

            detail_url = show['links']['target']['href']
            page = requests.get(detail_url)
            content = json.loads(page.content)
            if content is None:
                return False

            title = show['longTitle']
            widget = content['widgets'][0]

            item = (
                self._core.name,
                identifier,
                title,
                widget['synopsis'],
                self.getTag(title).name,
                show['images']['aspect16x9']['src'],
                tools.convertDateTime(show['broadcastedOn'], '%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%d %H:%M:%S')
            )

            item_id = DL_items.insertItem(con, item)

            item = (
                item_id,
                title,
                subItemTagEnum.NONE.name,
                tools.convertDateTime(show['broadcastedOn'], '%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%d %H:%M:%S'),
                tools.convertDateTime(show['availableTo'], '%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%d %H:%M:%S'),
                show['duration'],
            )

            subItem_id = DL_subItems.insertItem(con, item)

            ## TODO save links

            ## _quality: 0 --> 270p
            ## _quality: 1 --> 360p
            ## _quality: 2 --> 540p
            ## _quality: 3 --> 720p
            ## _quality: 4 --> 1080p
            ## _quality: 'auto' --> skip

            # mediastreamarray = widget['mediaCollection']['embedded']['_mediaArray'][0]['_mediaStreamArray']
            # for stream in mediastreamarray:
            #
            #     item = (
            #         show_id,
            #         stream['_quality'],
            #         stream['_stream'],
            #     )
            #
            #     DL_show_links.insertLink(con, item)

        return True

    def getTag(self, title):
        if self._core == coreEnum.HARTABERFAIR:
            if '(mit Gebärdensprache)' in title:
                return tagEnum.SIGNLANGUAGE
        elif self._core == coreEnum.INASNACHT:
            if 'Musik bei Inas Nacht:' in title:
                return tagEnum.MUSICCLIP
        elif self._core == coreEnum.ROCKPALAST:
            if 'Unplugged:' in title:
                return tagEnum.UNPLUGGED
            elif 'Live-Preview:' in title:
                return tagEnum.LIVEPREVIEW
            elif 'Interview' in title:
                return tagEnum.INTERVIEW

        return tagEnum.NONE



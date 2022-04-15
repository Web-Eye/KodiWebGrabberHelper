import json

import requests

from libs.common import tools
from libs.common.enums import tagEnum, coreEnum, subItemTagEnum
from libs.core.Datalayer.DL_links import DL_links
from libs.core.Datalayer.DL_items import DL_items
from libs.core.Datalayer.DL_subItems import DL_subItems
from libs.core.databaseCore import databaseCore
from libs.core.databaseHelper import databaseHelper


def _getBestQuality(mediastreamarray):
    li = list(filter(lambda p: isinstance(p['_quality'], int), mediastreamarray))
    if li is not None and len(li) > 0:
        return max(li, key=lambda p: int(p['_quality']))['_quality']

    return -1


def _getQuality(quality):
    if quality == 0:
        return '270p'
    elif quality == 1:
        return '360p'
    elif quality == 2:
        return '540p'
    elif quality == 3:
        return '720p'
    elif quality == 4:
        return '1080p'

    return None


class ardmediathekCore:

    def __init__(self, core, channel, mediathek_id, config):
        self._core = core
        self._channel = channel
        self._mediathek_id = mediathek_id
        self._config = config
        self._con = None

        self._baseurl = f'https://api.ardmediathek.de/page-gateway/widgets/{channel}/asset/{mediathek_id}' \
                        '?pageNumber={pageNumber}&pageSize={pageSize}&embedded=true&seasoned=false&seasonNumber=' \
                        '&withAudiodescription=false&withOriginalWithSubtitle=false&withOriginalversion=false '

    def run(self):

        self._con = databaseHelper.getConnection(self._config, databaseCore.DB_NAME)

        self._deleteExpiredShows()
        self._getLatestShows()

        self._con.close()

    def _deleteExpiredShows(self):
        DL_items.deleteExpiredItems(self._con, self._core.name)

    def _getLatestShows(self):
        pagenumber = 0
        pagesize = 48
        totalelements = 1

        requests_session = requests.Session()

        while totalelements > (pagenumber * pagesize):

            url = self._baseurl
            url = url.replace('{pageNumber}', str(pagenumber))
            url = url.replace('{pageSize}', str(pagesize))

            page = requests_session.get(url)
            content = json.loads(page.content)
            if content is None:
                break

            shows = content['teasers']
            if not self._getShows(requests_session, shows):
                break

            pagination = content['pagination']
            if pagination is None:
                break

            pagenumber = pagenumber + 1
            totalelements = int(pagination['totalElements'])

    def _getShows(self, requests_session, shows):

        if shows is None:
            return False

        for show in shows:
            identifier = show['id']
            if DL_items.existsItem(self._con, self._core.name, identifier):
                return False

            detail_url = show['links']['target']['href']
            page = requests_session.get(detail_url)
            content = json.loads(page.content)
            if content is None:
                return False

            title = show['longTitle']
            widget = content['widgets'][0]
            best_quality = -1

            mediastreamarray = widget['mediaCollection']['embedded']['_mediaArray'][0]['_mediaStreamArray']
            if mediastreamarray is not None and len(mediastreamarray) > 0:
                best_quality = _getBestQuality(mediastreamarray)

            if best_quality > -1:

                item = (
                    self._core.name,
                    identifier,
                    None,
                    title,
                    widget['synopsis'],
                    self._getTag(title).name,
                    show['images']['aspect16x9']['src'],
                    tools.convertDateTime(show['broadcastedOn'], '%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%d %H:%M:%S')
                )

                item_id = DL_items.insertItem(self._con, item)

                item = (
                    item_id,
                    None,
                    subItemTagEnum.NONE.name,
                    tools.convertDateTime(show['broadcastedOn'], '%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%d %H:%M:%S'),
                    tools.convertDateTime(show['availableTo'], '%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%d %H:%M:%S'),
                    show['duration'],
                )

                subItem_id = DL_subItems.insertSubItem(self._con, item)

                for stream in mediastreamarray:

                    quality = _getQuality(stream['_quality'])
                    if quality is not None:
                        item = (
                            subItem_id,
                            quality,
                            best_quality == stream['_quality'],
                            tools.getHoster(stream['_stream']),
                            None,
                            stream['_stream'],
                        )

                        DL_links.insertLink(self._con, item)

        return True

    def _getTag(self, title):
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

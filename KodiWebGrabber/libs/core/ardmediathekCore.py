import json
import random
import time
import requests

from .Datalayer.DL_itemTags import DL_itemTags
from .Datalayer.DL_projects import DL_projects
from .Datalayer.DL_qualities import DL_qualities
from .Datalayer.DL_subitemTags import DL_subitemTags
from ..common import tools
from .Datalayer.DL_links import DL_links
from .Datalayer.DL_items import DL_items
from .Datalayer.DL_subItems import DL_subItems
from .databaseCore import databaseCore
from .databaseHelper import databaseHelper


class ardmediathekCore:

    def __init__(self, core_id, channel, mediathek_id, config, addArgs):
        self._project_id = 0
        self._core_id = core_id
        self._channel = channel
        self._mediathek_id = mediathek_id
        self._config = config
        self._verbose = addArgs['verbose']
        self._page_begin = addArgs['page_begin']
        self._page_count = addArgs['page_count']
        self._suppressSkip = addArgs['suppress_skip']
        self._minWaittime = 0.0
        self._maxWaittime = 0.0
        waittime = addArgs['wait_time']
        if waittime is not None:
            self._minWaittime = waittime[0]
            self._maxWaittime = waittime[1]

        self._con = None

        self._addedShows = 0
        self._deletedShows = 0
        self._itemTagDict = {}
        self._subitemTagDict = {}

        self._baseurl = f'https://api.ardmediathek.de/page-gateway/widgets/{channel}/asset/{mediathek_id}' \
                        '?pageNumber={pageNumber}&pageSize={pageSize}&embedded=true&seasoned=false&seasonNumber=' \
                        '&withAudiodescription=false&withOriginalWithSubtitle=false&withOriginalversion=false '

    def run(self):
        self._con = databaseHelper.getConnection(self._config, databaseCore.DB_NAME)

        self._project_id = DL_projects.getOrInsertItem(self._con, self._core_id)
        self._itemTagDict = self._getItemTags()
        self._subitemTagDict = self._getSubitemTags()
        self._deleteExpiredShows()
        self._getLatestShows()

        self._con.close()

        if self._verbose:
            print(f'Added Shows: {self._addedShows}')
            print(f'Deleted Shows: {self._deletedShows}')

    @staticmethod
    def _getBestQuality(mediastreamarray):
        li = list(filter(lambda p: isinstance(p['_quality'], int), mediastreamarray))
        if tools.getLength(li) > 0:
            return max(li, key=lambda p: int(p['_quality']))['_quality']

        return -1

    @staticmethod
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

    def _deleteExpiredShows(self):
        self._deletedShows += DL_items.deleteExpiredItems(self._con, self._core_id)

    def _getContent(self, requests_session, url):
        conn_tries = 0
        while True:

            try:
                wt = round(random.uniform(self._minWaittime, self._maxWaittime), 2)
                if wt > 0:
                    time.sleep(wt)

                headers = {
                    'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
                }

                page = requests_session.get(url, timeout=10, headers=headers)
                return json.loads(page.content)

            except requests.exceptions.ConnectionError as e:
                conn_tries += 1
                if conn_tries > 4:
                    print('exit [max reties are reached]')
                    raise e

                time.sleep(60)

    def _getLatestShows(self):
        pagenumber = self._page_begin - 1
        pagesize = 48
        totalelements = 1

        requests_session = requests.Session()
        i = 0

        while totalelements > (pagenumber * pagesize):

            url = self._baseurl
            url = url.replace('{pageNumber}', str(pagenumber))
            url = url.replace('{pageSize}', str(pagesize))

            content = self._getContent(requests_session, url)

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

            i += 1
            if self._page_count is not None and i >= self._page_count:
                break

    def _getShows(self, requests_session, shows):

        if shows is None:
            return False

        for show in shows:
            identifier = show['id']
            showExists_id = tools.eint(DL_items.existsItem(self._con, self._project_id, identifier))
            if showExists_id > 0 and not self._suppressSkip:
                return False

            detail_url = show['links']['target']['href']
            content = self._getContent(requests_session, detail_url)
            if content is None:
                return False

            title = show['longTitle']
            widget = content['widgets'][0]
            best_quality = -1

            mediastreamarray = widget['mediaCollection']['embedded']['_mediaArray'][0]['_mediaStreamArray']
            if tools.getLength(mediastreamarray) > 0:
                best_quality = self._getBestQuality(mediastreamarray)

            if best_quality > -1:

                if showExists_id > 0:
                    DL_items.deleteItem(self._con, showExists_id)

                item = (
                    self._project_id,
                    identifier,
                    None,
                    title,
                    widget['synopsis'],
                    self._getTag_id(title),
                    show['images']['aspect16x9']['src'],
                    tools.convertDateTime(show['broadcastedOn'], '%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%d %H:%M:%S'),
                    None
                )

                row_count, item_id = DL_items.insertItem(self._con, item)
                self._addedShows += row_count

                item = (
                    item_id,
                    None,
                    self._getSubitemTag_id(None),
                    tools.convertDateTime(show['broadcastedOn'], '%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%d %H:%M:%S'),
                    tools.convertDateTime(show['availableTo'], '%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%d %H:%M:%S'),
                    show['duration'],
                )

                row_count, subItem_id = DL_subItems.insertSubItem(self._con, item)

                for stream in mediastreamarray:

                    quality = self._getQuality(stream['_quality'])
                    if quality is not None:
                        item = (
                            subItem_id,
                            self._getQuality_id(quality),
                            best_quality == stream['_quality'],
                            tools.getHoster(stream['_stream']),
                            None,
                            stream['_stream'],
                        )

                        DL_links.insertLink(self._con, item)

        return True

    def _addItemTag(self, _dict, tag):
        tag_id = DL_itemTags.getOrInsertItem(self._con, tag)
        _dict[tag] = tag_id

        return _dict

    def _getItemTags(self):
        _dict = {}
        _dict = self._addItemTag(_dict, 'None')

        return _dict

    def _getTag_id(self, title):
        return self._itemTagDict['None']

    def _addSubitemTag(self, _dict, tag):
        tag_id = DL_subitemTags.getOrInsertItem(self._con, tag)
        _dict[tag] = tag_id

        return _dict

    def _getSubitemTags(self):
        _dict = {}
        _dict = self._addSubitemTag(_dict, 'None')

        return _dict

    def _getSubitemTag_id(self, title):
        return self._subitemTagDict['None']

    def _getQuality_id(self, quality):
        return DL_qualities.getOrInsertItem(self._con, quality)

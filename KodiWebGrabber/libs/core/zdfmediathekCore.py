# -*- coding: utf-8 -*-
# Copyright 2022 WebEye
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
import datetime
import json
import random
import time
import requests
import urllib
import urllib.parse
from bs4 import BeautifulSoup
from dateutil.relativedelta import relativedelta

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


class zdfmediathekCore:

    def __init__(self, core_id, mediathek_id, config, addArgs):
        self._project_id = 0
        self._core_id = core_id
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

        self._timeout = 10
        if 'timeout' in addArgs:
            self._timeout = addArgs['timeout']

        self._con = None

        self._addedShows = 0
        self._deletedShows = 0
        self._itemTagDict = {}
        self._subitemTagDict = {}

        self._requests_session = None
        self._baseurl = f'https://zdf-cdn.live.cellular.de/mediathekV2/document/{mediathek_id}'

    def run(self):
        self._con = databaseHelper.getConnection(self._config)
        self._requests_session = requests.Session()

        self._project_id = DL_projects.getOrInsertItem(self._con, self._core_id)
        self._itemTagDict = self._getItemTags()
        self._subitemTagDict = self._getSubitemTags()
        self._deleteExpiredShows()
        self._getLatestShows()

        self._con.close()

        if self._verbose:
            print(f'Added Shows: {self._addedShows}')
            print(f'Deleted Shows: {self._deletedShows}')

    def _getItemTags(self):
        _dict = {}
        _dict = self._addItemTag(_dict, 'None')

        return _dict

    def _addItemTag(self, _dict, tag):
        tag_id = DL_itemTags.getOrInsertItem(self._con, tag)
        _dict[tag] = tag_id

        return _dict

    def _getSubitemTags(self):
        _dict = {}
        _dict = self._addSubitemTag(_dict, 'None')

        return _dict

    def _addSubitemTag(self, _dict, tag):
        tag_id = DL_subitemTags.getOrInsertItem(self._con, tag)
        _dict[tag] = tag_id

        return _dict

    def _deleteExpiredShows(self):
        self._deletedShows += DL_items.deleteExpiredItems(self._con, self._project_id)

    def _getLatestShows(self):
        content = self._getJSONContent(self._baseurl)

        if content is not None:
            shows = self._getShowsContainer(content)
            self._getShows(shows)

    def _getJSONContent(self, url, apiToken = None):
        conn_tries = 0
        while True:

            try:
                wt = round(random.uniform(self._minWaittime, self._maxWaittime), 2)
                if wt > 0:
                    time.sleep(wt)

                headers = {
                    'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
                }

                if apiToken is not None:
                    headers['Api-Auth'] = f'Bearer {apiToken}'
                    headers['Origin'] = 'https://www.zdf.de'
                    headers['Sec-Fetch-Mode'] = 'cors'

                page = self._requests_session.get(url, timeout=self._timeout, headers=headers)
                return json.loads(page.content)

            except requests.exceptions.ConnectionError as e:
                conn_tries += 1
                if conn_tries > 4:
                    print('exit [max reties are reached]')
                    raise e

                time.sleep(60)

    def _getHTMLContent(self, url):

        conn_tries = 0
        while True:

            try:
                wt = round(random.uniform(self._minWaittime, self._maxWaittime), 2)
                if wt > 0:
                    time.sleep(wt)
                url = urllib.parse.urljoin(self._baseurl, url)

                headers = {
                    'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
                }

                page = self._requests_session.get(url, timeout=self._timeout, headers=headers)
                content = BeautifulSoup(page.content, 'lxml')
                return content
            except requests.exceptions.ConnectionError as e:
                conn_tries += 1
                if conn_tries > 4:
                    print('exit [max retries are reached]')
                    raise e

                time.sleep(60)

    def _getShowsContainer(self, content):
        cluster = content['cluster']
        if cluster is not None:
            for c in cluster:
                if c['type'] == 'teaser':
                    return c['teaser']

        return None

    def _getShows(self, shows):

        if shows is None:
            return False

        for show in shows:

            if show['type'] != 'video' or show['contentType'] != 'episode':
                break

            identifier = show['externalId']
            showExists_id = tools.eint(DL_items.existsItem(self._con, self._project_id, identifier))
            if showExists_id > 0 and not self._suppressSkip:
                return False

            detail_url = show['url']
            content = self._getJSONContent(detail_url)
            if content is None or 'document' not in content:
                return False

            mediaStreams = self._getMediaStreams(content['document'])
            if mediaStreams is None:
                return False

            title = show['titel']
            synopsis = show['beschreibung']
            best_quality = 'none'

            if tools.getLength(mediaStreams) > 0:
                best_quality = self._getBestQuality(mediaStreams)

            if best_quality != 'none':

                if showExists_id > 0:
                    DL_items.deleteItem(self._con, showExists_id)

                dt = self._getShowDate(show, content['document'])

                item = (
                    self._project_id,
                    identifier,
                    None,
                    title,
                    synopsis,
                    self._getTag_id(title),
                    self._getPreviewImage(show),
                    dt,
                    None
                )

                row_count, item_id = DL_items.insertItem(self._con, item)
                self._addedShows += row_count

                item = (
                    item_id,
                    None,
                    self._getSubitemTag_id(None),
                    dt,
                    tools.convertDateTime(show['timetolive'],  '%d.%m.%Y %H:%M', '%Y-%m-%d %H:%M:%S'),
                    show['length'],
                    None,
                )

                row_count, subItem_id = DL_subItems.insertSubItem(self._con, item)

                for stream in mediaStreams:

                    quality = stream['quality']
                    if quality is not None:
                        item = (
                            subItem_id,
                            self._getQuality_id(quality),
                            best_quality == stream['quality'],
                            tools.getHoster(stream['url']),
                            None,
                            stream['url'],
                        )

                        DL_links.insertLink(self._con, item)

        return True

    def _getShowDate(self, show, showDetail):
        if 'visibleFrom' in show:
            return tools.convertDateTime(show['visibleFrom'], '%d.%m.%Y %H:%M', '%Y-%m-%d %H:%M:%S')
        elif 'date' in show:
            return tools.convertDateTime(show['date'], '%d.%m.%Y %H:%M', '%Y-%m-%d %H:%M:%S')
        elif 'date' in showDetail:
            return tools.convertDateTime(showDetail['date'], '%d.%m.%Y %H:%M', '%Y-%m-%d %H:%M:%S')
        elif 'timetolive' in show:
            dt = tools.convertDateTime(show['timetolive'], '%d.%m.%Y %H:%M', '%Y-%m-%d %H:%M:%S')
            return dt - relativedelta(years=1)
        elif 'timetolive' in showDetail:
            dt = tools.convertDateTime(showDetail['timetolive'], '%d.%m.%Y %H:%M', '%Y-%m-%d %H:%M:%S')
            return dt - relativedelta(years=1)

        return None

    def _getMediaStreams(self, showDetail):
        if 'formitaeten' in showDetail:
            return list(filter(lambda p: p['type'] == 'h264_aac_ts_http_m3u8_http' and p['quality'] != 'auto',
                               showDetail['formitaeten']))

        if 'sharingUrl' not in showDetail or 'streamApiUrlAndroid' not in showDetail:
            return None

        APIToken = self._getAPIToken(showDetail['sharingUrl'])
        if APIToken is None:
            return None

        retList = []
        content = self._getJSONContent(showDetail['streamApiUrlAndroid'], apiToken=APIToken)
        if content is not None and 'priorityList' in content:
            for priority in content['priorityList']:
                if 'formitaeten' in priority:
                    forminityList = list(filter(lambda p: p['type'] == 'h264_aac_ts_http_m3u8_http' and 'qualities' in p, priority['formitaeten']))
                    if tools.getLength(forminityList) > 0:
                        for forminity in forminityList:
                            qualityList = list(filter(lambda p: p['quality'] != 'auto' and 'audio' in p and 'tracks' in p['audio'], forminity['qualities']))

                            if tools.getLength(qualityList) > 0:
                                for quality in qualityList:
                                    t = quality['audio']['tracks'][0]
                                    retList.append(
                                        {
                                            'type': 'h264_aac_ts_http_m3u8_http',
                                            'url': t['uri'],
                                            'quality': quality['quality'],
                                            'hd': quality['hd'],
                                            'mimeType': forminity['mimeType'],
                                            'language': t['language'],
                                            'class': t['class']
                                        }
                                    )

        if tools.getLength(retList) > 0:
            return retList

        return None

    def _getAPIToken(self, url):
        content = self._getHTMLContent(url)
        if content is not None:
            items = content.find_all('div', class_='b-playerbox b-ratiobox js-rb-live')
            if tools.getLength(items) > 0:
                jsonValue = items[0]['data-zdfplayer-jsb']
                j = json.loads(jsonValue)
                if j is not None and 'apiToken' in j:
                    return j['apiToken']

        return None

    @staticmethod
    def _getBestQuality(mediastreamarray):

        qualityArray = ['veryhigh', 'high', 'med', 'low']
        for q in qualityArray:
            li = list(filter(lambda p: p['quality'] == q, mediastreamarray))
            if tools.getLength(li) > 0:
                return q

        return 'none'

    def _getTag_id(self, title):
        return self._itemTagDict['None']

    @staticmethod
    def _getPreviewImage(show):

        if show['teaserBild'] is not None:
            resArray = ['1920', '1', '1280', '936']

            for res in resArray:

                if show['teaserBild'][res] is not None:
                    return show['teaserBild'][res]['url']

        return None

    def _getSubitemTag_id(self, title):
        _title = title
        return self._subitemTagDict['None']

    def _getQuality_id(self, quality):
        return DL_qualities.getOrInsertItem(self._con, quality)

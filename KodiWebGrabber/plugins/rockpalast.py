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

from libs.core.ardmediathekCore import ardmediathekCore

__VERSION__ = '0.1.0'
__TYPE__ = 'plugin'
__TEMPLATE__ = 'rockpalast'
__PID__ = 'Rockpalast.pid'


def register():
    if __TYPE__ == 'plugin':
        return {
            'name': __name__,
            'file': __file__,
            'template': __TEMPLATE__,
            'version': __VERSION__,
            'type': __TYPE__,
            'pid': __PID__
        }


class core(ardmediathekCore):

    def __init__(self, config, addArgs):
        _channel = 'wdr'
        _mediathek_id = 'Y3JpZDovL3dkci5kZS9Sb2NrcGFsYXN0'
        _core_id = 'ROCKPALAST'

        super().__init__(_core_id, _channel, _mediathek_id, config, addArgs)

    def _getItemTags(self):
        _dict = {}
        _dict = self._addItemTag(_dict, 'None')
        _dict = self._addItemTag(_dict, 'UNPLUGGED')
        _dict = self._addItemTag(_dict, 'LIVEPREVIEW')
        _dict = self._addItemTag(_dict, 'INTERVIEW')

        return _dict

    def _getTag_id(self, title):
        if 'Unplugged:' in title:
            return self._itemTagDict['UNPLUGGED']
        if 'Live-Preview:' in title:
            return self._itemTagDict['LIVEPREVIEW']
        if 'Interview' in title:
            return self._itemTagDict['INTERVIEW']

        return self._itemTagDict['None']

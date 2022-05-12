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

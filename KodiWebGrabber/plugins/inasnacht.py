from libs.core.ardmediathekCore import ardmediathekCore


__VERSION__ = '0.1.0'
__TYPE__ = 'plugin'
__TEMPLATE__ = 'inasnacht'
__PID__ = 'InasNacht.pid'


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
        _channel = 'daserste'
        _mediathek_id = 'Y3JpZDovL2Rhc2Vyc3RlLm5kci5kZS8xNDA5'
        _core_id = 'INASNACHT'

        super().__init__(_core_id, _channel, _mediathek_id, config, addArgs)

    def _getItemTags(self):
        _dict = {}
        _dict = self._addItemTag(_dict, 'None')
        _dict = self._addItemTag(_dict, 'MUSICCLIP')

        return _dict

    def _getTag_id(self, title):
        if 'Musik bei Inas Nacht:' in title:
            return self._itemTagDict['MUSICCLIP']

        return self._itemTagDict['None']

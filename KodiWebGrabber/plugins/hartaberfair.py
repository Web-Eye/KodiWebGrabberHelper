from libs.core.ardmediathekCore import ardmediathekCore

__VERSION__ = '0.1.0'
__TYPE__ = 'plugin'
__TEMPLATE__ = 'hartaberfair'
__PID__ = 'HartAberFair.pid'


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
        _mediathek_id = 'Y3JpZDovL3dkci5kZS9oYXJ0IGFiZXIgZmFpcg'
        _core_id = 'HARTABERFAIR'

        super().__init__(_core_id, _channel, _mediathek_id, config, addArgs)

    def _getTag_id(self, title):
        return 1

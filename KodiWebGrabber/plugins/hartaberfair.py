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


class core:

    def __init__(self, config, addArgs):
        self._config = config
        self._addArgs = addArgs

        self._channel = 'daserste'
        self._mediathek_id = 'Y3JpZDovL3dkci5kZS9oYXJ0IGFiZXIgZmFpcg'
        self._core_id = 'HARTABERFAIR'

    def run(self):
        _core = ardmediathekCore(self._core_id, self._channel, self._mediathek_id, self._config, self._addArgs)
        _core.run()

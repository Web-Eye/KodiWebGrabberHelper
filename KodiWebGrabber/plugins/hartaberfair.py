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


class hart:

    def __init__(self, myid):
        self._id = myid
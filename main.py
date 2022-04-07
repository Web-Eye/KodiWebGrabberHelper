import argparse

from libs.common.PIDhandler import PIDhandler
import sys
from os import _exit

from libs.common.enums import cores
from libs.core.ardmediathekCore import ardmediathekCore
from libs.common.tools import GetPIDFile, GetConfigFile, ReadConfig


def doHartAberFair(config):
    pidfile = GetPIDFile("HartAberFair.pid")
    h = PIDhandler(pidfile)
    h.checkPID()
    core = None

    try:
        core = ardmediathekCore(cores.HARTABERFAIR, 'daserste', 'Y3JpZDovL3dkci5kZS9oYXJ0IGFiZXIgZmFpcg', config)
        core.run()

    except KeyboardInterrupt:
        if core is not None:
            print("interupt")
            pass

    h.unlinkPID()
    _exit(1)


def doInasNacht(config):
    pidfile = "InasNacht.pid"
    h = PIDhandler(pidfile)
    h.checkPID()

    h.unlinkPID()
    _exit(1)


def doRockpalast(config):
    pidfile = "Rockpalast.pid"
    h = PIDhandler(pidfile)
    h.checkPID()

    h.unlinkPID()
    _exit(1)


def doHDTrailers(config):
    pidfile = "HDTrailers.pid"
    h = PIDhandler(pidfile)
    h.checkPID()

    h.unlinkPID()
    _exit(1)


def doNothing(config):
    pass


def LoadConfig():
    configFile = GetConfigFile()
    return ReadConfig(configFile)


def isValidConfig(config):
    if config is None:
        return False

    if 'host' not in config or config['host'] == '':
        return False

    if 'port' not in config or config['port'] == '' or config['port'] == 0:
        return False

    if 'user' not in config or config['user'] == '':
        return False

    if 'password' not in config or config['password'] == '':
        return False
    return True


def main():
    parser = argparse.ArgumentParser(
        description='runner',
        epilog="That's all folks"
    )

    parser.add_argument('-t', '--template',
                        metavar='template switch',
                        type=str,
                        help='Accepts any of these values: hartaberfair, inasnacht, rockpalast, hdtrailers',
                        choices=['hartaberfair', 'inasnacht', 'rockpalast', 'hdtrailers'])

    try:
        args = parser.parse_args()
    except SystemExit:
        sys.exit()

    config = LoadConfig()
    if not isValidConfig(config):
        print('invalid config')
        sys.exit()

    template = args.template

    {
        'hartaberfair': doHartAberFair,
        'inasnacht': doInasNacht,
        'rockpalast': doRockpalast,
        'hdtrailers': doHDTrailers,
        None: doNothing
    }[template](config)


if __name__ == '__main__':
    main()

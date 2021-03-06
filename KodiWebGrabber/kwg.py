import argparse

import sys
from os import _exit

from libs.common.PIDhandler import PIDhandler
from libs.common.enums import coreEnum
from libs.core.ardmediathekCore import ardmediathekCore
from libs.core.databaseCore import databaseCore
from libs.core.hdtrailersCore import hdtrailersCore
from libs.common.tools import GetPIDFile, GetConfigFile, ReadConfig, SaveConfig

__VERSION__ = '1.1.2+Beta'
__VERSIONSTRING__ = f'KodiWebGrabberHelper Version {__VERSION__}'


def doHartAberFair(config, addArgs):
    pidfile = GetPIDFile("HartAberFair.pid")
    h = PIDhandler(pidfile)
    h.checkPID()
    core = None

    try:
        core = ardmediathekCore(coreEnum.HARTABERFAIR, 'daserste', 'Y3JpZDovL3dkci5kZS9oYXJ0IGFiZXIgZmFpcg', config,
                                addArgs)
        core.run()

    except KeyboardInterrupt:
        if core is not None:
            print("interupt")
            pass

    h.unlinkPID()
    _exit(1)


def doInasNacht(config, addArgs):
    pidfile = "InasNacht.pid"
    h = PIDhandler(pidfile)
    h.checkPID()
    core = None

    try:
        core = ardmediathekCore(coreEnum.INASNACHT, 'daserste', 'Y3JpZDovL2Rhc2Vyc3RlLm5kci5kZS8xNDA5', config, addArgs)
        core.run()

    except KeyboardInterrupt:
        if core is not None:
            print("interupt")
            pass

    h.unlinkPID()
    _exit(1)


def doRockpalast(config, addArgs):
    pidfile = "Rockpalast.pid"
    h = PIDhandler(pidfile)
    h.checkPID()
    core = None

    try:
        core = ardmediathekCore(coreEnum.ROCKPALAST, 'wdr', 'Y3JpZDovL3dkci5kZS9Sb2NrcGFsYXN0', config, addArgs)
        core.run()

    except KeyboardInterrupt:
        if core is not None:
            print("interupt")
            pass

    h.unlinkPID()
    _exit(1)


def doHDTrailers(config, addArgs):
    pidfile = "HDTrailers.pid"
    h = PIDhandler(pidfile)
    h.checkPID()
    core = None

    try:
        core = hdtrailersCore(coreEnum.HDTRAILERS, config, addArgs)
        core.run()

    except KeyboardInterrupt:
        if core is not None:
            print("interupt")
            pass

    h.unlinkPID()
    _exit(1)


def doNothing(config, addArgs):
    pass


def doInputConfig():
    host = input('Enter the MariDB host (localhost): ')
    port = input('Enter the MariaDB port (3306): ')
    user = input('Enter the MariaDB username: ')
    password = input('Enter the users password: ')

    if host == '':
        host = 'localhost'

    if port == '':
        port = '3306'

    configFile = GetConfigFile()
    config = {
        'host': host,
        'port': int(port),
        'user': user,
        'password': password
    }

    SaveConfig(configFile, config)


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

    parser.add_argument('-c', '--config',
                        action='store_true')

    parser.add_argument('-v', '--version',
                        action='store_true')

    parser.add_argument('--verbose',
                        action='store_true')

    parser.add_argument('-p', '--page',
                        type=int
                        )

    parser.add_argument('-pc', '--pagecount',
                        type=int
                        )

    parser.add_argument('-s', '--suppressSkip',
                        action='store_true')

    parser.add_argument('-wt', '--waittime',
                        type=float,
                        nargs=2,
                        metavar=('min waittime', 'max waittime'),
                        help='Waits in a range of seconds before sending the next request.',
                        )

    try:
        args = parser.parse_args()
    except SystemExit:
        sys.exit()

    if args.version:
        print(__VERSIONSTRING__)

    if args.config:
        doInputConfig()

    config = LoadConfig()
    if not isValidConfig(config):
        print('invalid config')
        sys.exit()

    db = databaseCore(config)
    if not db.check_database():
        print('unable to check database')
        sys.exit()

    if args.page is None:
        args.page = 1

    template = args.template
    addArgs = {
        'page_begin': args.page,
        'page_count': args.pagecount,
        'suppress_skip': args.suppressSkip,
        'wait_time': args.waittime,
        'verbose': args.verbose
    }

    {
        'hartaberfair': doHartAberFair,
        'inasnacht': doInasNacht,
        'rockpalast': doRockpalast,
        'hdtrailers': doHDTrailers,
        None: doNothing
    }[template](config, addArgs)


if __name__ == '__main__':
    main()

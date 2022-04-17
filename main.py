import argparse
from libs.common.PIDhandler import PIDhandler
import sys
from os import _exit

from libs.common.enums import coreEnum
from libs.core.ardmediathekCore import ardmediathekCore
from libs.core.databaseCore import databaseCore
from libs.core.hdtrailersCore import hdtrailersCore
from libs.common.tools import GetPIDFile, GetConfigFile, ReadConfig, SaveConfig

__VERSION__ = '1.0.0+Beta'
__VERSIONSTRING__ = f'KodiWebGrabberHelper Version {__VERSION__}'


def doHartAberFair(config, verbose):
    pidfile = GetPIDFile("HartAberFair.pid")
    h = PIDhandler(pidfile)
    h.checkPID()
    core = None

    try:
        core = ardmediathekCore(coreEnum.HARTABERFAIR, 'daserste', 'Y3JpZDovL3dkci5kZS9oYXJ0IGFiZXIgZmFpcg', config, verbose)
        core.run()

    except KeyboardInterrupt:
        if core is not None:
            print("interupt")
            pass

    h.unlinkPID()
    _exit(1)


def doInasNacht(config, verbose):
    pidfile = "InasNacht.pid"
    h = PIDhandler(pidfile)
    h.checkPID()
    core = None

    try:
        core = ardmediathekCore(coreEnum.INASNACHT, 'daserste', 'Y3JpZDovL2Rhc2Vyc3RlLm5kci5kZS8xNDA5', config, verbose)
        core.run()

    except KeyboardInterrupt:
        if core is not None:
            print("interupt")
            pass

    h.unlinkPID()
    _exit(1)


def doRockpalast(config, verbose):
    pidfile = "Rockpalast.pid"
    h = PIDhandler(pidfile)
    h.checkPID()
    core = None

    try:
        core = ardmediathekCore(coreEnum.ROCKPALAST, 'wdr', 'Y3JpZDovL3dkci5kZS9Sb2NrcGFsYXN0', config, verbose)
        core.run()

    except KeyboardInterrupt:
        if core is not None:
            print("interupt")
            pass

    h.unlinkPID()
    _exit(1)


def doHDTrailers(config, verbose):
    pidfile = "HDTrailers.pid"
    h = PIDhandler(pidfile)
    h.checkPID()
    core = None

    try:
        core = hdtrailersCore(coreEnum.HDTRAILERS, config, verbose)
        core.run()

    except KeyboardInterrupt:
        if core is not None:
            print("interupt")
            pass

    h.unlinkPID()
    _exit(1)


def doNothing(config, verbose):
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

    template = args.template

    {
        'hartaberfair': doHartAberFair,
        'inasnacht': doInasNacht,
        'rockpalast': doRockpalast,
        'hdtrailers': doHDTrailers,
        None: doNothing
    }[template](config, args.verbose)


if __name__ == '__main__':
    main()

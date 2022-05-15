import argparse
import os

import sys
from os import _exit
import importlib
from os.path import isfile

from libs.common.PIDhandler import PIDhandler
from libs.core.databaseCore import databaseCore
from libs.common.tools import GetPIDFile, GetConfigFile, ReadConfig, SaveConfig

__VERSION__ = '1.2.0+Beta'
__VERSIONSTRING__ = f'KodiWebGrabberHelper Version {__VERSION__}'


def runTemplate(plugins, template, config, addArgs):
    if plugins is not None and len(plugins) > 0 and template is not None and template:
        plugin = next(filter(lambda p: p.get('template') == template, plugins), None)
        if plugin is not None:
            pidfile = GetPIDFile(plugin.get('pid'))
            h = PIDhandler(pidfile)
            h.checkPID()
            core = None

            try:
                m = importlib.import_module(plugin.get('name'))
                core = m.core(config, addArgs)
                core.run()

            except KeyboardInterrupt:
                if core is not None:
                    print("interupt")
                    pass

            h.unlinkPID()
            _exit(1)


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


def getPlugins():

    plugins = []
    templates = []
    helpTuple = ()

    cwd = os.path.join(os.getcwd(), 'plugins')
    for f in os.listdir(cwd):
        if isfile(os.path.join(cwd, f)):
            try:
                m = importlib.import_module('plugins.' + f[:-3])
                plugin = m.register()
                if plugin is not None:
                    plugins.append(plugin)
                    templates.append(plugin.get('template'))
                    helpTuple += (plugin.get('template'), )
            except AttributeError:
                pass

    helpString = 'Accepts any of these values: ' + ', '.join(helpTuple)

    return plugins, templates, helpString


def main():
    plugins, templates, helpString = getPlugins()
    if plugins is None or len(plugins) == 0:
        print('no plugin found')
        return

    parser = argparse.ArgumentParser(
        description='runner',
        epilog="That's all folks"
    )

    parser.add_argument('-t', '--template',
                        metavar='template switch',
                        type=str,
                        help=helpString,
                        choices=templates)

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

    runTemplate(plugins, template, config, addArgs)


if __name__ == '__main__':
    main()

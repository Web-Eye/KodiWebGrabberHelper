import json
import os.path
import sys


def GetPIDFile(filename):
    if sys.platform == "linux" or sys.platform == "linux2":
        return os.path.join('/var/run/', filename)

    elif sys.platform == "darwin":
        # MAC OS X
        return None

    elif sys.platform == "win32":
        return os.path.join('C:\\python', filename)

    return None


def GetConfigFile():
    if sys.platform == "linux" or sys.platform == "linux2":
        return '/etc/KodiGrabberHelper.config'

    elif sys.platform == "darwin":
        # MAC OS X
        return None

    elif sys.platform == "win32":
        return 'C:\\python\\KodiGrabberHelper.config'

    return None


def ReadConfig(filename):
    if os.path.isfile(filename):
        with open(filename) as json_data_file:
            return json.load(json_data_file)

    return None

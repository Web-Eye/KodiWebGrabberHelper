import json
import os.path
import sys
import time
from datetime import datetime
from urllib.parse import urlparse


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


def SaveConfig(filename, json_data):
    with open(filename, 'w') as outfile:
        json.dump(json_data, outfile, indent=4)


def getDateTime(strDateTime, strFormat):
    if strDateTime is not None:
        return datetime(*(time.strptime(strDateTime, strFormat)[0:6]))
    return None


def datetimeToString(dt, dstFormat):
    return dt.strftime(dstFormat)


def convertDateTime(strDateTime, srcFormat, dstFormat):
    dt = getDateTime(strDateTime, srcFormat)
    if dt is not None:
        return dt.strftime(dstFormat)

    return None


def maxDate(date1, date2):
    if date1 is None:
        return date2

    if date2 is None:
        return date1

    if date1 > date2:
        return date1

    return date2


def getHoster(url):
    o = urlparse(url)
    return o.hostname


def getLength(o):
    if o is None:
        return 0

    return len(o)


def eint(value, default=0):
    if value is not None:
        return int(value)

    return default


def estr(value, default=''):
    if value is not None:
        return str(value)

    return default
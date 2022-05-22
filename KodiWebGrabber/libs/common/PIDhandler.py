# -*- coding: utf-8 -*-
# Copyright 2022 WebEye
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import os
import sys
import psutil as psutil


def checkPidRunning(pid):
    if sys.platform == "linux" or sys.platform == "linux2":

        try:
            os.kill(pid, 0)
        except OSError:
            return False
        else:
            return True

    else:
        return False


class PIDhandler(object):
    """description of class"""

    def __init__(self, filename):

        self.pid = str(os.getpid())
        if sys.platform == "linux" or sys.platform == "linux2":
            self.pidfile = os.path.join("/var/run/", filename)
        elif sys.platform == "win32":
            if not os.path.exists("c:\\python\\"):
                os.makedirs("c:\\python\\")
            self.pidfile = os.path.join("c:\\python\\", filename)

    def checkPID(self):

        if os.path.isfile(self.pidfile) and checkPidRunning(int(open(self.pidfile, 'r').readlines()[0])):
            print("%s already exists, exiting" % self.pidfile)
            sys.exit()
        else:
            open(self.pidfile, 'w').write(self.pid)

    def checkPIDSilent(self):
        if os.path.isfile(self.pidfile):
            pid = int(open(self.pidfile, 'r').readlines()[0])
            if pid is not None:
                try:
                    process = psutil.Process(pid)
                    return process.is_running()
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    return False

        return False

    def unlinkPID(self):
        os.unlink(self.pidfile)

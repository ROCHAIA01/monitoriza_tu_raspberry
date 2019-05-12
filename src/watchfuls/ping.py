#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Monitorize your Raspberry Pi
#
# Copyright © 2019  Javier Pastor (aka VSC55)
# <jpastor at cerebelum dot net>
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

import importlib

class Watchful():
    def __init__(self, monitor):
        self.monitor = monitor
        pass

    def check(self):
        utils = importlib.import_module('__utils')

        returnDict = {}
        for (key, value) in self.monitor.config['ping'].items():
            print("Ping: {0} - Enabled: {1}".format(key, value))
            if value:
                returncode = utils.execute_call('ping -c 1 {0}'.format(key))
                returnDict[key] = {}
                returnDict[key]['status']=False if returncode == 1 else True
                returnDict[key]['message']='Ping: {0} {1}'.format(key, 'UP' if returnDict[key]['status'] else 'DOWN' )
        
        return True, returnDict

if __name__ == '__main__':
    wf = Watchful()
    print(wf.check())

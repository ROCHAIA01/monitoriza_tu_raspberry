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

"""Module Main."""


import os
import sys
import time
import argparse
import lib.debug
import lib.monitor
import lib.config


class Main(object):

    debug = None
    monitor = None
    cfg_general = None
    cfg_monitor = None
    cfg_modules = None
    __cfg_file_config = 'config.json'
    __cfg_file_monitor = 'monitor.json'
    __cfg_file_modules = 'modules.json'

    def __init__(self, args_get):
        self._daemon_mode = False
        self._timer_check = 0
        self.__sys_path_append([self._modules_dir])
        self.__args_set(args_get)
        self.__init_debug()
        self.__init_config()
        self.__init_monitor()
        self.__args_cmd(args_get)

    def __init_debug(self):
        self.debug = lib.debug.Debug(True)

    def __init_config(self):
        self.cfg_general = lib.config.Config(os.path.join(self._config_dir, self.__cfg_file_config),
                                             obj_debug=self.debug)
        self.cfg_general.read()
        if self.__check_config():
            self.__default_conf()
            self.__read_config()
        else:
            raise Exception("Error load config.")

    def __check_config(self):
        if self.cfg_general:
            return True
        return False

    def __default_conf(self):
        if self.__check_config:
            if not self.cfg_general.is_exist_conf(['daemon', 'timer_check']):
                self.cfg_general.set_conf(['daemon', 'timer_check'], 300)

            if not self.cfg_general.is_exist_conf(['global', 'debug']):
                self.cfg_general.set_conf(['global', 'debug'], False)

            return True
        return False

    def __read_config(self):
        if self.__verbose:
            self.debug.enabled = True
        else:
            self.debug.enabled = self.cfg_general.get_conf(['global', 'debug'], self.debug.enabled)

        if self.__timer_check_forze:
            self._timer_check = self.__timer_check_forze
        else:
            self._timer_check = self.cfg_general.get_conf(['daemon', 'timer_check'], self._timer_check)

    @staticmethod
    def __sys_path_append(list_dir):
        for f in list_dir:
            if os.path.isdir(f):
                if f not in sys.path:
                    sys.path.append(f)

    def __init_monitor(self):
        self.monitor = lib.monitor.Monitor(self._dir, self._config_dir, self._modules_dir, self._var_dir, self.debug)

    @property
    def _is_mode_dev(self):
        if self._dir.find('src') != -1:
            return True
        return False

    @property
    def _dir(self):
        """Path run program.

        Returns:
        str: Returning value

        """
        return os.path.dirname(os.path.abspath(__file__))

    @property
    def _modules_dir(self):
        """Path modules.

        Returns:
        str: Returning value

        """
        return os.path.join(self._dir, 'watchfuls')

    @property
    def _lib_dir(self):
        """Path lib's.

        Returns:
        str: Returning value

        """
        return os.path.join(self._dir, 'lib')

    @property
    def _config_dir(self):
        """Path config files.

        Returns:
        str: Returning value

        """
        if self.__path_config:
            return self.__path_config
        elif self._is_mode_dev:
            return os.path.normpath(os.path.join(self._dir, '../data/'))
        else:
            return '/etc/watchful/'

    @property
    def _var_dir(self):
        """Path /var/lib...

        Returns:
        str: Returning value

        """
        if self._is_mode_dev:
            return '/var/lib/watchful/dev/'
        else:
            return '/var/lib/watchful/'

    def __args_set(self, args_get):
        if args_get:
            for key, value in args_get.items():
                if key == 'path':
                    self.__path_config = value

                elif key == 'verbose':
                    self.__verbose = value

                elif key == 'timer_check':
                    self.__timer_check_forze = value

                elif key == 'daemon_mode':
                    self.__daemon_mode = value

    def __args_cmd(self, args_get):
        if args_get:
            for key, value in args_get.items():
                if key == 'clear_status':
                    if value:
                        if self.monitor:
                            self.monitor.clearStatus()

    @property
    def _daemon_mode(self):
        return self.__daemon_mode

    @_daemon_mode.setter
    def _daemon_mode(self, val):
        self.__daemon_mode = val

    @property
    def _timer_check(self):
        if self.__timer_check:
            return self.__timer_check
        return 0

    @_timer_check.setter
    def _timer_check(self, val):
        if not val:
            val = 0
        elif isinstance(val, str):
            if not val.isnumeric():
                val = 0
            else:
                val = int(val)
        elif isinstance(val, float):
            val = int(val)
        elif not isinstance(val, int):
            val = 0

        if int(val) < 0:
            val = 0

        self.__timer_check = int(val)

    def start(self):
        if not self._daemon_mode:
            self.debug.print("Run Mode Single Process", lib.debug.DebugLevel.debug)
            self.monitor.check()
        else:
            self.debug.print("Run Mode Daemon", lib.debug.DebugLevel.debug)
            while True:
                self.monitor.check()
                if self._timer_check == 0:
                    break
                self.debug.print("Waiting {0} seconds...".format(args['timer_check']), lib.debug.DebugLevel.debug)
                try:
                    time.sleep(self._timer_check)
                except KeyboardInterrupt:
                    self.debug.print("Process cancel  by the user!!", lib.debug.DebugLevel.info)
                    try:
                        sys.exit(0)
                    except SystemExit:
                        os._exit(0)
                except Exception as e:
                    self.debug.Exception(e)


def arg_check_dir_path(path):
    if not path:
        return ''
    elif os.path.isdir(path):
        return path
    else:
        raise argparse.ArgumentTypeError("{0} is not a valid path".format(path))


def arg_check_timer(timercheck):
    if timercheck.isnumeric() and int(timercheck) > 0:
        return timercheck
    else:
        raise argparse.ArgumentTypeError("{0} is not a valid timer".format(timercheck))


if __name__ == "__main__":

    # allow_abbrev modo estricto en la detección de argumento, de lo contrario --pat lo reconocería como --path
    ap = argparse.ArgumentParser(allow_abbrev=False)
    ap.add_argument(
        '-c', '--clear',
        default=False,
        action="store_true",
        dest="clear_status",
        help="clear status.json"
    )
    ap.add_argument(
        '-d', '--daemon',
        default=False,
        action="store_true",
        dest="daemon_mode",
        help="start mode daemon"
    )
    ap.add_argument(
        '-t', '--timer',
        default=None,
        type=arg_check_timer,
        dest="timer_check",
        help="timer interval of the check in daemon mode"
    )
    ap.add_argument(
        '-v', '--verbose',
        default=False,
        action="store_true",
        dest="verbose",
        help="verbose mode true"
    )
    ap.add_argument(
        '-p', '--path',
        default=None,
        type=arg_check_dir_path,
        dest="path",
        help="path config files"
    )
    args = vars(ap.parse_args())

    main = Main(args)
    main.start()

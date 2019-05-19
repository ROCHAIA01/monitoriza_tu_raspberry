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

import globales
import datetime
import lib.configStore

__all__ = ['Config']

class Config(lib.configStore.ConfigStore):

    __load=None
    __update=None

    def __init__(self, file, init_data=None):
        super().__init__(file)
        self.data = init_data

    @property
    def data(self):
        return self.__data

    @data.setter
    def data(self, val):
        self.__update = datetime.datetime.now()
        self.__data = val

    @property
    def isChanged(self):
        if self.__update and not self.__load:
            #Se han insertado datos manulamente, no se ha leido ningun archivo.
            return True
        if not self.__update or not self.__load:
            #No se ha cargado ningun archivo ni se han insertado datos.
            return False
        if self.__update > self.__load:
            #la fecha de actualizacione es superior a la de carga por lo que se ha modificado.
            return True
        return False

    @property
    def isLoad(self):
        if self.__load != None:
            return True
        return False

    def read(self, returnData=True):
        try:
            self.data = super().read()
            self.__load=datetime.datetime.now()
            self.__update=self.__load
            
        except Exception as e:
            globales.GlobDebug.Exception(e)
            self.__load=None
            self.__update=None

        if returnData:
            return self.data
        
    def save(self):
        try:
            super().save(self.data)
            self.__load=datetime.datetime.now()
            self.__update=self.__load
        except Exception as e:
            globales.GlobDebug.Exception(e)
            return False
        return True

    def get_conf(self, findkey, default_val=None, returnType=None):
        return self.__get_conf(self.data, findkey , default_val, returnType)

    def __get_conf(self, data, findkey, default_val=None, returnType=None):
        dataReturn = None
        if data:
            if isinstance(findkey, dict):
                """
                Se anula ya dict no mantine simpre el orden de los elementos.
                https://docs.python.org/3/library/collections.html#collections.OrderedDict

                Ordered dictionaries are just like regular dictionaries but have some 
                extra capabilities relating to ordering operations. They have become less 
                important now that the built-in dict class gained the ability to remember 
                insertion order (this new behavior became guaranteed in Python 3.7).
                """
                raise ValueError('findkey type dict in not valid.')

            elif isinstance(findkey, list) or isinstance(findkey, tuple):
#                print("findkey:",findkey)
#                print("count:",len(findkey))

                if isinstance(findkey, tuple):
                    findkey = list(findkey)

                i = findkey.pop(0)
                    
#                print("i:",i)
                if i in data.keys():
#                    print("d:", data[i])
#                    print("t:",type(data[i]))

                    if isinstance(data[i], list) or isinstance(data[i], tuple) or isinstance(data[i], dict):
                        if len(findkey) == 0:
                            dataReturn = data[i]
                        else:
                            dataReturn = self.__get_conf(data[i], findkey, default_val, returnType)
                    else:
                        if len(findkey) == 0:
                            dataReturn = data[i]
                else:
                    return None

            else:
#                print ("other:", findkey)
#                print ("other dataType:", type(data))
#                print ("other data:", data)
                if findkey in data.keys():
                    dataReturn = data[findkey]
                else:
                    dataReturn = None

        if dataReturn != None:
            return dataReturn

        if isinstance(returnType, list):
            if not default_val:
                return []
        elif isinstance(returnType, dict):
            if not default_val:
                return {}
        elif isinstance(returnType, tuple):
            if not default_val:
                return ()
        elif isinstance(returnType, int) or isinstance(returnType, bool):
            if default_val != None:
                return None
        else:
            if not default_val:
                return ''

        return default_val
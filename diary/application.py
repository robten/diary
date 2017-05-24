#!/usr/bin/env python3
# coding=utf-8

import os
from utilities import MetaSingleton
from diary.configmanager import INImanager


class App(metaclass=MetaSingleton):
    """
    A Class for storing an managing the configuration of an application.
    It allows to store and read configuration data permanently in a configuration file.
    Beside that it can work as a central hub for managing the aplication flow.
    """
    def __init__(self, name=None):

        self.app_name = name if name else os.path.basename(__file__)
        self.storage_path = os.getcwd()
        self.conf_path = os.path.join(self.storage_path,
                                      os.path.normpath("config/config.ini"))
        self.conf = INImanager(path=self.conf_path)

        if not os.path.exists(self.conf_path):
            self.conf.set("name", self.app_name, section="app")
            self.conf.set("storage", self.storage_path, section="app")
            self.conf.save()
        else:
            self.conf.load()
            self.app_name = str(self.conf.get("name", section="app"))
            self.storage_path = os.path.normpath(self.conf.get("storage", section="app"))

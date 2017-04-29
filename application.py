#!/usr/bin/env python3
# coding=utf-8

import configparser
import os
from utilities import MetaSingleton


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
        self.conf = configparser.ConfigParser()

        if not os.path.exists(self.conf_path):
            self.conf["app"] = {"name": self.app_name,
                                "storage": self.storage_path}
            self.write_conf()
        else:
            self.read_conf()
            self.app_name = str(self.conf.get("app", "name", fallback=self.app_name))
            self.storage_path = os.path.normpath(self.conf.get("app", "storage",
                                                               fallback=self.storage_path))

    def write_conf(self):
        with open(self.conf_path, 'w') as conf_file:
            self.conf.write(conf_file)

    def read_conf(self):
        with open(self.conf_path) as conf_file:
            self.conf.read_file(conf_file)

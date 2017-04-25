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
                                      os.path.normpath("config/config.txt"))
        self.conf = configparser.ConfigParser()

        # TODO Should the config file been created or read in __init__?
        if not os.path.exists(self.conf_path):
            self.conf["app"] = {"Name": self.app_name,
                                "Storage": self.storage_path}
            self.write_conf()
        else:
            self.read_conf()

    def write_conf(self):
        with open(self.conf_path, 'w') as conf_file:
            self.conf.write(conf_file)

    def read_conf(self):
        with open(self.conf_path) as conf_file:
            self.conf.read_file(conf_file)

    def set_conf(self, key, value, section="app"):
        """
        Method for setting entries in the configuration of this App object
        :param key: The key of a key-value pair inside the configuration dict
        :param value: The value of a key-value pair inside the configuration dict
        :param section: Optional for inserting into a new section, defaults to "App" if is omitted
        """
        section_conf = self.conf[str(section)]
        section_conf[str(key)] = value

    def get_conf(self, key, section="app"):
        return self.conf[section][key]

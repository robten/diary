#!/usr/bin/env python3
# coding: utf-8

from configparser import ConfigParser


class ManagerBase:
    def __init__(self, path=None, file=None):
        self._config_path = path
        self._config_file = file
        self.default_section = "DEFAULT"
        self._data = {self.default_section: {}}

    def set(self, key, value, section=None):
        section = section if section else self.default_section
        self._data[section].__setitem__(key, value) # todo: handle implicit creation of a new section

    def get(self, key, section=None):
        section = section if section else self.default_section
        return self._data[section].__getitem__(key) # todo: key not found exception

    def get_data(self):
        return self._data


class INImanager(ManagerBase):
    def __init__(self, *args, **kwargs):
        super(INImanager, self).__init__(*args, **kwargs)
        self._config = ConfigParser()

    def save(self):
        self._config = self.get_data() # todo: search for alternativ method for assignment
        if self._config_path:
            with open(self._config_path, 'w') as file:
                self._config.write(file)
        elif self._config_file:
            self._config.write(self._config_file)
        else:
            raise FileNotFoundError()

    def load(self):
        if self._config_path:
            with open(self._config_path) as file:
                self._config.read_file(file)
        elif self._config_file:
            self._config.read_file(self._config_file)
        else:
            raise FileNotFoundError()

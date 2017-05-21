#!/usr/bin/env python3
# coding: utf-8

from configparser import ConfigParser


class ManagerBase:
    def __init__(self, path=None, file=None):
        self._config_path = path
        self._config_file = file
        self._default_section = "DEFAULT"
        self._data = {self._default_section: {}}

    def set(self, key, value, section=None):
        section = section if section else self._default_section
        if section not in self._data:  # TODO: Handling non-existent sections
            self._data[section] = dict()
        self._data[section][key] = value

    def get(self, key, section=None):
        section = section if section else self._default_section
        return self._data[section][key]


class INImanager(ManagerBase):
    def __init__(self, *args, **kwargs):
        super(INImanager, self).__init__(*args, **kwargs)
        self._config = ConfigParser()

    def save(self):
        self._config.read_dict(self._data)
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

        self._data = dict(self._config._sections)  # TODO: Find a less dirty way then to use private attributes
        self._data[self._default_section] = dict(self._config.defaults())

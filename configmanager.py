#!/usr/bin/env python3
# coding: utf-8

from configparser import ConfigParser


class INImanager:
    def __init__(self, path=None, file=None):
        self._config_path = path
        self._config_file = file
        self._config = ConfigParser()
        self.default_section = "DEFAULT"

    def set(self, key, value, section=None):
        section = section if section else self.default_section
        self._config.set(section, key, value)

    def get(self, key, section=None):
        section = section if section else self.default_section
        return self._config.get(section, key)

    def save(self):
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

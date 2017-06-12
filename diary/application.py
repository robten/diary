#!/usr/bin/env python3
# coding=utf-8

from utilities import MetaSingleton


class App(metaclass=MetaSingleton):
    """
    A Class for storing and managing components of an application.
    It allows to store and read configuration data permanently in a configuration file.
    Beside that it can work as a central hub for managing the aplication flow.
    """
    def __init__(self, conf_component, db_component, storage_component, view_component):
        self._conf = conf_component
        self._db = db_component
        self._storage = storage_component
        self._view = view_component

    def load_conf(self, path):
        self._conf.set_source(path=path)
        self._conf.load()

    def is_ready(self, component):
        pass

    def setup_database(self, file=":memory:", user=None, password=None, url=None, db=None):
        pass

    def setup_storage(self, location=None):
        pass

    def start(self):
        pass

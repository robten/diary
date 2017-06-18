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

    def load_conf(self, path=None):
        if path:
            self._conf.set_source(path=path)
            self._conf.load()
        elif self._conf.ready():
            self._conf.load()
        else:
            raise FileNotFoundError("path not set hence config can't load")
        #  TODO: check if any components can be set initially with loaded config file

    def is_ready(self, component):
        attr = "_" + component
        try:
            result = self.__dict__[attr].ready()
        except KeyError:
            raise KeyError("No component by the name of '" + component + "'.")
        else:
            return result

    def setup_database(self, file=":memory:", user=None, password=None, url=None, db=None):
        if user and password and url and db:
            self._db.set(user=user, password=password, url=url, db=db)
        else:
            self._db.set(file=file)

    def setup_storage(self, location=None):
        self._storage.set(location=location)

    def setup_view(self, **kwargs):
        self._view.set(**kwargs)

    def start(self):
        #  TODO: Implement App.start() when all components are finished
        pass

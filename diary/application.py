#!/usr/bin/env python3
# coding=utf-8

from functools import wraps
from utilities import MetaSingleton


class App(metaclass=MetaSingleton):
    """
    A Class for storing and managing components of an application.
    It allows to store and read configuration data permanently in a configuration file.
    Beside that it can work as a central hub for managing the aplication flow.
    """
    def __init__(self, conf=None, db=None, storage=None, view=None):
        self._conf = conf
        self._db = db
        self._storage = storage
        self._view = view

    def load_conf(self, path=None):
        if path:
            self._conf.set_source(path=path)
            self._conf.load()
        elif self.is_ready("conf"):
            self._conf.load()
        else:
            raise FileNotFoundError("path not set hence config can't load")
        #  TODO: check if any components can be set initially with loaded config file

    def is_ready(self, component):
        attr = "_" + component
        if not hasattr(self, attr):
            raise KeyError("App has no component by the name of '{}'.".format(component))
        if not hasattr(getattr(self, attr), "is_valid"):
            raise TypeError("No valid component is set for '{}' in App.".format(component))
        return getattr(self, attr).is_valid()

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


class Component:
    """
    Base class for all components used by App class. It serves both: providing a common
    interface and internal manageing functionality.
    """
    def __init__(self):
        self._state_postive = dict()
        self._state_negative = dict()
        self._states_alternate_positive = dict()
        self._states_alternate_negative = dict()

    @classmethod
    def dependent(cls, func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if self.is_valid():
                return func(self, *args, **kwargs)
            else:
                raise ValueError("{} object is not in a valid state.".format(cls))
        return wrapper

    def valid_state(self, member, value, alternate=False):
        if not alternate:
            self._state_postive[member] = value
        else:
            self._states_alternate_positive.update({member: value})
        return value

    def invalid_state(self, member, value, alternate=False):
        if not alternate:
            self._state_negative[member] = value
        else:
            self._states_alternate_negative.update({member: value})
        return value

    def is_valid(self):
        for member in self._state_postive:
            if self._state_postive[member] != self.__dict__[member]:
                return False
        for member in self._state_negative:
            if self._state_negative[member] == self.__dict__[member]:
                return False
        if len(self._states_alternate_positive) > 0:
            false_state = 0
            for member, value in self._states_alternate_positive.items():
                if value != self.__dict__[member]:
                    false_state += 1
            if false_state == len(self._states_alternate_positive):
                return False
        if len(self._states_alternate_negative) > 0:
            false_state = 0
            for member, value in self._states_alternate_negative.items():
                if value == self.__dict__[member]:
                    false_state += 1
            if false_state == len(self._states_alternate_negative):
                return False
        return True

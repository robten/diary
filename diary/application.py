#!/usr/bin/env python3
# coding=utf-8

from pathlib import Path
from functools import wraps
from utilities import MetaSingleton, standard_data_dir, standard_config_dir
from abc import ABCMeta, abstractmethod


class App(metaclass=MetaSingleton):
    """
    A Class for storing and managing components of an application.
    It allows to store and read configuration data permanently in a configuration file.
    Beside that it can work as a central hub for managing the application flow.
    """
    def __init__(self, app_name, config=None, db=None, storage=None, view=None):
        self.name = app_name
        self.config = config
        self.db = db
        self.storage = storage
        self.view = view
        self.default_driver = "sqlite"
        self.default_root = standard_data_dir(self.name)
        self.default_config = standard_config_dir(self.name) / "config.ini"

    def load_config(self, path=None):
        if path:
            config_path = Path(path)
        else:
            config_path = self.default_config
        if not config_path.is_file():
            raise FileNotFoundError("Given or default path '{}' is not valid.".format(config_path))
        self.config.initialize(path=config_path)
        if self.is_ready("config"):
            self.config.load()
        else:
            raise ValueError("Config component isn't in a valid state, hence config can't load")
        #  TODO: check if any components can be set initially with loaded config file

    def config_init_db(self, section="DATABASE"):  # TODO: obsolete (in component)
        if not self.is_ready("config"):
            return False
        conf = self.config
        if conf.has(section=section):
            driver = conf.get("driver", section)\
                if conf.has("driver", section) else self.default_driver
            db = conf.get("db", section) if conf.has("db", section) else None
            user = conf.get("user", section) if conf.has("user", section) else None
            pw = conf.get("password", section) if conf.has("password", section) else None
            host = conf.get("host", section) if conf.has("host", section) else None
            port = conf.get("port", section) if conf.has("port", section) else None
            self.db.initialize(driver=driver,
                               db=db,
                               user=user,
                               password=pw,
                               host=host,
                               port=port)
            return True
        else:
            return False

    def config_init_storage(self, section="STORAGE"):  # TODO: obsolete (in component)
        if not self.is_ready("storage"):
            return False
        conf = self.config
        if conf.has(section=section):
            location = conf.get("location", section)\
                if conf.has("location", section) else self.default_root
            compr = conf.get("compression", section) if conf.has("compression", section) else False
            self.storage.initialize(root=location, compressed=compr)
            return True
        else:
            return False

    def is_ready(self, component, raising=False):
        if not hasattr(self, component):
            if raising:
                raise KeyError("App has no component by the name of '{}'.".format(component))
            return False
        if not hasattr(getattr(self, component), "is_valid"):
            if raising:
                raise TypeError("No valid component is set for '{}' in App.".format(component))
            return False
        return getattr(self, component).is_valid()

    def setup_view(self, **kwargs):
        self.view.set(**kwargs)

    def start(self):
        #  TODO: Implement App.start() when all components are finished
        pass


class Component(metaclass=ABCMeta):
    """
    Base class for all components used by App class. It serves both: providing a common
    interface and internal managing functionality.
    """
    def __init__(self):
        self._state_positive = dict()
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
            self._state_positive[member] = value
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
        for member in self._state_positive:
            if self._state_positive[member] != self.__dict__[member]:
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

    @abstractmethod
    def load_conf(self, config):
        pass

    @abstractmethod
    def save_conf(self, config):
        pass

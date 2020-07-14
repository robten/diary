#!/usr/bin/env python3
# coding: utf-8

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine.url import URL
from diary.application import Component
from diary.models import Model


class DbManager(Component):
    def __init__(self):
        super(DbManager, self).__init__()
        self.engine = self.invalid_state("engine", None)
        self.session = self.invalid_state("session", None)
        self.section = "DATABASE"
        self.credentials = dict()

    def initialize(self, driver="sqlite", database=None, username=None, password=None,
                   host=None, port=None):
        self.engine = create_engine(URL(drivername=driver, database=database, host=host, port=port,
                                        username=username, password=password))
        Model.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)()

    def _session_action(self, action, *items):
        actions = ["add", "delete"]
        if action in actions:
            for item in items:
                if isinstance(item, Model):
                    getattr(self.session, action)(item)
                else:
                    raise TypeError("Item of {} can't be appended to a commit.".format(type(item)))
        else:
            raise ValueError("action should be 'add' or 'delete'.")

    @Component.dependent
    def add(self, *items):
        self._session_action("add", *items)

    @Component.dependent
    def read(self, *args, **kwargs):
        return self.session.query(*args, **kwargs)

    @Component.dependent
    def delete(self, *items):
        self._session_action("delete", *items)

    @Component.dependent
    def commit(self):
        self.session.commit()

    @Component.dependent
    def rollback(self):
        self.session.rollback()

    def load_conf(self, config):
        self.credentials["driver"] = config.get("driver", section=self.section)
        self.credentials["database"] = config.get("database", section=self.section)
        if self.credentials["driver"] != "sqlite":
            self.credentials["username"] = config.get("username", section=self.section)
            self.credentials["password"] = config.get("password", section=self.section)
            self.credentials["host"] = config.get("host", section=self.section)
            self.credentials["port"] = config.get("port", section=self.section)
        self.initialize(**self.credentials)

    def save_conf(self, config):
        cr = self.credentials
        config.set("driver", cr["driver"], section=self.section)
        config.set("database", cr["database"], section=self.section)
        if self.credentials["driver"] != "sqlite":
            config.set("username", cr["username"], section=self.section)
            config.set("password", cr["password"], section=self.section)
            config.set("host", cr["host"], section=self.section)
            config.set("port", cr["port"], section=self.section)

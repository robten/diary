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

    def initialize(self, driver="sqlite", db=None, user=None, password=None, host=None, port=None):
        self.engine = create_engine(URL(drivername=driver, database=db, host=host, port=port,
                                        username=user, password=password))
        Model.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)()

    def _session_action(self, action, *items):
        if action == "add":
            for item in items:
                if isinstance(item, Model):
                    self.session.add(item)
                else:
                    raise TypeError("Item of {} can't be appended to a commit.".format(type(item)))
        elif action == "delete":
            for item in items:
                if isinstance(item, Model):
                    self.session.delete(item)
                else:
                    raise TypeError("Item of {} can't be appended to a commit.".format(type(item)))
        else:
            raise ValueError("action should be 'add' or 'delete'.")

    @Component.dependent
    def create(self, *items):
        self._session_action("add", *items)

    @Component.dependent
    def read(self, *args, **kwargs):
        return self.session.query(*args, **kwargs)

    @Component.dependent
    def update(self, *items):
        self._session_action("add", *items)

    @Component.dependent
    def delete(self, *items):
        self._session_action("delete", *items)

    @Component.dependent
    def commit(self):
        self.session.commit()

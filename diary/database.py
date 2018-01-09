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
        self.Session = self.invalid_state("Session", None)
        self._transaction = {"create": list(), "update": list(), "delete": list()}

    def initialize(self, driver="sqlite", db=None, user=None, password=None, host=None, port=None):
        self.engine = create_engine(URL(drivername=driver, database=db, host=host, port=port,
                                        username=user, password=password))
        Model.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def _transaction_add(self, section, *items):
        if section not in self._transaction.keys():
            raise ValueError("Section isn't one of these keys: {}".format(self._transaction.keys()))
        for item in items:
            if isinstance(item, Model):
                if item not in self._transaction[section]:
                    self._transaction[section].append(item)
            else:
                raise TypeError("Item of {} can't be appended to a commit.".format(type(item)))

    def create(self, *items):
        self._transaction_add("create", items)

    @Component.dependent
    def read(self, *args, **kwargs):
        pass  # Implement read with own session

    def update(self, *items):
        self._transaction_add("update", items)

    def delete(self, *items):
        self._transaction_add("delete", items)

    @Component.dependent
    def commit(self):
        pass  # Implement committing _transaction in its own session

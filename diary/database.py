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
        self._transaction = {"create": list(), "update": list(), "delete": list()}

    def initialize(self, driver="sqlite", db=None, user=None, password=None, host=None, port=None):
        self.engine = create_engine(URL(drivername=driver, database=db, host=host, port=port,
                                        username=user, password=password))
        Model.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)()

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
        self._transaction_add("create", *items)

    @Component.dependent
    def read(self, *args, **kwargs):
        pass  # Implement read with own session

    def update(self, *items):
        self._transaction_add("update", *items)

    def delete(self, *items):
        self._transaction_add("delete", *items)

    @Component.dependent
    def commit(self):
        create_pending = len(self._transaction["create"]) > 0
        update_pending = len(self._transaction["update"]) > 0
        delete_pending = len(self._transaction["delete"]) > 0
        if any([create_pending, update_pending, delete_pending]):
            if create_pending:
                for item in self._transaction["create"]:
                    self.session.add(item)
                self._transaction["create"].clear()
            if update_pending:
                for item in self._transaction["update"]:
                    self.session.add(item)
                self._transaction["update"].clear()
            if delete_pending:
                for item in self._transaction["delete"]:
                    self.session.delete(item)
                self._transaction["delete"].clear()
            self.session.commit()
        else:
            return False

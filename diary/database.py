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
        self._session = self.invalid_state("_session", None)

    def initialize(self, driver="sqlite", db=None, user=None, password=None, host=None, port=None):
        self.engine = create_engine(URL(drivername=driver, database=db, host=host, port=port,
                                        username=user, password=password))
        Model.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self._session = Session()

    @Component.dependent
    def add(self, *args):
        if all(isinstance(arg, Model) for arg in args):
            self._session.add_all(args)
        else:
            raise TypeError("Not called with a valid instance(s) of {}.".format(str(Model)))

    @Component.dependent
    def delete(self, item):
        if isinstance(item, Model):
            self._session.delete(item)
        else:
            raise TypeError("Not called with a valid instance of {}.".format(str(Model)))

    @Component.dependent
    def commit(self):
        self._session.commit()

    @Component.dependent
    def rollback(self):
        self._session.rollback()

    @Component.dependent
    def get(self, *args, **kwargs):
        return self._session.query(*args, **kwargs)

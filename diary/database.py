#!/usr/bin/env python3
# coding: utf-8

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine.url import URL
from diary.models import Model


class DbManager:
    def __init__(self, driver="sqlite", db=None, user=None, password=None, host=None, port=None):
        self.engine = create_engine(URL(drivername=driver, database=db, host=host, port=port,
                                        username=user, password=password))
        Model.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self._session = Session()

    def add(self, *args):
        if all(isinstance(arg, Model) for arg in args):
            self._session.add_all(args)
        else:
            raise TypeError("Not only instances of {} where given.".format(str(Model)))

    def commit(self):
        self._session.commit()

    def get(self, *args, **kwargs):
        return self._session.query(*args, **kwargs)

#!/usr/bin/env python3
# coding: utf-8

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base


class DbManager:
    def __init__(self, driver="sqlite", db=None, user=None, password=None, host=None, port=None):
        self.engine = create_engine(URL(drivername=driver, database=db, host=host, port=port,
                                        username=user, password=password))
        self.Session = sessionmaker(bind=self.engine)
        self.Model = declarative_base()
        self._stage = None

    def add(self, *args):
        if not self._stage:
            self._stage = self.Session()
        self._stage.add_all(*args)

    def commit(self):
        pass

    def get(self):
        pass

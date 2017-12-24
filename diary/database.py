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
        self.Model = declarative_base()
        Session = sessionmaker(bind=self.engine)
        self._session = Session()

    def add(self, *args):
        self._session.add_all(*args)

    def commit(self):
        self._session.commit()

    def get(self):
        pass

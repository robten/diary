#!/usr/bin/env python3
# coding: utf-8

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date


Model = declarative_base()


class Entry(Model):
    __tablename__ = "entry"
    id = Column(Integer, primary_key=True)
    title = Column(String(50))
    text = Column(String)  # TODO Use SQL String for a large textfield?
    timestamp = Column(Date)

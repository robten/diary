#!/usr/bin/env python3
# coding: utf-8

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, ForeignKey, Integer, String, Date, Text
from sqlalchemy.orm import relationship


Model = declarative_base()


entry_files = Table("entry_files", Model.metadata,
                    Column("post_id", ForeignKey("entries.id"), primary_key=True),
                    Column("file_id", ForeignKey("files.id"), primary_key=True))


class Entry(Model):
    __tablename__ = "entries"
    id = Column(Integer, primary_key=True)
    title = Column(String(80))
    text = Column(Text)
    timestamp = Column(Date)
    files = relationship("File", secondary=entry_files, back_populates="entries")

    def __repr__(self):
        return "Entry(id={}, title='{}')".format(self.id, self.title)


class File(Model):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True)
    name = Column(String(80))
    subpath = Column(String(120))
    type = Column(String(10))
    timestamp = Column(Date)
    entries = relationship("Entry", secondary=entry_files, back_populates="files")

    def __repr__(self):
        return "File(id={}, name='{}')".format(self.id, self.name)

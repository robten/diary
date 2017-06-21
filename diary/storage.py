#!/usr/bin/env python3
# coding: utf-8

from os import path


class FileManager:
    def __init__(self, db_backend=None, compressed=False, root=None):
        self._db = db_backend
        self._compression = compressed
        if root and path.exists(path.normpath(root)):
            self._root = path.normpath(root)
        else:
            self._root = None

    def set_root(self, root):
        if path.exists(path.normpath(root)):
            self._root = root
        else:
            raise NotADirectoryError()

    def ready(self):
        return self._root is not None

    def exists(self, item):
        raise NotImplementedError()

    def store(self, item,
              name=None, location=None, ftype=None, date=None, hierachy=None):
        pass

    def retrieve(self, item):
        raise NotImplementedError()

    def get_info(self, item):
        raise NotImplementedError()

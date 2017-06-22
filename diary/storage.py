#!/usr/bin/env python3
# coding: utf-8

from os import path


class FileManager:
    def __init__(self, backend=None, compressed=False, root=None):
        self._db = backend
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
        
    def set_backend(self, db):
        self._db = db
        
    def set_compressed(self, state):
        self._compression = state

    def ready(self):
        return self._root is not None

    def exists(self, item):
        pass

    def store(self, item,
              name=None, location=None, ftype=None, date=None, hierachy=None):
        pass

    def retrieve(self, item):
        pass

    def delete(self, item):
        pass

    def get_info(self, item):
        pass

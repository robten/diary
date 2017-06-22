#!/usr/bin/env python3
# coding: utf-8

from os import path


class FileManager:
    def __init__(self, root=None, backend=None, compressed=False):
        self._db = backend
        self._compression = compressed
        if root and path.exists(path.normpath(root)):
            self._root = path.normpath(root)
        else:
            self._root = None

    def set(self, root=None, backend=None, compressed=None):
        if root:
            if path.exists(path.normpath(root)):
                self._root = root
            else:
                raise NotADirectoryError()
        if backend:
            self._db = backend
        if compressed is not None:
            self._compression = compressed

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

#!/usr/bin/env python3
# coding: utf-8

from os import path


class StorageBase:
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

    def store(self, item):
        raise NotImplementedError()

    def retrieve(self, item):
        raise NotImplementedError()

    def get_info(self, item):
        raise NotImplementedError()


class FileManager(StorageBase):
    def __init__(self, *args, **kwargs):
        super(FileManager, self).__init__(*args, **kwargs)

    def store(self, item,
              name=None, location=None, ftype=None, date=None, hierachy=None):
        pass

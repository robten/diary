#!/usr/bin/env python3
# coding: utf-8

from os import path
import shutil


class FileManager:
    def __init__(self, root=None, backend=None, compressed=False):
        self._db = backend
        self._compression = compressed
        if root and path.exists(path.abspath(root)):
            self._root = path.abspath(root)
        else:
            self._root = None

    def set(self, root=None, backend=None, compressed=None):
        if root:
            if path.exists(path.abspath(root)):
                self._root = path.abspath(root)
            else:
                raise NotADirectoryError()
        if backend:
            self._db = backend
        if compressed is not None:
            self._compression = compressed

    def ready(self, raising=False):  # TODO: Get a more elegant state-checking for all components
        if raising and self._root is None:
            raise ValueError("FileManger object is not in a valid state.")
        return self._root is not None

    def exists(self, item):
        self.ready(raising=True)
        return path.isfile(path.join(self._root, item))

    def store(self, src, name=None, ftype=None, date=None, hierarchy=None):
        self.ready(raising=True)
        src_path = path.abspath(src)
        if path.isfile(src_path):
            stored_name = path.basename(src_path) if not name else name
            # TODO: Implement optional storing inside subdirectories (hierarchy)
            if path.exists(path.join(self._root, stored_name)):
                raise FileExistsError("File with the same name is already stored.")
            shutil.copy(src_path, self._root)
            # TODO: Implement optional database storing of meta-data (name, ftype, date, hierarchy)
        else:
            raise ValueError("FileManager.store() should only be called with a path to a file.")

    def retrieve(self, item):
        self.ready(raising=True)

    def delete(self, item):
        self.ready(raising=True)

    def get_info(self, item):
        self.ready(raising=True)

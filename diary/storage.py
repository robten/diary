#!/usr/bin/env python3
# coding: utf-8

import os
import shutil
from diary.application import Component


class FileManager(Component):
    def __init__(self, root=None, backend=None, compressed=False):
        super(FileManager, self).__init__()
        self._db = backend
        self._compression = compressed
        self._root = self.invalid_state("_root", None)
        if root and os.path.exists(os.path.abspath(root)):
            self._root = os.path.abspath(root)

    def set(self, root=None, backend=None, compressed=None):
        if root:
            if os.path.exists(os.path.abspath(root)):
                self._root = os.path.abspath(root)
            else:
                raise NotADirectoryError()
        if backend:
            self._db = backend
        if compressed is not None:
            self._compression = compressed

    @Component.dependent
    def exists(self, item):
        return os.path.isfile(os.path.join(self._root, item))

    @Component.dependent
    def store(self, src, name=None, ftype=None, date=None, hierarchy=None):
        src_path = os.path.abspath(src)
        if os.path.isfile(src_path):
            stored_name = os.path.basename(src_path) if not name else name
            # TODO: Implement optional storing inside subdirectories (hierarchy)
            if os.path.exists(os.path.join(self._root, stored_name)):
                raise FileExistsError("File with the same name is already stored.")
            shutil.copy(src_path, self._root)
            # TODO: Implement optional database storing of meta-data (name, ftype, date, hierarchy)
        else:
            raise ValueError("FileManager.store() should only be called with a path to a file.")

    @Component.dependent
    def retrieve(self, item, target):
        src_path = os.path.join(self._root, item)
        target_path = os.path.abspath(target)
        if os.path.isfile(src_path):
            if os.path.isdir(target_path):
                shutil.copy(src_path, target_path)
            else:
                raise NotADirectoryError("'{}' is not a valid target directory.".format(target))
        else:
            raise FileNotFoundError("'{}' is not in storage or not a valid item.".format(item))

    @Component.dependent
    def delete(self, item):
        target_path = os.path.join(self._root, item)
        if os.path.isfile(target_path):
            os.remove(target_path)
        else:
            raise FileNotFoundError("'{}' is not in storage or not a valid item.".format(item))

    @Component.dependent
    def get_info(self, item):
        # right now there is only an implementation without DB usage
        src_path = os.path.join(self._root, item)
        if os.path.isfile(src_path):
            return {"path": src_path}
        else:
            raise FileNotFoundError("'{}' is not in storage or not a valid item.".format(item))

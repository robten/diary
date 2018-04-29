#!/usr/bin/env python3
# coding: utf-8

from pathlib import Path
import shutil
from diary.application import Component


class FileManager(Component):
    def __init__(self, root=None, backend=None, compressed=False):
        super(FileManager, self).__init__()
        self._db = backend
        self._compression = compressed
        self._root = self.invalid_state("_root", None)
        if any((root, backend, compressed)):
            self.initialize(root, backend, compressed)

    def initialize(self, root=None, backend=None, compressed=None):
        if root and isinstance(root, (Path, str)):
            root_path = Path(root).resolve()
            if not root_path.is_dir():
                raise NotADirectoryError(f"Given root={root_path} is not a directory.")
            self._root = root_path
        elif root:
            raise TypeError(f"root is not of type Path or str, it was {type(root)}.")
        if backend:
            self._db = backend
        if compressed:
            self._compression = compressed

    @Component.dependent
    def has(self, item):
        return (self._root / item).is_file()

    @Component.dependent
    def store(self, src, name=None, ftype=None, date=None, hierarchy=None):
        src_path = Path(src).resolve()
        if src_path.is_file():
            stored_name = src_path.name if not name else name
            # TODO: Implement optional storing inside subdirectories (hierarchy)
            if (self._root / stored_name).is_file():
                raise FileExistsError("File with the same name is already stored.")
            shutil.copy(src_path, self._root)
            # TODO: Implement optional database storing of meta-data (name, ftype, date, hierarchy)
        else:
            raise ValueError("FileManager.store() should only be called with a path to a file.")

    @Component.dependent
    def retrieve(self, item, target):
        src_path = self._root / item
        target_path = Path(target).resolve()
        if src_path.is_file():
            if target_path.is_dir():
                shutil.copy(src_path, target_path)
            else:
                raise NotADirectoryError("'{}' is not a valid target directory.".format(target))
        else:
            raise FileNotFoundError("'{}' is not in storage or not a valid item.".format(item))

    @Component.dependent
    def delete(self, item):
        target_path = self._root / item
        if target_path.is_file():
            shutil.rmtree(target_path)
        else:
            raise FileNotFoundError("'{}' is not in storage or not a valid item.".format(item))

    @Component.dependent
    def get_info(self, item):
        # right now there is only an implementation without DB usage
        src_path = self._root / item
        if src_path.is_file():
            return {"path": str(src_path)}
        else:
            raise FileNotFoundError("'{}' is not in storage or not a valid item.".format(item))

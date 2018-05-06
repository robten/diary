#!/usr/bin/env python3
# coding: utf-8

from pathlib import Path
import shutil
from diary.application import Component


class FileManager(Component):
    def __init__(self, root=None, db=None, table_cls=None):
        super(FileManager, self).__init__()
        self._db = self.invalid_state("_db", None)
        self._table_cls = self.invalid_state("_table_cls", None)
        self._root = self.invalid_state("_root", None)
        if all((root, db, table_cls)):
            self.initialize(root, db, table_cls)

    def initialize(self, root, db, table_cls):
        """
        Sets the valid state of the FileManager
        :param pathlib.Path or str root: Path to file storage location
        :param diary.database.DbManager db: DB used as a backend for metadata
        :param sqlalchemy.ext.declarative.api.DeclarativeMeta table_cls: Class of the table for
        storing file metadata
        """
        if isinstance(root, (Path, str)):
            root_path = Path(root).resolve()
            if not root_path.is_dir():
                raise NotADirectoryError(f"Given root={root_path} is not a directory.")
            self._root = root_path
        else:
            raise TypeError(f"root is not of type Path or str, it was {type(root)}.")
        self._db = db
        self._table_cls = table_cls

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

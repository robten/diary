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
    def store(self, src, name=None, ftype=None, subdir=None):
        src_path = Path(src).resolve()
        subpath = Path(subdir if subdir else ".") / src_path.name
        target_path = self._root / subpath
        if src_path.is_file():
            stored_name = name if name else src_path.stem
            if target_path.is_file():
                raise FileExistsError("File with the same name is already stored.")
            if self._db.read(self._table_cls).filter(self._table_cls.name == stored_name).first():
                raise ValueError("File by that name is already stored in database.")
            shutil.copy(src_path, self._root)
            meta_data = self._table_cls(name=stored_name,
                                        ftype=ftype if ftype else subpath.suffix[1:],
                                        path=str(subpath))
            self._db.add(meta_data)
            self._db.commit()
        else:
            raise ValueError("FileManager.store() should only be called with a path to a file.")

    @Component.dependent
    def retrieve(self, name=None, id=None):
        if name:
            file = self._db.read(self._table_cls).filter(self._table_cls.name == name).first()
        elif id:
            file = self._db.read(self._table_cls).filter(self._table_cls.id == id).first()
        else:
            return None
        path = self._root / file.subpath
        if path.is_file():
            return path
        else:
            raise FileNotFoundError("File in DB but wasn't found in storage location.")

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

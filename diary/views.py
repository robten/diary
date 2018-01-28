#!/usr/bin/env python3
# coding: utf-8


from PyQt5.QtCore import QAbstractTableModel, QModelIndex, Qt, QVariant
from sqlalchemy import inspect


class SqlAlchemyQueryModel(QAbstractTableModel):
    def __init__(self, query, captions=None, parent=None):
        super(SqlAlchemyQueryModel, self).__init__(parent)
        # TODO: handle query.first() == None, when query has no results
        self._fields = inspect(type(query.first())).columns.keys()
        self._captions = []
        if captions:
            if isinstance(captions, list):
                self._captions = captions
            else:
                raise ValueError("parameter column_names should be of type list()")
        self._query = query
        self._data = self._query.all()

    def headerData(self, column, orientation=Qt.Horizontal, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole and column < len(self._fields):
            if column < len(self._captions):
                return QVariant(self._captions[column])
            else:
                return QVariant(self._fields[column])
        return QVariant()

    def data(self, index, role=Qt.DisplayRole):
        pass

    def setData(self, index, value, role=Qt.EditRole):
        pass

    def insertRow(self, row, parent=QModelIndex(), *args, **kwargs):
        pass

    def insertRows(self, row, count, parent=QModelIndex(), *args, **kwargs):
        pass

    def removeRow(self, row, parent=None, *args, **kwargs):
        pass

    def removeRows(self, row, count, parent=None, *args, **kwargs):
        pass

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable

    def columnCount(self, parent=QModelIndex(), *args, **kwargs):
        return len(self._fields)

    def rowCount(self, parent=QModelIndex(), *args, **kwargs):
        return len(self._data)

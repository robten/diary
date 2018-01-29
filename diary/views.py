#!/usr/bin/env python3
# coding: utf-8


from PyQt5.QtCore import QAbstractTableModel, QModelIndex, Qt, QVariant, QDate
from sqlalchemy import inspect
from datetime import date


class SqlAlchemyQueryModel(QAbstractTableModel):
    def __init__(self, query, captions=None, parent=None):
        super(SqlAlchemyQueryModel, self).__init__(parent)
        # TODO: handle query.first() == None, when query has no results
        # TODO: implement field selection through query
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
        if not index.isValid() or not (0 <= index.row() < len(self._data)):
            return QVariant()
        data = self._data[index.row()]
        column = index.column()
        if role == Qt.DisplayRole:
            value = getattr(data, self._fields[column])
            if isinstance(value, date):
                value = QDate(value)
            return QVariant(value)
        return QVariant()

    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid() or not (0 <= index.row() < len(self._data)):
            return False
        data = self._data[index.row()]
        element = value.value()
        if isinstance(element, QDate):
            element = value.value().toPyDate()
        setattr(data, self._fields[index.column()], element)
        self.dataChanged.emit(index, index)
        return True

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable

    def columnCount(self, parent=QModelIndex(), *args, **kwargs):
        return len(self._fields)

    def rowCount(self, parent=QModelIndex(), *args, **kwargs):
        return len(self._data)

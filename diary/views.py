#!/usr/bin/env python3
# coding: utf-8


from PyQt5.QtCore import QAbstractTableModel, QModelIndex, Qt, QVariant


class SqlAlchemyQueryModel(QAbstractTableModel):
    def __init__(self, query, headers, parent=None):
        super(SqlAlchemyQueryModel, self).__init__(parent)
        self._headers = headers
        self._query = query
        self._data = self._query.all()

    def headerData(self, column, orientation=Qt.Horizontal, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self._headers[column])
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
        return len(self._headers)

    def rowCount(self, parent=QModelIndex(), *args, **kwargs):
        return len(self._data)

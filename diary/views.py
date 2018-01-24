#!/usr/bin/env python3
# coding: utf-8


from PyQt5.QtCore import QAbstractTableModel, QModelIndex, Qt


class SqlAlchemyQueryModel(QAbstractTableModel):
    def __init__(self, parent=None):
        super(SqlAlchemyQueryModel, self).__init__(parent)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        pass

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
        pass

    def columnCount(self, parent=QModelIndex(), *args, **kwargs):
        pass

    def rowCount(self, parent=QModelIndex(), *args, **kwargs):
        pass

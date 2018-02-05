#!/usr/bin/env python3
# coding: utf-8


from PyQt5.QtCore import QAbstractTableModel, QModelIndex, Qt, QVariant, QDate
from sqlalchemy import inspect
from datetime import date


class SqlAlchemyQueryModel(QAbstractTableModel):
    def __init__(self, query, parent=None):
        super(SqlAlchemyQueryModel, self).__init__(parent)
        if not type(query).__name__ == "Query":
            raise TypeError("parameter query should be of type sqlalchemy.orm.query.Query")
        self._query = query
        self._data = self._query.all()
        self._fields = list()
        self._header_data = dict()
        self._result_is_collection = False  # query result could be single model class or collection
        self._analyse_data()

    def _analyse_data(self):
        if type(self._data[0]).__name__ == "result":
            self._result_is_collection = True
        else:
            self._result_is_collection = False
        column_count = 0
        for column in self._query.column_descriptions:
            if column["expr"] is column["type"]:
                # column is a model class
                inspector = inspect(column["type"])
                for attr in inspector.columns.keys():
                    definition = {
                        "type": "class_attr",
                        "name": attr,
                        "class": inspector.class_,
                        "class_name": inspector.class_.__name__,
                        "result_position": column_count
                    }
                    self._fields.append(definition)
                for relation in inspector.relationships.keys():
                    definition = {
                        "type": "class_relation",
                        "name": relation,
                        "class": inspector.class_,
                        "class_name": inspector.class_.__name__,
                        "result_position": column_count
                    }
                    self._fields.append(definition)
            elif type(column["expr"]).__name__ == "InstrumentedAttribute":
                # column is a selected Column from a Table
                definition = {
                    "type": "attr",
                    "name": column["name"],
                    "class": column["entity"],
                    "class_name": column["entity"].__name__,
                    "result_position": column_count
                }
                self._fields.append(definition)
            else:
                raise ValueError("parameter query only excepts tables or individual columns")
            column_count += 1

    def _list_relations(self, index):
        column = index.column()
        if self._fields[column]["type"] != "class_relation":
            raise ValueError("Column {} has no relations to display.".format(column))
        position = self._fields[column]["result_position"]
        collection = self._fields[column]["name"]
        row = index.row()
        if self._result_is_collection:
            data = getattr(self._data[row][position], collection)
        else:
            data = getattr(self._data[row], collection)
        if len(data) == 0:  # no relations for this item to display
            return ""
        primay_key = inspect(type(data[0])).primary_key[0].name
        relation_list = list()
        for related_obj in data:
            relation_list.append(str(getattr(related_obj, primay_key)))
        return ", ".join(relation_list)

    def headerData(self, column, orientation=Qt.Horizontal, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole and column < len(self._fields):
            if column in self._header_data:
                if self._header_data[column]["orientation"] == Qt.Horizontal:
                    return self._header_data[column]["caption"]
            return QVariant("{}.{}".format(self._fields[column]["class_name"],
                                           self._fields[column]["name"]))
        return QVariant()

    def setHeaderData(self, column, orientation, caption, role=None):
        self._header_data[column] = {"caption": caption,
                                     "orientation": orientation}

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < len(self._data)):
            return QVariant()
        data = self._data[index.row()]
        column = index.column()
        value = None
        if role == Qt.DisplayRole:
            if self._result_is_collection:
                # handle collections returned by query
                if self._fields[column]["type"] == "class_attr":
                    model_obj = data[self._fields[column]["result_position"]]
                    value = getattr(model_obj, self._fields[column]["name"])
                if self._fields[column]["type"] == "attr":
                    value = data[self._fields[column]["result_position"]]
                if self._fields[column]["type"] == "class_relation":
                    value = self._list_relations(index)
            else:
                # handle single result (only possible, when a single model class was queried for
                if self._fields[column]["type"] == "class_relation":
                    value = self._list_relations(index)
                else:
                    value = getattr(data, self._fields[column]["name"])
            # Checking value or _fields type for individual type representation:
            if isinstance(value, date):
                value = QDate(value)
            return QVariant(value)
        return QVariant()

    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.EditRole:
            if not index.isValid() or not (0 <= index.row() < len(self._data)):
                return False
            data = self._data[index.row()]
            column = index.column()
            element = value  # FIXME: must be bug, because value should be QVariant not str
            if isinstance(element, QDate):  # FIXME: won't work with plain str
                element = value.toPyDate()
            if self._result_is_collection:
                # handle collections returned by query
                if self._fields[column]["type"] == "class_attr":
                    model_obj = data[self._fields[column]["result_position"]]
                    setattr(model_obj, self._fields[column]["name"], element)
                if self._fields[column]["type"] == "attr":
                    # data[self._fields[column]["result_position"]] = element
                    pass  # TODO: Handle editing for single columns (not easy in SqlAlchemy)
                if self._fields[column]["type"] == "class_relation":
                    pass  # TODO: Handle editing of relationships
            else:
                # handle single result (only possible, when a single model class was queried for
                setattr(data, self._fields[column]["name"], element)
            self.dataChanged.emit(index, index, (Qt.EditRole,))
            return True
        else:
            return False

    def flags(self, index):
        column = index.column()
        if self._fields[column]["type"] == "class_attr":
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable
        else:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def columnCount(self, parent=QModelIndex(), *args, **kwargs):
        return len(self._fields)

    def rowCount(self, parent=QModelIndex(), *args, **kwargs):
        return len(self._data)

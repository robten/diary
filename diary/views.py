#!/usr/bin/env python3
# coding: utf-8


from PyQt5.QtCore import QAbstractTableModel, QSortFilterProxyModel, QModelIndex, Qt, QVariant,\
    QDate
from sqlalchemy import inspect
from datetime import date


class SqlAlchemyQueryModel(QAbstractTableModel):
    def __init__(self, query, parent=None):
        super(SqlAlchemyQueryModel, self).__init__(parent)
        if not type(query).__name__ == "Query":
            raise TypeError("parameter query should be of type sqlalchemy.orm.query.Query")
        self._query = query
        self._data = list()
        self._fields = list()
        self._header_data = dict()
        self._result_is_collection = False  # query result could be single model class or collection
        self._v_header_enabled = False  # whether model displays vertical headers (row numbers)
        self.load()

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
        if "relation_key" in self._fields[column]:
            primay_key = self._fields[column]["relation_key"]
        else:
            primay_key = inspect(type(data[0])).primary_key[0].name
        relation_list = list()
        for related_obj in data:
            relation_list.append(str(getattr(related_obj, primay_key)))
        return ", ".join(relation_list)

    def set_relation_display(self, collection, key):
        """
        Method offers to set the key that will be displayed in the list showing the collection
        (relation inside a SqlAlchemy model class). If not set explicitly the list will display
        the primary key of the related model class (see _list_relations()).
        :param str collection: Name of the relation collection in the refering model class
        :param str key: Name of the key in the related model class
        """
        for field in self._fields:
            if field["name"] == collection and field["type"] == "class_relation":
                field["relation_key"] = key
                return
        raise ValueError("Collection '{}' was not found in query or is no 'class_relation'."
                         .format(collection))

    def load(self):
        self._data = self._query.all()
        self._analyse_data()

    def save(self):
        self._query.session.commit()

    def vertical_headers_enabled(self, status=True):
        self._v_header_enabled = status

    def headerData(self, section, orientation=Qt.Horizontal, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if section in self._header_data:
                if self._header_data[section]["orientation"] == Qt.Horizontal:
                    return self._header_data[section]["caption"]
            return QVariant("{}.{}".format(self._fields[section]["class_name"],
                                           self._fields[section]["name"]))
        elif orientation == Qt.Vertical and role == Qt.DisplayRole and self._v_header_enabled:
            return QVariant(int(section) + 1)
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
            self.save()
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


class SortFilterModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super(SortFilterModel, self).__init__(parent)
        self._keep_vheader_order = True

    def keep_vertical_header_order(self, status=True):
        self._keep_vheader_order = status

    def headerData(self, section, orientation=Qt.Horizontal, role=Qt.DisplayRole):
        if self._keep_vheader_order:
            if orientation == Qt.Vertical and role == Qt.DisplayRole:
                return self.sourceModel().headerData(section, orientation, role)
        return super(SortFilterModel, self).headerData(section, orientation, role)

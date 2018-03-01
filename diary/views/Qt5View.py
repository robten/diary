#!/usr/bin/env python3
# coding: utf-8


from PyQt5.QtCore import QAbstractTableModel, QSortFilterProxyModel, QModelIndex, Qt, QDate
from PyQt5.QtWidgets import *
from sqlalchemy import inspect
from datetime import date


class SqlAlchemyQueryModel(QAbstractTableModel):
    def __init__(self, query, parent=None):
        super(SqlAlchemyQueryModel, self).__init__(parent)
        if not type(query).__name__ == "Query":
            raise TypeError("parameter query should be of type sqlalchemy.orm.query.Query")
        self._query = query
        self._data = list()
        self._header_data = dict()
        self._result_is_collection = False  # query result could be single model class or collection
        self._vheader_enabled = False  # whether model displays vertical headers (row numbers)
        self.meta_columns = list()  # Description of all columns in query result
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
                        "column_type": inspector.columns[attr].type,
                        "result_position": column_count
                    }
                    self.meta_columns.append(definition)
                for relation in inspector.relationships.keys():
                    definition = {
                        "type": "class_relation",
                        "name": relation,
                        "class": inspector.class_,
                        "class_name": inspector.class_.__name__,
                        "result_position": column_count
                    }
                    self.meta_columns.append(definition)
            elif type(column["expr"]).__name__ == "InstrumentedAttribute":
                # column is a selected Column from a Table
                definition = {
                    "type": "attr",
                    "name": column["name"],
                    "class": column["entity"],
                    "class_name": column["entity"].__name__,
                    "column_type": column["type"],
                    "result_position": column_count
                }
                self.meta_columns.append(definition)
            else:
                raise ValueError("parameter query only excepts tables or individual columns")
            column_count += 1

    def _list_relations(self, index):
        column = index.column()
        if self.meta_columns[column]["type"] != "class_relation":
            raise ValueError("Column {} has no relations to display.".format(column))
        position = self.meta_columns[column]["result_position"]
        collection = self.meta_columns[column]["name"]
        row = index.row()
        if self._result_is_collection:
            data = getattr(self._data[row][position], collection)
        else:
            data = getattr(self._data[row], collection)
        if len(data) == 0:  # no relations for this item to display
            return ""
        if "relation_key" in self.meta_columns[column]:
            primary_key = self.meta_columns[column]["relation_key"]
        else:
            primary_key = inspect(type(data[0])).primary_key[0].name
        relation_list = list()
        for related_obj in data:
            relation_list.append(str(getattr(related_obj, primary_key)))
        return ", ".join(relation_list)

    def set_relation_display(self, collection, key):
        """
        Method offers to set the key that will be displayed in the list showing the collection
        (relation inside a SqlAlchemy model class). If not set explicitly the list will display
        the primary key of the related model class (see _list_relations()).
        :param str collection: Name of the relation collection in the refering model class
        :param str key: Name of the key in the related model class
        """
        for field in self.meta_columns:
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
        self._vheader_enabled = status

    def headerData(self, section, orientation=Qt.Horizontal, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if section in self._header_data:
                if self._header_data[section]["orientation"] == Qt.Horizontal:
                    return self._header_data[section]["caption"]
            return "{}.{}".format(self.meta_columns[section]["class_name"],
                                  self.meta_columns[section]["name"])
        elif orientation == Qt.Vertical and role == Qt.DisplayRole and self._vheader_enabled:
            return int(section) + 1
        return None

    def setHeaderData(self, column, orientation, caption, role=None):
        self._header_data[column] = {"caption": caption,
                                     "orientation": orientation}

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < len(self._data)):
            return None
        data = self._data[index.row()]
        column = index.column()
        value = None
        if role in (Qt.DisplayRole, Qt.EditRole):
            if self._result_is_collection:
                # handle collections returned by query
                if self.meta_columns[column]["type"] == "class_attr":
                    model_obj = data[self.meta_columns[column]["result_position"]]
                    value = getattr(model_obj, self.meta_columns[column]["name"])
                if self.meta_columns[column]["type"] == "attr":
                    value = data[self.meta_columns[column]["result_position"]]
                if self.meta_columns[column]["type"] == "class_relation":
                    value = self._list_relations(index)
            else:
                # handle single result (only possible, when a single model class was queried for
                if self.meta_columns[column]["type"] == "class_relation":
                    value = self._list_relations(index)
                else:
                    value = getattr(data, self.meta_columns[column]["name"])
            # Checking value or meta_columns type for individual type representation:
            if isinstance(value, date):
                value = QDate(value)
            return value
        return None

    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.EditRole:
            if not index.isValid() or not (0 <= index.row() < len(self._data)):
                return False
            data = self._data[index.row()]
            column = index.column()
            if isinstance(value, QDate):
                value = value.toPyDate()
            if self._result_is_collection:
                # handle collections returned by query
                if self.meta_columns[column]["type"] == "class_attr":
                    model_obj = data[self.meta_columns[column]["result_position"]]
                    setattr(model_obj, self.meta_columns[column]["name"], value)
                if self.meta_columns[column]["type"] == "attr":
                    # data[self.meta_columns[column]["result_position"]] = element
                    pass  # TODO: Handle editing for single columns (not easy in SqlAlchemy)
                if self.meta_columns[column]["type"] == "class_relation":
                    pass  # TODO: Handle editing of relationships
            else:
                # handle single result (only possible, when a single model class was queried for
                setattr(data, self.meta_columns[column]["name"], value)
            self.save()
            self.dataChanged.emit(index, index, (Qt.EditRole,))
            return True
        else:
            return False

    def flags(self, index):
        column = index.column()
        if self.meta_columns[column]["type"] == "class_attr":
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable
        else:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def columnCount(self, parent=QModelIndex(), *args, **kwargs):
        return len(self.meta_columns)

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


class DisplayWidget(QWidget):
    def __init__(self, model, parent=None):
        super(DisplayWidget, self).__init__(parent)
        self.entry_display = QTableView()
        self.title_edit = QLineEdit()
        self.text_edit = QTextEdit()
        self.mapper = QDataWidgetMapper()
        self.setModel(model)
        self.mapper.addMapping(self.title_edit, 1)
        self.mapper.addMapping(self.text_edit, 2)
        title_label = QLabel("&Title:")
        title_label.setBuddy(self.title_edit)
        text_label = QLabel("T&ext:")
        text_label.setBuddy(self.text_edit)

        # Layout
        main_layout = QVBoxLayout(self)
        sub_layout = QGridLayout(self)
        sub_layout.addWidget(title_label, 0, 0)
        sub_layout.addWidget(self.title_edit, 0, 1)
        sub_layout.addWidget(text_label, 1, 0, Qt.AlignTop)
        sub_layout.addWidget(self.text_edit, 1, 1)
        main_layout.addWidget(self.entry_display)
        main_layout.addLayout(sub_layout)
        self.setLayout(main_layout)

        # Connections
        self.entry_display.selectionModel().currentRowChanged.connect(
            self.mapper.setCurrentModelIndex)

    def setModel(self, model):
        self.entry_display.setModel(model)
        self.mapper.setModel(model)

    def model(self):
        return self.entry_display.model()


class DiaryViewer(QMainWindow):
    def __init__(self, parent=None):
        super(DiaryViewer, self).__init__(parent)

        # View
        central_widget = DisplayWidget(self)
        central_widget.entry_display.hideColumn(0)
        central_widget.entry_display.horizontalHeader().setStretchLastSection(True)
        central_widget.entry_display.resizeColumnsToContents()
        self.setCentralWidget(central_widget)
        self.setGeometry(200, 20, 1500, 1000)
        self.setWindowTitle("Diary")
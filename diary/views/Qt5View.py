#!/usr/bin/env python3
# coding: utf-8


from PyQt5.QtCore import QAbstractTableModel, QSortFilterProxyModel, QModelIndex, Qt, QDate,\
    pyqtSlot, QStandardPaths
from PyQt5.QtWidgets import *
from collections import Iterable
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
        self._last_insert = QModelIndex()
        self.meta_columns = list()  # Description of all columns in query result
        self.load()

    def _analyse_data(self):
        if type(self._data[0]).__name__ == "result":
            self._result_is_collection = True
        else:
            self._result_is_collection = False
        for column_count, column in enumerate(self._query.column_descriptions):
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
                        "result_position": column_count,
                        "related_class": getattr(inspector.class_, relation).mapper.class_
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

    def related_table_model(self, collection, key=None, exclude=None):
        """
        Method creates a sub-query for the related table of the collection column-name and
        returns it encapsulated inside a seperate SqlAlchemyQueryModel.
        :param any or Iterable exclude: optional - A single value or a list/tuple of values to be
        excluded.
        :param str key: optional - The key to be used for the value comparison, defaults to primay
        key if not supplied.
        :param str collection: Name of the relation collection in the refering model class
        :return: SqlAlchemyQueryModel
        """
        for field in self.meta_columns:
            if field["name"] == collection and field["type"] == "class_relation":
                primary_key = key if key else inspect(field["class"]).primary_key[0].name
                related_query = self._query.session.query(field["related_class"])
                if exclude:
                    if isinstance(exclude, Iterable):
                        return SqlAlchemyQueryModel(related_query
                                                    .filter(getattr(field["related_class"],
                                                                    primary_key).notin_(exclude)))
                    else:
                        return SqlAlchemyQueryModel(related_query
                                                    .filter(getattr(field["related_class"],
                                                                    primary_key) != exclude))
                return SqlAlchemyQueryModel(related_query)
        raise ValueError("Collection '{}' was not found in query or is no 'class_relation'."
                         .format(collection))

    def load(self):
        self._data = self._query.all()
        self._analyse_data()

    def save(self):
        self._query.session.commit()

    def vertical_headers_enabled(self, status=True):
        self._vheader_enabled = status

    def inserted_index(self):
        return self._last_insert

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
        if role in (Qt.DisplayRole, Qt.EditRole, Qt.UserRole):
            if self._result_is_collection:
                model_obj = data[self.meta_columns[column]["result_position"]]
                # handle collections returned by query
                if self.meta_columns[column]["type"] == "class_attr":
                    value = getattr(model_obj, self.meta_columns[column]["name"])
                if self.meta_columns[column]["type"] == "attr":
                    value = model_obj
                if self.meta_columns[column]["type"] == "class_relation":
                    value = self._list_relations(index) if role == Qt.DisplayRole \
                        else getattr(model_obj, self.meta_columns[column]["name"])
                if role == Qt.UserRole:
                    value = model_obj
            else:
                # handle single result (only possible, when a single model class was queried for
                if self.meta_columns[column]["type"] == "class_relation":
                    value = self._list_relations(index) if role == Qt.DisplayRole \
                        else getattr(data, self.meta_columns[column]["name"])
                else:
                    value = getattr(data, self.meta_columns[column]["name"])
                if role == Qt.UserRole:
                    value = data
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
                model_obj = data[self.meta_columns[column]["result_position"]]
                # handle collections returned by query
                if self.meta_columns[column]["type"] == "class_attr":
                    setattr(model_obj, self.meta_columns[column]["name"], value)
                if self.meta_columns[column]["type"] == "attr":
                    # data[self.meta_columns[column]["result_position"]] = element
                    pass  # TODO: Handle editing for single columns (not easy in SqlAlchemy)
                if self.meta_columns[column]["type"] == "class_relation":
                    setattr(model_obj, self.meta_columns[column]["name"], value)
            else:
                # handle single result (only possible, when a single model class was queried for
                setattr(data, self.meta_columns[column]["name"], value)
            self.save()
            self.dataChanged.emit(index, index, (Qt.EditRole,))
            return True
        else:
            return False

    def insertRows(self, row, count, parent=None, *args, **kwargs):
        if count > 1 or row > self.rowCount():
            return False
        column_types = list()
        for column in self.meta_columns:
            if column["type"] == "class_attr" and column["class"] not in column_types:
                column_types.append(column["class"])
        if 0 < len(column_types) < 2:
            new_row = column_types[0]()
        elif 0 < len(column_types) >= 2:
            new_row = tuple(type_() for type_ in column_types)
        else:
            return False
        self.beginInsertRows(parent, row, row + count - 1)
        self._last_insert = self.index(row, 0)
        if row < self.rowCount():
            self._data.insert(row, new_row)
        elif row == self.rowCount():
            self._data.append(new_row)
        if isinstance(new_row, tuple):
            self._query.session.add_all(new_row)
        else:
            self._query.session.add(new_row)
        self.endInsertRows()
        return True

    def removeRows(self, row, count, parent=None, *args, **kwargs):
        if row < 0 or row > self.rowCount():
            return False
        item = self._data[row]  # Only implemented for single row removal, yet
        self.beginRemoveRows(parent, row, row + count - 1)
        if type(item).__name__ == "result" or isinstance(item, tuple):
            for content in item:
                if content in self._query.session.new:
                    self._query.session.expunge(content)
                else:
                    self._query.session.delete(content)
        else:
            if item in self._query.session.new:
                self._query.session.expunge(item)
            else:
                self._query.session.delete(item)
        self.save()
        self.load()
        self.endRemoveRows()
        return True

    def flags(self, index):
        column = index.column()
        if self.meta_columns[column]["type"] in ("class_attr", "class_relation"):
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable
        else:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def columnCount(self, parent=None, *args, **kwargs):
        return len(self.meta_columns)

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self._data)


class SortFilterModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super(SortFilterModel, self).__init__(parent)
        self._keep_vheader_order = True

    def keep_vertical_header_order(self, status=True):
        self._keep_vheader_order = status

    def inserted_index(self):
        source_index = self.sourceModel().inserted_index()
        return self.mapFromSource(source_index)

    def headerData(self, section, orientation=Qt.Horizontal, role=Qt.DisplayRole):
        if self._keep_vheader_order:
            if orientation == Qt.Vertical and role == Qt.DisplayRole:
                return self.sourceModel().headerData(section, orientation, role)
        return super(SortFilterModel, self).headerData(section, orientation, role)

    def set_relation_display(self, collection, key):
        self.sourceModel().set_relation_display(collection, key)

    def related_table_model(self, *args, **kwargs):
        return self.sourceModel().related_table_model(*args, **kwargs)


class SqlAlchemyCollectionDelegate(QStyledItemDelegate):
    def __init__(self, managed_column, displayed_columns, column_labels=None, parent=None):
        """
        A generic delegate to manage editing collections of SqlAlchemy relations. To be used only
        on a QTableWidget as editor (i.e. used by a QDataWidgetMapper).
        :param managed_column: int, The column of the collection inside the model.
        :param displayed_columns: Iterable, Which fields of the related model should be displayed.
        :param column_labels: Iterable, Optional list of label names for column headers.
        :param parent: QObject
        """
        super(SqlAlchemyCollectionDelegate, self).__init__(parent)
        if not isinstance(displayed_columns, Iterable):
            raise TypeError("parameter displayed_columns should be an iterable.")
        self._target_column = managed_column
        self._source_columns = displayed_columns
        self._labels = column_labels if column_labels else displayed_columns

    def setEditorData(self, editor, index):
        if index.column() == self._target_column:
            collection = index.model().data(index, Qt.EditRole)
            editor.setColumnCount(len(self._source_columns))
            editor.setHorizontalHeaderLabels(self._labels)
            editor.setRowCount(len(collection))
            for row, element in enumerate(collection):
                for column, field in enumerate(self._source_columns):
                    data = getattr(element, field)
                    if isinstance(data, date):
                        data = QDate(data)
                    item = QTableWidgetItem()
                    item.setData(Qt.DisplayRole, data)
                    if column == 0:
                        item.setData(Qt.UserRole, element)
                    editor.setItem(row, column, item)
            editor.setCurrentCell(-1, -1)  # cancel any previous selection
        else:
            super(SqlAlchemyCollectionDelegate, self).setEditorData(editor, index)

    def setModelData(self, editor, model, index):
        if index.column() == self._target_column:
            edited_rows = list()
            for row in range(editor.rowCount()):
                edited_rows.append(editor.item(row, 0).data(Qt.UserRole))
            model.setData(index, edited_rows)
        else:
            super(SqlAlchemyCollectionDelegate, self).setModelData(editor, model, index)


class SqlAlchemySelectDialog(QDialog):
    def __init__(self, model, caption, parent=None):
        super(SqlAlchemySelectDialog, self).__init__(parent)
        self.setWindowTitle(caption)
        self.table = QTableView()
        self.table.setModel(model)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.MultiSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setCurrentIndex(QModelIndex())
        self.selection = list()  # List of selected items from table

        # Buttons
        self.select_button = QPushButton("&Select")
        self.select_button.setEnabled(False)
        self.cancel_button = QPushButton("&Cancel")

        # Layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.select_button)
        button_layout.addWidget(self.cancel_button)
        dialog_layout = QGridLayout()
        dialog_layout.addWidget(self.table, 0, 0)
        dialog_layout.addLayout(button_layout, 1, 0, Qt.AlignRight)
        self.setLayout(dialog_layout)
        self.setMinimumWidth(self.table.size().width())

        # Connection
        self.table.selectionModel().selectionChanged.connect(self.update_status)
        self.select_button.pressed.connect(self.select_items)
        self.cancel_button.pressed.connect(self.reject)

    @pyqtSlot()
    def update_status(self):
        status = True if self.table.selectionModel().hasSelection() else False
        self.select_button.setEnabled(status)
        self.table.setCurrentIndex(QModelIndex())

    @pyqtSlot()
    def select_items(self):
        for index in self.table.selectionModel().selectedRows():
            self.selection.append(self.table.model().data(index, Qt.UserRole))
        self.accept()


class SqlAlchemyAddFileDialog(QDialog):
    def __init__(self, caption, parent=None):
        super(SqlAlchemyAddFileDialog, self).__init__(parent)
        self.setWindowTitle(caption)
        self.name_edit = QLineEdit()
        self.name_edit.setMinimumWidth(300)
        self.meta_data_display = QPlainTextEdit()
        self.meta_data_display.setEnabled(False)
        name_label = QLabel("&Name:")
        name_label.setBuddy(self.name_edit)
        meta_data_label = QLabel("&File Info:")
        meta_data_label.setBuddy(self.meta_data_display)

        # Buttons
        self.new_button = QPushButton("&Open New File")
        self.new_button.setDefault(True)
        self.add_button = QPushButton("&Add")
        self.add_button.setEnabled(False)
        self.cancel_button = QPushButton("&Cancel")

        # Layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.cancel_button)
        dialog_layout = QGridLayout()
        dialog_layout.addWidget(name_label, 0, 0)
        dialog_layout.addWidget(self.name_edit, 0, 1)
        dialog_layout.addWidget(self.new_button, 0, 2)
        dialog_layout.addWidget(meta_data_label, 1, 0)
        dialog_layout.addWidget(self.meta_data_display, 1, 1, 1, 2)
        dialog_layout.addLayout(button_layout, 2, 2, Qt.AlignRight)
        self.setLayout(dialog_layout)

        # Connection
        self.new_button.pressed.connect(self.new_pressed)
        self.cancel_button.pressed.connect(self.reject)

    @pyqtSlot()
    def new_pressed(self):
        start_dir = QStandardPaths.standardLocations(QStandardPaths.HomeLocation)[-1]
        file_dialog = QFileDialog(self)
        file_dialog.setDirectory(start_dir)
        if file_dialog.exec_():
            # TODO: Implement File-adding logic using storage module
            self.add_button.setEnabled(True)

    @pyqtSlot()
    def add_pressed(self):
        self.accept()


class DisplayWidget(QWidget):
    def __init__(self, model, parent=None):
        super(DisplayWidget, self).__init__(parent)
        self._last_index = None
        self._edit_new = False
        self._file_fields = ("name", "subpath", "timestamp")

        # Widgets
        self.entry_display = QTableView()
        self.entry_display.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.entry_display.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.title_edit = QLineEdit()
        self.text_edit = QPlainTextEdit()
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.file_edit = QTableWidget()
        self.file_edit.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        self.file_edit.setMaximumHeight(83)
        self.file_edit.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.file_edit.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.file_edit.setEditTriggers(QAbstractItemView.NoEditTriggers)
        title_label = QLabel("&Title:")
        title_label.setBuddy(self.title_edit)
        text_label = QLabel("T&ext:")
        text_label.setBuddy(self.text_edit)
        date_label = QLabel("&Date:")
        date_label.setBuddy(self.date_edit)
        file_label = QLabel("&Files")
        file_label.setBuddy(self.file_edit)

        # Buttons
        self.add_button = QPushButton("&Add")
        self.remove_button = QPushButton("&Remove")
        self.submit_button = QPushButton("&Submit")
        self.cancel_button = QPushButton("&Cancel")
        self.submit_button.hide()
        self.cancel_button.hide()
        self.fadd_button = QPushButton("Add &File")
        self.fconnect_button = QPushButton("C&onnect File")
        self.fdisconnect_button = QPushButton("&Disconnect File")

        # Mapper &  UI setup
        self.mapper = QDataWidgetMapper()
        self.mapper.setItemDelegate(SqlAlchemyCollectionDelegate(4,
                                                                 self._file_fields,
                                                                 column_labels=("Filename",
                                                                                "Filepath",
                                                                                "Timestamp"),
                                                                 parent=self))
        self.mapper.setSubmitPolicy(QDataWidgetMapper.ManualSubmit)
        self.setModel(model)
        self.enable_mapping()
        self.entry_display.hideColumn(0)
        self.entry_display.hideColumn(2)
        self.entry_display.horizontalHeader().setStretchLastSection(True)
        self.entry_display.setSortingEnabled(True)
        self.entry_display.resizeColumnsToContents()

        # Tab Order
        self.setTabOrder(self.add_button, self.remove_button)
        self.setTabOrder(self.remove_button, self.title_edit)
        self.setTabOrder(self.title_edit, self.date_edit)
        self.setTabOrder(self.date_edit, self.text_edit)
        self.setTabOrder(self.text_edit, self.file_edit)
        self.setTabOrder(self.file_edit, self.submit_button)
        self.setTabOrder(self.submit_button, self.cancel_button)

        # Layout
        main_layout = QVBoxLayout(self)
        sub_layout = QHBoxLayout(self)
        edit_layout = QGridLayout(self)
        button_layout = QVBoxLayout(self)
        fbutton_layout = QVBoxLayout(self)
        fbutton_layout.addWidget(self.fadd_button)
        fbutton_layout.addWidget(self.fconnect_button)
        fbutton_layout.addWidget(self.fdisconnect_button)
        edit_layout.addWidget(title_label, 0, 0)
        edit_layout.addWidget(self.title_edit, 0, 1)
        edit_layout.addWidget(date_label, 0, 2)
        edit_layout.addWidget(self.date_edit, 0, 3)
        edit_layout.addWidget(text_label, 1, 0, Qt.AlignTop)
        edit_layout.addWidget(self.text_edit, 1, 1, 1, 3)
        edit_layout.addWidget(file_label, 2, 0)
        edit_layout.addWidget(self.file_edit, 2, 1, 1, 2)
        edit_layout.addLayout(fbutton_layout, 2, 3, Qt.AlignTop)
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)
        button_layout.addWidget(self.submit_button)
        button_layout.addWidget(self.cancel_button)
        button_layout.setAlignment(Qt.AlignTop)
        sub_layout.addLayout(edit_layout)
        sub_layout.addLayout(button_layout)
        main_layout.addWidget(self.entry_display)
        main_layout.addLayout(sub_layout)
        self.setLayout(main_layout)

        # Connections
        self.entry_display.selectionModel().currentRowChanged.connect(
            self.mapper.setCurrentModelIndex)
        self.title_edit.textEdited.connect(self.start_edit_mode)
        self.text_edit.document().undoAvailable.connect(self.start_edit_mode)
        self.date_edit.editingFinished.connect(self.start_edit_mode)
        self.add_button.pressed.connect(self.add_pressed)
        self.remove_button.pressed.connect(self.remove_pressed)
        self.submit_button.pressed.connect(self.submit_pressed)
        self.cancel_button.pressed.connect(self.cancel_pressed)
        self.fconnect_button.pressed.connect(self.fconnect_pressed)
        self.fdisconnect_button.pressed.connect(self.fdisconnect_pressed)
        self.fadd_button.pressed.connect(self.fadd_pressed)

    def enable_mapping(self):
        self.mapper.addMapping(self.title_edit, 1)
        self.mapper.addMapping(self.text_edit, 2)
        self.mapper.addMapping(self.date_edit, 3)
        self.mapper.addMapping(self.file_edit, 4)
        if self._last_index:
            self.mapper.setCurrentIndex(self._last_index)

    def disable_mapping(self):
        self._last_index = self.mapper.currentIndex()
        self.mapper.clearMapping()
        self.title_edit.clear()
        self.text_edit.clear()

    def setModel(self, model):
        self.entry_display.setModel(model)
        self.mapper.setModel(model)

    def model(self):
        return self.entry_display.model()

    @pyqtSlot()
    def add_pressed(self):
        model = self.model()
        row = self.mapper.currentIndex()
        model.insertRow(row)
        index = model.inserted_index()
        self.entry_display.selectRow(index.row())
        self.mapper.setCurrentModelIndex(index)
        self.title_edit.setFocus()
        self._edit_new = True
        self.start_edit_mode()

    @pyqtSlot()
    def remove_pressed(self):
        selected_row = self.entry_display.selectionModel().selectedRows()
        model = self.model()
        model.removeRow(selected_row[0].row())

    @pyqtSlot()
    def submit_pressed(self):
        self.mapper.submit()
        self.end_edit_mode()

    @pyqtSlot()
    def cancel_pressed(self):
        self.mapper.revert()
        if self._edit_new:
            self.remove_pressed()
            self._edit_new = False
        self.end_edit_mode()

    @pyqtSlot()
    def start_edit_mode(self):
        self.add_button.setDisabled(True)
        self.remove_button.setDisabled(True)
        self.submit_button.show()
        self.cancel_button.show()
        self.entry_display.setDisabled(True)

    @pyqtSlot()
    def end_edit_mode(self):
        self.add_button.setDisabled(False)
        self.remove_button.setDisabled(False)
        self.submit_button.hide()
        self.cancel_button.hide()
        self.entry_display.setDisabled(False)

    @pyqtSlot()
    def fconnect_pressed(self):
        # Model
        sql_model = self.model().related_table_model("files",
                                                     exclude=extract_from_table(self.file_edit,
                                                                                0,
                                                                                "id"))
        sql_model.setHeaderData(1, Qt.Horizontal, "Filename")
        sql_model.setHeaderData(2, Qt.Horizontal, "Path")
        sql_model.setHeaderData(4, Qt.Horizontal, "Date")
        model = SortFilterModel(self)
        model.setSourceModel(sql_model)

        # Dialog setup
        dialog = SqlAlchemySelectDialog(model, "Files to associate this Entry with:")
        dialog.table.hideColumn(0)
        dialog.table.hideColumn(3)
        dialog.table.hideColumn(5)
        dialog.table.setSortingEnabled(True)
        if dialog.exec_():
            existing_rows = self.file_edit.rowCount()
            self.file_edit.setRowCount(existing_rows + len(dialog.selection))
            for row, file in enumerate(dialog.selection, start=existing_rows):
                for column, field in enumerate(self._file_fields):
                    data = getattr(file, field)
                    if isinstance(data, date):
                        data = QDate(data)
                    item = QTableWidgetItem()
                    item.setData(Qt.DisplayRole, data)
                    if column == 0:
                        item.setData(Qt.UserRole, file)
                    self.file_edit.setItem(row, column, item)
            self.date_edit.editingFinished.emit()  # To trigger start_edit_mode()

    @pyqtSlot()
    def fdisconnect_pressed(self):
        if self.file_edit.selectionModel().hasSelection():
            row = self.file_edit.currentRow()
            self.file_edit.removeRow(row)
            self.file_edit.setCurrentCell(-1, -1)
            self.date_edit.editingFinished.emit()  # To trigger start_edit_mode()

    @pyqtSlot()
    def fadd_pressed(self):
        dialog = SqlAlchemyAddFileDialog("Add a new File")
        if dialog.exec_():
            pass



class DiaryViewer(QMainWindow):
    def __init__(self, parent=None):
        super(DiaryViewer, self).__init__(parent)

        # View
        central_widget = DisplayWidget(self)
        self.setCentralWidget(central_widget)
        self.setGeometry(200, 20, 1500, 1000)
        self.setWindowTitle("Diary")


def extract_from_table(table_widget, column, key=None):
    """
    A generator for contents of a column and key (optional) for each row in a QTableWidget.
    :param QTableWidget table_widget: The source table to extract from
    :param int column: The column to extract from
    :param str key: Optional - The key of a SqlAlchemy table stored under Qt.UserRole
    """
    if not isinstance(table_widget, QTableWidget):
        raise TypeError("'table_widget' must be of Type QTableWidget but instead was of type {}"
                        .format(type(table_widget)))
    if key:
        for row in range(table_widget.rowCount()):
            data = table_widget.item(row, column).data(Qt.UserRole)
            yield getattr(data, key)
    else:
        for row in range(table_widget.rowCount()):
            yield table_widget.item(row, column).data(Qt.DisplayRole)

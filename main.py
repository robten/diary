#!/usr/bin/env python3
# coding: utf-8

from diary.application import App
from diary.configmanager import INImanager
from diary.database import DbManager
from diary.storage import FileManager
from diary.views import TerminalView


app = App(conf_component=INImanager(),
          db_component=DbManager(),
          storage_component=FileManager(),
          view_component=TerminalView())
app.load_conf("./config/config.ini")
if not app.is_ready("database"):
    app.setup_storage(location="./config/storage/")
if not app.is_ready("storage"):
    app.setup_database(file="./config/database.db")
app.start()

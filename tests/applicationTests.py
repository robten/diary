#!/usr/bin/env python3
# coding: utf-8

import unittest
from unittest.mock import MagicMock
from diary.application import App


class AppTest(unittest.TestCase):

    def setUp(self):
        self.app = App(conf_component=MagicMock(),
                       db_component=MagicMock(),
                       storage_component=MagicMock(),
                       view_component=MagicMock())

    def test_load_conf(self):
        test_path = "./testdir/test.conf"
        self.app.load_conf(test_path)
        self.app._conf.set_source.assert_called_once_with(path=test_path)
        self.app._conf.load.assert_called_once_with()

    def test_is_ready(self):
        self.app._view.ready.return_value = True
        self.assertTrue(self.app.is_ready("view"), "is_ready() should return True")
        self.app._view.ready.assert_called_once_with()

    def test_is_ready_with_wrong_component(self):
        self.app._view.ready.return_value = True
        with self.assertRaises(KeyError, msg="is_ready() should reraise KeyError"):
            self.app.is_ready("wrong_view")
        self.app._view.ready.assert_called_once_with()

    def test_setup_database_for_mysql(self):
        test_kwargs = {"user": "tester",
                       "password": "testy",
                       "url": "localhost",
                       "db": "test"}
        self.app.setup_database(**test_kwargs)
        self.app._db.set.assert_called_with(**test_kwargs)

    def test_setup_database_for_sqlite(self):
        test_kwargs = {"file": "./config/test.db"}
        self.app.setup_database(**test_kwargs)
        self.app._db.set.assert_called_with(**test_kwargs)

    def test_file_storage(self):
        test_kwargs = {"location": "./config/storage"}
        self.app.setup_storage(**test_kwargs)
        self.app._storage.set.assert_called_with(**test_kwargs)


if __name__ == "__main__":
    unittest.main()

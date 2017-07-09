#!/usr/bin/env python3
# coding: utf-8

import unittest
from unittest.mock import MagicMock
from diary.application import App, Component


class AppTest(unittest.TestCase):

    def setUp(self):
        self.app = App(conf_component=MagicMock(),
                       db_component=MagicMock(),
                       storage_component=MagicMock(),
                       view_component=MagicMock())

    def test_load_conf_with_path(self):
        test_path = "./testdir/test.conf"
        self.app.load_conf(test_path)
        self.app._conf.set_source.assert_called_with(path=test_path)
        self.app._conf.load.assert_called_with()

    def test_load_conf_unset_without_path(self):
        """
        Test if load_conf() without path argument raises the correct error when the
        corresponding components ready() returns False (hence component is not set yet).
        """
        self.app._conf.ready.return_value = False
        with self.assertRaises(FileNotFoundError,
                               msg="there should be no file set hence non found"):
            self.app.load_conf()

    def test_load_conf_set_without_path(self):
        """
        Test if load_conf() without path argument calles only the components load()
        without extra call to its set_source().
        """
        self.app._conf.ready.return_value = True
        self.app.load_conf()
        self.app._conf.set_source.assert_not_called()
        self.app._conf.load.assert_called_with()

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

    def test_setup_storage_for_file(self):
        test_kwargs = {"location": "./config/storage"}
        self.app.setup_storage(**test_kwargs)
        self.app._storage.set.assert_called_with(**test_kwargs)

    def test_setup_view(self):
        test_kwargs = {"geometry": (800,600)}
        self.app.setup_view(**test_kwargs)
        self.app._view.set.assert_called_with(**test_kwargs)


class ComponentTest(unittest.TestCase):

    class TestClass(Component):
        def __init__(self):
            super(ComponentTest.TestClass, self).__init__()

    def test_is_valid_for_invalid_state(self):
        test_obj = self.TestClass()
        test_obj.test = test_obj.invalid_state("test", None)
        self.assertEqual(test_obj.is_valid(), False, msg="test_obj should be in an invalid state")

    def test_is_valid_for_invalid_state_made_valid(self):
        test_obj = self.TestClass()
        test_obj.test = test_obj.invalid_state("test", None)
        test_obj.test = "content that makes sense"
        self.assertEqual(test_obj.is_valid(), True, msg="test_obj should be in a valid state now")


if __name__ == "__main__":
    unittest.main()

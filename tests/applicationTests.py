#!/usr/bin/env python3
# coding: utf-8

import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path
from diary.application import App, Component


class AppTest(unittest.TestCase):

    def setUp(self):
        self.app = App("Test App",
                       config=MagicMock(),
                       db=MagicMock(),
                       storage=MagicMock(),
                       view=MagicMock())

    def test_load_config_with_path(self):
        with patch.object(Path, "is_file") as mock_is_file:
            mock_is_file.return_value = True
            test_path = "./testdir/test.conf"
            self.app.config.is_valid.return_value = True
            self.app.load_config(test_path)
            self.app.config.initialize.assert_called_with(path=Path(test_path))
            self.app.config.load.assert_called_with()

    def test_load_config_set_without_path(self):
        """
        Test if load_config() without path argument calles only the components load()
        without extra call to its initialize().
        """
        with patch.object(Path, "is_file") as mock_is_file:
            mock_is_file.return_value = True
            self.app.config.is_valid.return_value = True
            self.app.load_config()
            self.app.config.initialize.assert_called_with(path=self.app.default_config)
            self.app.config.load.assert_called_with()

    def test_is_ready(self):
        self.app.view.is_valid.return_value = True
        self.assertTrue(self.app.is_ready("view"), "is_ready() should return True")
        self.app.view.is_valid.assert_called_once_with()

    def test_is_ready_with_wrong_component(self):
        self.app.view.is_valid.return_value = True
        self.assertFalse(self.app.is_ready("wrong_view"),
                         msg="is_ready() should return False, if component isn't found")

    def test_is_ready_with_wrong_component_raising(self):
        self.app.view.is_valid.return_value = True
        with self.assertRaises(KeyError,
                               msg="is_ready() should reraise KeyError, if raising is set"):
            self.app.is_ready("wrong_view", raising=True)

    # def test_setup_database_for_mysql(self):
    #     test_kwargs = {"user": "tester",
    #                    "password": "testy",
    #                    "url": "localhost",
    #                    "db": "test"}
    #     self.app.setup_database(**test_kwargs)
    #     self.app.db.set.assert_called_with(**test_kwargs)
    #
    # def test_setup_database_for_sqlite(self):
    #     test_kwargs = {"file": "./config/test.db"}
    #     self.app.setup_database(**test_kwargs)
    #     self.app.db.set.assert_called_with(**test_kwargs)
    #
    # def test_setup_storage_for_file(self):
    #     test_kwargs = {"location": "./config/storage"}
    #     self.app.setup_storage(**test_kwargs)
    #     self.app.storage.set.assert_called_with(**test_kwargs)
    #
    # def test_setup_view(self):
    #     test_kwargs = {"geometry": (800,600)}
    #     self.app.setup_view(**test_kwargs)
    #     self.app.view.set.assert_called_with(**test_kwargs)


class ComponentTest(unittest.TestCase):

    class TestClass(Component):
        def __init__(self):
            super(ComponentTest.TestClass, self).__init__()

        @Component.dependent
        def test_method(self):
            pass

    def test_is_valid_for_invalid_state(self):
        test_obj = self.TestClass()
        test_obj.test = test_obj.invalid_state("test", None)
        self.assertEqual(test_obj.is_valid(), False, msg="test_obj should be in an invalid state")

    def test_is_valid_for_invalid_state_made_valid(self):
        test_obj = self.TestClass()
        test_obj.test = test_obj.invalid_state("test", None)
        test_obj.test = "content that makes sense"
        self.assertEqual(test_obj.is_valid(), True, msg="test_obj should be in a valid state now")

    def test_is_valid_for_valid_state(self):
        test_obj = self.TestClass()
        test_obj.test = test_obj.valid_state("test", "normal state")
        self.assertEqual(test_obj.is_valid(), True,
                         msg="test_obj should already be in a valid state")

    def test_is_valid_for_valid_state_made_invalid(self):
        test_obj = self.TestClass()
        test_obj.test = test_obj.valid_state("test", "normal state")
        test_obj.test = "wrong state"
        self.assertEqual(test_obj.is_valid(), False,
                         msg="test_obj should be in an invalid state")

    def test_alternate_valid_states_for_valid_state(self):
        test_obj = self.TestClass()
        test_obj.test1 = test_obj.valid_state("test1", 1, alternate=True)
        test_obj.test2 = test_obj.valid_state("test2", 2, alternate=True)
        test_obj.test1 = 5
        self.assertEqual(test_obj.is_valid(), True,
                         msg="test_obj should be in a valid alternate state")

    def test_alternate_valid_states_for_invalid_state(self):
        test_obj = self.TestClass()
        test_obj.test1 = test_obj.valid_state("test1", 1, alternate=True)
        test_obj.test2 = test_obj.valid_state("test2", 2, alternate=True)
        test_obj.test1 = 5
        test_obj.test2 = 10
        self.assertEqual(test_obj.is_valid(), False,
                         msg="test_obj should be in an invalid alternate state")

    def test_alternate_invalid_states_for_valid_state(self):
        test_obj = self.TestClass()
        test_obj.test1 = test_obj.invalid_state("test1", None, alternate=True)
        test_obj.test2 = test_obj.invalid_state("test2", None, alternate=True)
        test_obj.test1 = 5
        self.assertEqual(test_obj.is_valid(), True,
                         msg="test_obj should be in a valid alternate state")

    def test_alternate_invalid_states_for_invalid_state(self):
        test_obj = self.TestClass()
        test_obj.test1 = test_obj.invalid_state("test1", None, alternate=True)
        test_obj.test2 = test_obj.invalid_state("test2", None, alternate=True)
        self.assertEqual(test_obj.is_valid(), False,
                         msg="test_obj should be in an invalid alternate state")

    def test_dependent_decorator(self):
        test_obj = self.TestClass()
        test_obj.test = test_obj.invalid_state("test", None)
        with self.assertRaises(ValueError,
                               msg="calling decorated method in invalid state should raise error"):
            test_obj.test_method()


if __name__ == "__main__":
    unittest.main()

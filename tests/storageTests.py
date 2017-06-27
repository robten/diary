#!/usr/bin/env python3
# coding: utf-8

import unittest
from unittest.mock import MagicMock, patch, call
from os import path
from diary.storage import FileManager


class FileManagerTest(unittest.TestCase):
    def test_ready_unset_init(self):
        test = FileManager()
        self.assertFalse(test.ready(),
                         msg="for an unset FileManager ready() should return False")

    def test_ready_set_init(self):
        test = FileManager(root="./")
        self.assertTrue(test.ready(),
                        msg="for a set FileManager ready() should return True")

    def test_set_root(self):
        test_root = "./"
        test = FileManager()
        self.assertIsNone(test._root,
                          msg="unset _root should be None")
        test.set(root=test_root)
        self.assertEqual(test._root, path.abspath(test_root),
                         msg="after set_root() member should match input")

    def test_set_root_fail_nonexisitent(self):
        test_root = "./nonexistent"
        test = FileManager()
        self.assertIsNone(test._root,
                          msg="unset _root should be None")
        with self.assertRaises(NotADirectoryError,
                               msg="set_root() didn't raise Error if root path is invalid"):
            test.set(root=test_root)

    def test_exists_nonexistent_item(self):
        test_root = "./testroot"
        test_file = "testfile"
        test_path = path.abspath(path.join(test_root, test_file))
        isfile_mock = MagicMock(return_value=False)
        exists_mock = MagicMock(return_value=True)
        with patch("os.path.isfile", isfile_mock), patch("os.path.exists", exists_mock):
            test = FileManager(root=test_root)
            self.assertIsNotNone(test.exists(test_file),
                                 msg="exists() should return only True or False")
            self.assertFalse(test.exists(test_file),
                             msg="exists() should return False, when test_file was not created yet")
        isfile_mock.assert_called_with(test_path)

    def test_exists_existent_item(self):
        test_root = "./testroot"
        test_file = "testfile"
        test_path = path.abspath(path.join(test_root, test_file))
        isfile_mock = MagicMock(return_value=True)
        exists_mock = MagicMock(return_value=True)
        with patch("os.path.isfile", isfile_mock), patch("os.path.exists", exists_mock):
            test = FileManager(root=test_root)
            self.assertTrue(test.exists(test_file),
                            msg="exists() should return True, when test_file was created")
        isfile_mock.assert_called_with(test_path)

    def test_exists_invalid_state(self):
        test = FileManager()
        with self.assertRaises(ValueError,
                               msg="ValueError missing when exists() is called in invalid state"):
            test.exists("~/")
        with self.assertRaises(ValueError,
                               msg="ValueError missing when store() is called in invalid state"):
            test.store("test")
        with self.assertRaises(ValueError,
                               msg="ValueError missing when retrieve() is called in invalid state"):
            test.retrieve("test")
        with self.assertRaises(ValueError,
                               msg="ValueError missing when delete() is called in invalid state"):
            test.delete("test")
        with self.assertRaises(ValueError,
                               msg="ValueError missing when get_info() is called in invalid state"):
            test.get_info("test")

    def test_store_new_file(self):
        test_root = "./testroot"
        test_file = "storage_test.py"
        source_location = "/tmp"
        source_path = path.abspath(path.join(source_location, test_file))
        target_path = path.abspath(path.join(test_root, test_file))

        def exists_side_effect(mocked_path):
            if mocked_path == path.abspath(test_root):
                return True
            if mocked_path == target_path:
                return False

        exists_mock = MagicMock(side_effect=exists_side_effect)
        exists_expected_calls = [call(path.abspath(test_root)),
                                 call(target_path)]
        isfile_mock = MagicMock(return_value=True)
        copy_mock = MagicMock()
        with patch("shutil.copy", copy_mock),\
             patch("os.path.exists", exists_mock),\
             patch("os.path.isfile", isfile_mock):
                test = FileManager(root=test_root)
                test.store(source_path)
        exists_mock.assert_has_calls(exists_expected_calls)
        isfile_mock.assert_called_with(source_path)
        copy_mock.assert_called_with(source_path, path.abspath(test_root))


if __name__ == "__main__":
    unittest.main()

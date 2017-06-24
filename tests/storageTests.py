#!/usr/bin/env python3
# coding: utf-8

import unittest
from unittest.mock import MagicMock, patch
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


if __name__ == "__main__":
    unittest.main()

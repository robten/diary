#!/usr/bin/env python3
# coding: utf-8

import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path
from diary.storage import FileManager


class FileManagerTest(unittest.TestCase):
    def test_initialize_root(self):
        test_root = "./"
        db_mock = MagicMock()
        table_mock = MagicMock()
        test = FileManager()
        self.assertIsNone(test._root,
                          msg="unset _root should be None")
        test.initialize(test_root, db_mock, table_mock)
        self.assertEqual(test._root, Path(test_root).resolve(),
                         msg="after set_root() member should match input")

    def test_initialize_root_fail_nonexisitent(self):
        test_root = "./nonexistent"
        db_mock = MagicMock()
        table_mock = MagicMock()
        test = FileManager()
        self.assertIsNone(test._root,
                          msg="unset _root should be None")
        with self.assertRaises(NotADirectoryError,
                               msg="set_root() didn't raise Error if root path is invalid"):
            test.initialize(test_root, db_mock, table_mock)

    def test_has_nonexistent_item(self):
        test_root = "./testroot"
        db_mock = MagicMock()
        table_mock = MagicMock()
        test_file = "testfile"
        isfile_mock = MagicMock(return_value=False)
        isdir_mock = MagicMock(return_value=True)
        with patch("pathlib.Path.is_file", isfile_mock),\
             patch("pathlib.Path.is_dir", isdir_mock):
            test = FileManager(test_root, db_mock, table_mock)
            self.assertFalse(test.has(test_file),
                             msg="exists() should return False, when test_file was not created yet")

    def test_has_existent_item(self):
        test_root = "./testroot"
        db_mock = MagicMock()
        table_mock = MagicMock()
        test_file = "testfile"
        isfile_mock = MagicMock(return_value=True)
        isdir_mock = MagicMock(return_value=True)
        with patch("pathlib.Path.is_file", isfile_mock),\
             patch("pathlib.Path.is_dir", isdir_mock):
            test = FileManager(test_root, db_mock, table_mock)
            self.assertTrue(test.has(test_file),
                            msg="exists() should return True, when test_file was created")

    def test_has_invalid_state(self):
        test = FileManager()
        with self.assertRaises(ValueError,
                               msg="ValueError missing when exists() is called in invalid state"):
            test.has("~/")
        with self.assertRaises(ValueError,
                               msg="ValueError missing when store() is called in invalid state"):
            test.store("test")
        with self.assertRaises(ValueError,
                               msg="ValueError missing when retrieve() is called in invalid state"):
            test.retrieve("test", "/nonedir")
        with self.assertRaises(ValueError,
                               msg="ValueError missing when delete() is called in invalid state"):
            test.delete("test")
        with self.assertRaises(ValueError,
                               msg="ValueError missing when get_info() is called in invalid state"):
            test.get_info("test")

    def test_store_new_file(self):
        test_root = "./testroot"
        db_mock = MagicMock()
        table_mock = MagicMock()
        test_file = "storage_test.py"
        source_location = "/tmp"
        source_path = Path(source_location).resolve() / test_file
        target_path = Path(test_root).resolve()
        isfile_mock = MagicMock(side_effect=[True, False])
        isdir_mock = MagicMock(return_value=True)
        copy_mock = MagicMock()
        with patch("shutil.copy", copy_mock),\
             patch("pathlib.Path.is_dir", isdir_mock),\
             patch("pathlib.Path.is_file", isfile_mock):
                test = FileManager(test_root, db_mock, table_mock)
                test.store(source_location + "/" + test_file)
        isfile_mock.assert_called_with()
        copy_mock.assert_called_with(source_path, target_path)

    def test_retrieve(self):
        test_root = "./testroot"
        db_mock = MagicMock()
        table_mock = MagicMock()
        test_file = "storage_test.py"
        target_dir = "/tmp/testdir"
        src_path = Path(test_root).resolve() / test_file
        target_path = Path(target_dir).resolve()
        isdir_mock = MagicMock(return_value=True)
        isfile_mock = MagicMock(return_value=True)
        copy_mock = MagicMock()
        with patch("pathlib.Path.is_dir", isdir_mock),\
             patch("pathlib.Path.is_file", isfile_mock),\
             patch("shutil.copy", copy_mock):
                test = FileManager(test_root, db_mock, table_mock)
                test.retrieve(test_file, target_dir)
        copy_mock.assert_called_with(src_path, target_path)

    def test_delete(self):
        test_root = "./testroot"
        db_mock = MagicMock()
        table_mock = MagicMock()
        test_file = "storage_test.py"
        src_path = Path(test_root).resolve() / test_file
        isfile_mock = MagicMock(return_value=True)
        isdir_mock = MagicMock(return_value=True)
        remove_mock = MagicMock()
        with patch("pathlib.Path.is_file", isfile_mock),\
             patch("pathlib.Path.is_dir", isdir_mock),\
             patch("shutil.rmtree", remove_mock):
                test = FileManager(test_root, db_mock, table_mock)
                test.delete(test_file)
        remove_mock.assert_called_with(src_path)

    def test_get_info(self):
        test_root = "./testroot"
        db_mock = MagicMock()
        table_mock = MagicMock()
        test_file = "storage_test.py"
        src_path = Path(test_root).resolve() / test_file
        isfile_mock = MagicMock(return_value=True)
        isdir_mock = MagicMock(return_value=True)
        with patch("pathlib.Path.is_file", isfile_mock),\
             patch("pathlib.Path.is_dir", isdir_mock):
            test = FileManager(test_root, db_mock, table_mock)
            result_obj = test.get_info(test_file)
        self.assertIn("path", result_obj,
                      msg="Returned Obj should have a key or attribute named 'path'.")
        self.assertEqual(result_obj["path"], str(src_path),
                         msg="Returned Obj's 'path' should match '{}'.".format(src_path))


if __name__ == "__main__":
    unittest.main()

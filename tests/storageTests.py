#!/usr/bin/env python3
# coding: utf-8

import unittest
import tempfile
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

    def test_initialize_root_with_not_pathlike(self):
        test_root = 1234
        db_mock = MagicMock()
        table_mock = MagicMock()
        test = FileManager()
        with self.assertRaises(TypeError,
                               msg="giving a wrong type to initialize() root should raise error"):
            test.initialize(test_root, db_mock,table_mock)

    def test_has_nonexistent_item(self):
        test_root = "./testroot"
        db_mock = MagicMock()
        table_mock = MagicMock()
        filter_mock = MagicMock()
        file_mock = MagicMock()
        query_mock = MagicMock()
        query_mock.first.return_value = file_mock
        filter_mock.filter.return_value = query_mock
        db_mock.read.return_value = filter_mock
        isfile_mock = MagicMock(return_value=False)
        isdir_mock = MagicMock(return_value=True)
        test_name = "storage test"
        test_file = "storage_test.py"
        file_mock.id = 1
        file_mock.name = test_name
        file_mock.subpath = test_file
        file_mock.type = Path(test_file).suffix[1:]
        file_mock.timestamp = "2018-05-21"
        file_mock.entries = []
        with patch("pathlib.Path.is_file", isfile_mock),\
             patch("pathlib.Path.is_dir", isdir_mock):
            test = FileManager(test_root, db_mock, table_mock)
            self.assertFalse(test.has(test_name),
                             msg="has() should return False, when test_file is in db but not on fs")

    def test_has_nonexistent_item_in_db(self):
        test_root = "./testroot"
        db_mock = MagicMock()
        table_mock = MagicMock()
        filter_mock = MagicMock()
        query_mock = MagicMock()
        query_mock.first.return_value = None
        filter_mock.filter.return_value = query_mock
        db_mock.read.return_value = filter_mock
        isfile_mock = MagicMock(return_value=True)
        isdir_mock = MagicMock(return_value=True)
        test_name = "storage test"
        with patch("pathlib.Path.is_file", isfile_mock),\
             patch("pathlib.Path.is_dir", isdir_mock):
            test = FileManager(test_root, db_mock, table_mock)
            self.assertFalse(test.has(test_name),
                             msg="has() should return False, when test_name is not in db")

    def test_has_existent_item(self):
        test_root = "./testroot"
        db_mock = MagicMock()
        table_mock = MagicMock()
        filter_mock = MagicMock()
        file_mock = MagicMock()
        query_mock = MagicMock()
        query_mock.first.return_value = file_mock
        filter_mock.filter.return_value = query_mock
        db_mock.read.return_value = filter_mock
        isfile_mock = MagicMock(return_value=True)
        isdir_mock = MagicMock(return_value=True)
        test_name = "storage test"
        test_file = "storage_test.py"
        file_mock.id = 1
        file_mock.name = test_name
        file_mock.subpath = test_file
        file_mock.type = Path(test_file).suffix[1:]
        file_mock.timestamp = "2018-05-21"
        file_mock.entries = []
        with patch("pathlib.Path.is_file", isfile_mock),\
             patch("pathlib.Path.is_dir", isdir_mock):
            test = FileManager(test_root, db_mock, table_mock)
            self.assertTrue(test.has(test_name),
                            msg="has() should return True, when test_name is in db and fs")

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
        test_root = "./"
        db_mock = MagicMock()
        filter_mock = MagicMock()
        query_mock = MagicMock()
        query_mock.first.return_value = None
        filter_mock.filter.return_value = query_mock
        db_mock.read.return_value = filter_mock
        table_mock = MagicMock()
        test_file = "storage_test.py"
        test_kwargs ={"name": "testfile"}
        source_location = "/tmp"
        source_path = Path(source_location).resolve() / test_file
        target_path = Path(test_root).resolve()
        isfile_mock = MagicMock(side_effect=[True, False])
        copy_mock = MagicMock()
        with patch("shutil.copy", copy_mock),\
             patch("pathlib.Path.is_file", isfile_mock):
                test = FileManager(test_root, db_mock, table_mock)
                test.store(source_location + "/" + test_file, **test_kwargs)
        isfile_mock.assert_called_with()
        copy_mock.assert_called_with(source_path, target_path)
        table_mock.assert_called_with(name="testfile",
                                      ftype="py",
                                      path=test_file)
        db_mock.add.assert_called()
        db_mock.commit.assert_called()

    def test_retrieve(self):
        test_root = "./testroot"
        db_mock = MagicMock()
        filter_mock = MagicMock()
        query_mock = MagicMock()
        file_mock = MagicMock()
        query_mock.first.return_value = file_mock
        filter_mock.filter.return_value = query_mock
        db_mock.read.return_value = filter_mock
        table_mock = MagicMock()
        test_name = "storage test"
        test_file = "storage_test.py"
        file_mock.id = 1
        file_mock.name = test_name
        file_mock.subpath = test_file
        file_mock.type = Path(test_file).suffix[1:]
        file_mock.timestamp = "2018-05-21"
        file_mock.entries = []
        src_path = Path(test_root).resolve() / test_file
        isfile_mock = MagicMock(return_value=True)
        isdir_mock = MagicMock(return_value=True)
        with patch("pathlib.Path.is_file", isfile_mock),\
             patch("pathlib.Path.is_dir", isdir_mock):
                test = FileManager(test_root, db_mock, table_mock)
                result_name = test.retrieve(name=test_name)
                result_id = test.retrieve(id=1)
                self.assertEqual(result_name, src_path)
                self.assertEqual(result_id, src_path)

    def test_delete(self):
        test_root = "./testroot"
        db_mock = MagicMock()
        filter_mock = MagicMock()
        query_mock = MagicMock()
        file_mock = MagicMock()
        query_mock.first.return_value = file_mock
        filter_mock.filter.return_value = query_mock
        db_mock.read.return_value = filter_mock
        table_mock = MagicMock()
        test_name = "storage test"
        test_file = "storage_test.py"
        file_mock.id = 1
        file_mock.name = test_name
        file_mock.subpath = test_file
        file_mock.type = Path(test_file).suffix[1:]
        file_mock.timestamp = "2018-05-21"
        file_mock.entries = []
        src_path = Path(test_root).resolve() / test_file
        isfile_mock = MagicMock(return_value=True)
        isdir_mock = MagicMock(return_value=True)
        unlink_mock = MagicMock()
        cleanup_mock = MagicMock()
        with patch("pathlib.Path.is_file", isfile_mock),\
             patch("pathlib.Path.is_dir", isdir_mock),\
             patch("pathlib.Path.unlink", unlink_mock),\
             patch("diary.storage.FileManager._cleanup", cleanup_mock):
                test = FileManager(test_root, db_mock, table_mock)
                test.delete(name=test_file)
        unlink_mock.assert_called()
        cleanup_mock.assert_called_with(src_path.parent)

    def test_get_info(self):
        test_root = "./testroot"
        db_mock = MagicMock()
        filter_mock = MagicMock()
        query_mock = MagicMock()
        file_mock = MagicMock()
        query_mock.first.return_value = file_mock
        filter_mock.filter.return_value = query_mock
        db_mock.read.return_value = filter_mock
        table_mock = MagicMock()
        test_name = "storage test"
        test_file = "storage_test.py"
        file_mock.id = 1
        file_mock.name = test_name
        file_mock.subpath = test_file
        file_mock.type = Path(test_file).suffix[1:]
        file_mock.timestamp = "2018-05-21"
        file_mock.entries = []
        isdir_mock = MagicMock(return_value=True)
        with patch("pathlib.Path.is_dir", isdir_mock):
            test = FileManager(test_root, db_mock, table_mock)
            result_obj = test.get_info(name=test_name)
        self.assertEqual(result_obj.subpath, test_file,
                         msg="Returned Obj's 'subpath' should match '{}'.".format(test_file))

    def test__cleanup(self):
        test_root = "./"
        db_mock = MagicMock()
        table_mock = MagicMock()
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve()
            test_hierachy = root / "test1" / "test2" / "test3"
            test_hierachy.mkdir(parents=True, exist_ok=True)
            test_file = test_hierachy.parent / "testfile.txt"
            test_file.touch()
            tester = FileManager(test_root, db_mock, table_mock)
            tester._cleanup(root)
            self.assertTrue(test_hierachy.parent.exists())
            self.assertFalse(test_hierachy.exists())


if __name__ == "__main__":
    unittest.main()

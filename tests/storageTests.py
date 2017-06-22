#!/usr/bin/env python3
# coding: utf-8

import unittest
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
        test_root = path.normpath("./")
        test = FileManager()
        self.assertIsNone(test._root,
                          msg="unset _root should be None")
        test.set(root=test_root)
        self.assertEqual(test._root, test_root,
                         msg="after set_root() member should match input")

    def test_set_root_fail_nonexisitent(self):
        test_root = path.normpath("./nonexistent")
        test = FileManager()
        self.assertIsNone(test._root,
                          msg="unset _root should be None")
        with self.assertRaises(NotADirectoryError,
                               msg="set_root() didn't raise Error if root path is invalid"):
            test.set(root=test_root)


if __name__ == "__main__":
    unittest.main()

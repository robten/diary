#!/usr/bin/env python3
# coding: utf-8

import unittest
from diary.database import DbManager
from diary.models import Entry


class TestDbManager(unittest.TestCase):

    def setUp(self):
        self.db = DbManager()
        self.db.initialize()

    def test_transaction_add(self):
        test1 = Entry(title="test1", text="test text1")
        test2 = Entry(title="test2", text="test text2")
        test3 = Entry(title="test3", text="test text3")
        test4 = Entry(title="test4", text="test text4")
        self.db._transaction_add("create", test1, test2)
        self.db._transaction_add("update", test3)
        self.db._transaction_add("delete", test4)
        self.assertIn(test1, self.db._transaction["create"])
        self.assertIn(test2, self.db._transaction["create"])
        self.assertIn(test3, self.db._transaction["update"])
        self.assertIn(test4, self.db._transaction["delete"])

    def test_transaction_add_no_double_entry(self):
        test1 = Entry(title="test1", text="test text1")
        test2 = Entry(title="test2", text="test text2")
        self.db._transaction_add("create", test1, test2)
        self.db._transaction_add("create", test1)
        self.assertListEqual([test1, test2], self.db._transaction["create"])

    def test_transaction_add_invalid_type(self):
        test1 = Entry(title="test1", text="test text1")
        test2 = "dummy"
        with self.assertRaises(TypeError, msg="Invalid  item type should raise TypeError."):
            self.db._transaction_add("create", test1, test2)

    def test_transaction_add_invalid_section(self):
        test1 = Entry(title="test1", text="test text1")
        test2 = Entry(title="test2", text="test text2")
        with self.assertRaises(ValueError, msg="Invalid tag should raise ValueError."):
            self.db._transaction_add("wrong", test1, test2)


if __name__ == '__main__':
    unittest.main()

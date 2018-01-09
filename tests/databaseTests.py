#!/usr/bin/env python3
# coding: utf-8

import unittest
from unittest.mock import MagicMock
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

    def test_commit_cleanup(self):
        self.db.session = MagicMock()
        test1 = Entry(title="test1", text="test text1")
        test2 = Entry(title="test2", text="test text2")
        test3 = Entry(title="test3", text="test text3")
        self.db.create(test1)
        self.db.update(test2)
        self.db.delete(test3)
        self.db.commit()
        self.assertListEqual([], self.db._transaction["create"])
        self.assertListEqual([], self.db._transaction["update"])
        self.assertListEqual([], self.db._transaction["delete"])


class TestDbManagerIntegration(unittest.TestCase):

    def setUp(self):
        self.db = DbManager()
        self.db.initialize()

    def test_commit(self):
        test1 = Entry(title="test1", text="test text1")
        test2 = Entry(title="test2", text="test text2")
        self.db.create(test1, test2)
        self.db.commit()
        self.assertIsNotNone(test1.id)
        self.assertIsNotNone(test2.id)
        test1.title = "diverent title"
        self.db.update(test1)
        self.db.delete(test2)
        self.db.commit()


if __name__ == '__main__':
    unittest.main()

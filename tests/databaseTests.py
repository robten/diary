#!/usr/bin/env python3
# coding: utf-8

import unittest
from diary.database import DbManager
from diary.models import Entry


class TestDbManager(unittest.TestCase):

    def setUp(self):
        self.db = DbManager()
        self.db.initialize()

    def test_session_action(self):
        test1 = Entry(title="test1", text="test text1")
        test2 = Entry(title="test2", text="test text2")
        test3 = Entry(title="test3", text="test text3")
        self.db._session_action("add", test1, test2)
        self.db._session_action("add", test3)
        self.assertIn(test1, self.db.session)
        self.assertIn(test2, self.db.session)
        self.assertIn(test3, self.db.session)

    def test_session_action_invalid_type(self):
        test1 = Entry(title="test1", text="test text1")
        test2 = "dummy"
        with self.assertRaises(TypeError, msg="Invalid item type should raise TypeError."):
            self.db._session_action("add", test1, test2)

    def test_session_action_invalid_action(self):
        test1 = Entry(title="test1", text="test text1")
        test2 = Entry(title="test2", text="test text2")
        with self.assertRaises(ValueError, msg="Invalid action tag should raise ValueError."):
            self.db._session_action("wrong", test1, test2)


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
        self.assertFalse(test2 in self.db.session)


if __name__ == '__main__':
    unittest.main()

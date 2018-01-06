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

    def test_add_wrong_type(self):
        """
        Test if add() raises an exception when a wrong parameter-type is given.
        """
        test_entry1 = Entry(title="test", text="test item")
        test_entry2 = "not important"
        with self.assertRaises(TypeError,
                               msg="Should raise TypeError, when no registered model was given"):
            self.db.add(test_entry1, test_entry2)

    def test_add_correct_type(self):
        """
        Test if add() pushes given correct Model-types to the internal _session..
        """
        self.db._session = MagicMock()
        test_entry1 = Entry(title="test1", text="test item")
        test_entry2 = Entry(title="test2", text="test item")
        self.db.add(test_entry1, test_entry2)
        self.db._session.add_all.assert_called_with((test_entry1, test_entry2))

    def test_commit(self):
        self.db._session = MagicMock()
        self.db.commit()
        self.db._session.commit.assert_called_with()

    def test_get(self):
        """
        Test querying the database.
        """
        self.db._session = MagicMock()
        self.db._session.query.return_value(MagicMock())
        self.db.get(Entry).all()
        self.db._session.query.assert_called_with(Entry)

    def test_rollback(self):
        self.db._session = MagicMock()
        self.db.rollback()
        self.db._session.rollback.assert_called_with()

    def test_delete_wrong_type(self):
        wrong_entry = "text only"
        with self.assertRaises(TypeError,
                               msg="Should raise TypeError, when no registered model was given"):
            self.db.delete(wrong_entry)

    def test_delete_correct_type(self):
        self.db._session = MagicMock()
        test_entry = Entry(title="testing", text="test item")
        self.db.delete(test_entry)
        self.db._session.delete.assert_called_with(test_entry)


if __name__ == '__main__':
    unittest.main()

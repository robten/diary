#!/usr/bin/env python3
# coding: utf-8

import unittest
from unittest.mock import MagicMock
from diary.database import DbManager
from diary.models import Entry


class TestDbManager(unittest.TestCase):

    def setUp(self):
        self.db = DbManager()
        self.db._session = MagicMock()

    def test_add(self):
        """
        Test if add() pushes the given parameters to the internaly used db session.
        """
        test_entry1 = "not important"
        test_entry2 = "not important"
        self.db.add(test_entry1, test_entry2)
        self.db._session.add_all.assert_called_with(test_entry1, test_entry2)

    def test_commit(self):
        self.db.commit()
        self.db._session.commit.assert_called_with()

    def test_get(self):
        """
        Test querying the database.
        """
        self.db._session.query.return_value(MagicMock())
        self.db.get(Entry).all()
        self.db._session.query.assert_called_with(Entry)


if __name__ == '__main__':
    unittest.main()

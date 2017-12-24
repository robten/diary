#!/usr/bin/env python3
# coding: utf-8

import unittest
from unittest.mock import MagicMock
from diary.database import DbManager


class TestDbManager(unittest.TestCase):

    def test_add(self):
        """
        Test if add() pushes the given parameters to the internaly used db session.
        """
        manager = DbManager()
        manager.Session = MagicMock()
        test_entry1 = "not important"
        test_entry2 = "not important"
        manager.add(test_entry1, test_entry2)
        manager._session.add_all.assert_called_with(test_entry1, test_entry2)


if __name__ == '__main__':
    unittest.main()

#!/usr/bin/env python3
# coding: utf-8

import unittest
from unittest.mock import MagicMock
from diary.application import App


class AppTest(unittest.TestCase):

    def setUp(self):
        self.app = App(conf_component=MagicMock(),
                       db_component=MagicMock(),
                       storage_component=MagicMock(),
                       view_component=MagicMock())

    def test_load_conf(self):
        test_path = "./testdir/test.conf"
        self.app.load_conf(test_path)
        Dummy.Conf.set_source.assert_called_once_with(path=test_path)
        Dummy.Conf.load.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()

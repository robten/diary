#!/usr/bin/env python3
# coding: utf-8

import unittest
from diary.application import App


class AppTest(unittest.TestCase):

    def setUp(self):
        self.app = App(name="Test")

    def test_instance_is_singelton(self):
        app2 = App()

        self.assertIs(self.app, app2, "App is not createt as a singleton.")


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
# coding: utf-8

import unittest
from application import App


class AppTest(unittest.TestCase):

    def test_instance_is_singelton(self):
        app1 = App(name="Test")
        app2 = App()

        self.assertIs(app1, app2, "App is not createt as a singleton.")


if __name__ == "__main__":
    unittest.main()

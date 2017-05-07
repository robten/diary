#!/usr/bin/env python3
# coding: utf-8

import unittest
from application import App


class AppTest(unittest.TestCase):

    def setUp(self):
        self.app = App(name="Test")

    def test_instance_is_singelton(self):
        app2 = App()

        self.assertIs(self.app, app2, "App is not createt as a singleton.")

    def test_set_get_app_entry(self):
        input_value = "Testing"
        self.app.set("Test", input_value)
        output_value = self.app.get("Test")

        self.assertEqual(input_value, output_value, "set() and get(): input and output don't match")


if __name__ == "__main__":
    unittest.main()

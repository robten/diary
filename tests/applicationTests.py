#!/usr/bin/env python3
# coding: utf-8

import unittest
from application import App


class AppTest(unittest.TestCase):

    def test_instance_is_singelton(self):

        app1 = App(name="Test")
        app2 = App()

        self.assertIs(app1, app2, "App is not createt as a singleton.")

    def test_set_get_conf_entry(self):

        app = App(name="Test")
        input_value = "Testing"
        app.set_conf("Test", input_value)
        output_value = app.get_conf("Test")

        self.assertEqual(input_value, output_value, "Input added to conf does not match output.")


if __name__ == "__main__":
    unittest.main()

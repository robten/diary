#!/usr/bin/env python3
# coding: utf-8

import unittest
import configparser
from configmanager import INImanager


class TestINImanager(unittest.TestCase):

    def test_get_key_no_found_failure(self):
        """
        Test for exspected failure when a non existing key is demanded through get()
        """
        conf_manager = INImanager()
        self.assertRaises(configparser.NoOptionError, conf_manager.get, "NonExistent")

    def test_set_get_key(self):
        conf_manger = INImanager()
        input_value = "Testing"
        conf_manger.set("Test", input_value)
        output_value = conf_manger.get("Test")

        self.assertEqual(input_value, output_value, "set() and get(): input and output don't match")

    def test_load_file_no_found_failure(self):
        conf_manager = INImanager()
        self.assertRaises(FileNotFoundError, conf_manager.load)

    def test_save_file_no_found_failure(self):
        conf_manager = INImanager()
        self.assertRaises(FileNotFoundError, conf_manager.save)

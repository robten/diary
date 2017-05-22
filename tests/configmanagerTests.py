#!/usr/bin/env python3
# coding: utf-8

import unittest
import configparser
import json
import tempfile
from configmanager import INImanager, JSONmanager, ManagerBase


class TestManagerBase(unittest.TestCase):

    def test_get_key_no_found_failure(self):
        """
        Test for expected failure when a non existing key is demanded through get().
        """
        conf_manager = ManagerBase()
        self.assertRaises(KeyError, conf_manager.get, "NonExistent")

    def test_set_get_key(self):
        """
        Test if set() and get() ar producing the same content for the same key.
        """
        conf_manger = ManagerBase()
        input_value = "Testing"
        conf_manger.set("Test", input_value)
        output_value = conf_manger.get("Test")
        self.assertEqual(input_value, output_value, "set() and get(): input and output don't match")


class TestINImanager(unittest.TestCase):

    def test_load_file_not_found_failure(self):
        """
        Test for expected failure when load() is called without setting a source path or file.
        """
        conf_manager = INImanager()
        self.assertRaises(FileNotFoundError, conf_manager.load)

    def test_save_file_not_found_failure(self):
        """
        Test for expected failure when save() is called without setting a source path or file.
        """
        conf_manager = INImanager()
        self.assertRaises(FileNotFoundError, conf_manager.save)

    def test_load_file(self):
        """
        Functional test loading a config from a temporary file and checking input and output.
        """
        test_config = configparser.ConfigParser()
        test_config.set("DEFAULT", "test_content", "42")
        with tempfile.TemporaryFile(mode="w+t") as test_file:
            test_config.write(test_file)
            test_file.seek(0)
            result_config = INImanager(file=test_file)
            result_config.load()
            self.assertEqual(test_config.get("DEFAULT", "test_content"),
                             result_config.get("test_content"),
                             "Loaded config didn't match saved config.")

    def test_save_file(self):
        """
        Functional test saving a config to a temporary file and checking input and output.
        """
        result_config = configparser.ConfigParser()
        with tempfile.TemporaryFile(mode="w+t") as test_file:
            test_config = INImanager(file=test_file)
            test_config.set("test_content", "42")
            test_config.save()
            test_file.seek(0)
            result_config.read_file(test_file)
            self.assertEqual(test_config.get("test_content"),
                             result_config.get("DEFAULT", "test_content"),
                             "Saved config didn't match loaded config.")


class TestJSONmanager(unittest.TestCase):

    def test_load_file_not_found_failure(self):
        """
        Test for expected failure when load() is called without setting a source path or file.
        """
        conf_manager = JSONmanager()
        self.assertRaises(FileNotFoundError, conf_manager.load)

    def test_save_file_not_found_failure(self):
        """
        Test for expected failure when save() is called without setting a source path or file.
        """
        conf_manager = JSONmanager()
        self.assertRaises(FileNotFoundError, conf_manager.save)

    def test_load_file(self):
        """
        Functional test loading a config from a temporary file and checking input and output.
        """
        test_config = {"DEFAULT": {"test_content": "42"}}
        with tempfile.TemporaryFile(mode="w+t") as test_file:
            json.dump(test_config, test_file)
            test_file.seek(0)
            result_config = JSONmanager(file=test_file)
            result_config.load()
            self.assertEqual(test_config["DEFAULT"]["test_content"],
                             result_config.get("test_content"),
                             "Loaded config didn't match saved config.")

    def test_save_file(self):
        """
        Functional test saving a config to a temporary file and checking input and output.
        """
        with tempfile.TemporaryFile(mode="w+t") as test_file:
            test_config = JSONmanager(file=test_file)
            test_config.set("test_content", "42")
            test_config.save()
            test_file.seek(0)
            result_config = json.load(test_file)
            self.assertEqual(test_config.get("test_content"),
                             result_config["DEFAULT"]["test_content"],
                             "Saved config didn't match loaded config.")
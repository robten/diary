#!/usr/bin/env python3
# coding=utf-8

import unittest
from utilities import MetaOrderedAttributes


class UtilitiesTest(unittest.TestCase):

    def test_MetaOrderedAttributes_preserve_order(self):
        """
        Testing if the base class correctly reads in the attributes defined
        in class Test.
        (Should be done through the metaclass MetaOrderedAttributes)
        """

        class Test(metaclass=MetaOrderedAttributes):
            attribute1 = "attribute1"
            attribute2 = "attribute2"

            def attribute_method(self):
                pass

        test_attributes = ("attribute1", "attribute2", "attribute_method")

        self.assertEqual(test_attributes, Test._fields,
                         "Order of attributes doesn't match.")


if __name__ == "__main__":
    unittest.main()

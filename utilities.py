#!/usr/bin/env python3
# coding: utf-8

from collections import OrderedDict


class MetaSingleton(type):
    """
    Metaclass that ensures the class can only be instantiated once. Implementing
    the Singelton design pattern.
    """
    def __init__(cls, *args, **kwargs):
        cls._instance = None
        super().__init__(*args, **kwargs)

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__call__(*args, **kwargs)
            return cls._instance
        else:
            return cls._instance


class MetaOrderedAttributes(type):
    """
    Metaclass that ensures the class preserves the order of its attributes
    """

    @classmethod
    def __prepare__(mcs, name, bases, **kwargs):
        """
        Switches the Dict for an OrderedDict to preserve the order
        of class attributes.
        :rtype : OrderedDict
        """
        return OrderedDict()

    def __new__(mcs, name, bases, namespace, **kwargs):
        result = type.__new__(mcs, name, bases, dict(namespace))
        fields = [attr for attr in namespace.keys() if not attr.endswith("__")]

        result._fields = tuple(fields)
        return result


def print_entry(entry):
    print("This Entry contains:")
    for attr, value in entry.__dict__.items():
        print(" {}: {}".format(attr, value))


def print_attr(obj):
    """
    Prints all attributes of the class and its instance in a readable format.
    Callables (methods) are not listet.
    :type obj: object, that should be inspected and printed
    """
    print("Class Attributes:")
    for key, value in obj.__class__.__dict__.items():
        if not key.endswith("__") and not callable(value):
            print("{}: {}".format(key, value))

    print("Instance Attributes:")
    for key, value in obj.__dict__.items():
        if not key.endswith("__") and not callable(value):
            print("{}: {}".format(key, value))
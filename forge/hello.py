#!/usr/bin/python

"""@package hello
Documentation about this package
"""

# import <modules>

__copyright__ = "Copyright 2015 The Paladin's Forge"
__license__ = "The MIT License"
__author__ = "The Paladin's Forge"
__email__ = "ThePaladinsForge@gmail.com"
__version__ = "1.0"
__status__ = "Development"  # Prototype, Development, Production


class Hello(object):
    """ class documentation """

    def __init__(self):
        pass

    def __repr__(self):
        return str()

    @staticmethod
    def hello():
        print "Hello world!"


if __name__ == '__main__':
    Hello.hello()

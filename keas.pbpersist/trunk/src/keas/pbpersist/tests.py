##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

import time
import unittest

from zope.testing import doctest
from persistent import Persistent
from keas.pbstate.meta import ProtobufState
from keas.pbstate.testclasses_pb2 import ContactPB


class PContact(Persistent):
    """A simple ProtobufState class for testing"""
    __metaclass__ = ProtobufState
    protobuf_type = ContactPB

    def __init__(self):
        self.create_time = 1


class Adder(Persistent):
    """A Persistent class with a __getnewargs__ method for testing"""

    def __new__(cls, constant):
        res = super(cls, Adder).__new__(cls)
        res.constant = constant
        return res

    def add(self, n):
        return self.constant + n

    def __getnewargs__(self):
        return (self.constant,)


class PContactWithGetNewArgs(PContact):
    """A ProtobufState persistent class with a __getnewargs__ method.

    This is here to demonstrate that such a class won't currently work,
    because storing the result of __getnewargs__() would require pickling.
    """
    def __getnewargs__(self):
        return ()


def test_suite():
    return unittest.TestSuite([
        doctest.DocFileSuite(
            'README.txt',
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
    ])

if __name__ == '__main__':
    unittest.main()

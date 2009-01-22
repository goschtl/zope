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
    __metaclass__ = ProtobufState
    protobuf_type = ContactPB

    def __init__(self):
        self.create_time = 1


def test_suite():
    return unittest.TestSuite([
        doctest.DocFileSuite(
            'README.txt',
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
    ])

if __name__ == '__main__':
    unittest.main()

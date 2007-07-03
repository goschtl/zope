##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Observable tests

$Id$
"""
__docformat__ = "reStructuredText"

import unittest
from persistent import Persistent
from zope.interface import implements
from zope.app.annotation.interfaces import IAttributeAnnotatable
from zope.app.testing.functional import FunctionalDocFileSuite

def chickenModified(event):
     print "buh-PAH! I was modified."

class Chicken(Persistent):
     implements(IAttributeAnnotatable)

def test_suite():
    globs = {'Chicken': Chicken,
             'chickenModified': chickenModified}
    return unittest.TestSuite((
	FunctionalDocFileSuite('observable.txt', globs=globs),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

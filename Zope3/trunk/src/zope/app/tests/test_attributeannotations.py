##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""

Revision information:
$Id: test_attributeannotations.py,v 1.3 2003/05/01 19:35:37 faassen Exp $
"""

from unittest import TestCase, main, makeSuite
from zope.testing.cleanup import CleanUp # Base class w registry cleanup
from zope.app.tests.annotations import Annotations
from zope.app.attributeannotations import AttributeAnnotations
from zope.app.interfaces.annotation import IAttributeAnnotatable

class Dummy:
    __implements__ = IAttributeAnnotatable

class Test(CleanUp, Annotations, TestCase):

    def setUp(self):
        self.annotations = AttributeAnnotations(Dummy())
        #super(Test,self).setUp()
        Annotations.setUp(self)
        CleanUp.setUp(self)


def test_suite():
    return makeSuite(Test)

if __name__=='__main__':
    main(defaultTest='test_suite')

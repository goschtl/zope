##############################################################################
#
# Copyright (c) 2006-2007 Lovely Systems and Contributors.
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
"""
$Id$
"""
__docformat__ = "reStructuredText"

import unittest
from zope.app.testing import functional
from zope.app.testing import setup
from z3c.configurator import configurator
from z3c.testing import layer

def appSetUp(app):
    configurator.configure(app, {},
                           names=["lovely.relation.o2oStringTypeRelations"])

layer.defineLayer('LovelyRelationsDemoLayer', zcml='ftesting.zcml',
                  appSetUp=appSetUp,
                  clean=True)


def test_suite():
    fsuites = (
        functional.FunctionalDocFileSuite('README.txt')
    )
    for fsuite in fsuites:
        fsuite.layer=LovelyRelationsDemoLayer
    return unittest.TestSuite(fsuites)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

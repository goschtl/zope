##############################################################################
#
# Copyright (c) Zope Corporation. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Visible Source
# License, Version 1.0 (ZVSL).  A copy of the ZVSL should accompany this
# distribution.
#
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

from zope.testing import doctest
import os
import unittest
import zope.app.testing.functional

class Test(zope.app.testing.functional.ZCMLLayer):

    def __init__(self):
        pass # Circumvent inherited constructior :)

    allow_teardown = False
    config_file = os.path.join(os.path.dirname(__file__), 'tests.zcml')
    __name__ = config_file
    product_config = None

    def __call__(self, *args, **kw):
        test = doctest.DocFileSuite(*args, **kw)
        test.layer = self
        return test

def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('widgets.txt',
                             setUp=zope.app.testing.placelesssetup.setUp,
                             tearDown=zope.app.testing.placelesssetup.tearDown,
                             ),
        Test()('application.txt', 'session.txt', 'form.txt'),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')


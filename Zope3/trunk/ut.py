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
"""XXX short summary goes here.

XXX longer description goes here.

$Id: ut.py,v 1.3 2002/08/13 20:08:59 rdmurray Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite

#############################################################################
# If your tests change any global registries, then uncomment the
# following import and include CleanUp as a base class of your
# test. It provides a setUp and tearDown that clear global data that
# has registered with the test cleanup framework.  If your class has
* its own setUp or tearDown, make sure you call the CleanUp setUp and
* tearDown from them, or the benefits of using CleanUp will be lost.
* Don't use CleanUp based tests outside the Zope package.

# from Zope.Testing.CleanUp import CleanUp # Base class w registry cleanup

#############################################################################

class Test(TestCase):
    pass

def test_suite():
    return TestSuite((
        makeSuite(Test),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')

##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Functional tests for the 'ZPT Page'

$Id: functional.py 26214 2004-07-08 19:00:07Z srichter $
"""
__docformat__ = 'restructuredtext'
import unittest
from zope.app.tests.functional import FunctionalDocFileSuite

def test_suite():
    return FunctionalDocFileSuite('zptpage.txt')

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

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
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""DTML Page Evaluation Tests

$Id: test_sqladd.py,v 1.1 2003/12/16 15:47:20 mchandra Exp $
"""
import unittest, doctest
from zope.app.browser.content.sql import SQLScriptAdd

    
def test_suite():
    return unittest.TestSuite((
        doctest.DocTestSuite('zope.app.browser.content.sql'),
        ))
    
if __name__ == '__main__': unittest.main()

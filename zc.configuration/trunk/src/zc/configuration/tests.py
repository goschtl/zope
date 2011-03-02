##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
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
import os, re, doctest
from zope.testing import setupstack, renormalizing

def setUp(test):
    setupstack.setUpDirectory(test)

def test_suite():
    return doctest.DocFileSuite(
            'README.txt', setUp=setUp, tearDown=setupstack.tearDown,
            checker=renormalizing.RENormalizing([
                (re.compile('include [^\n]+zc.configuration[\S+]'),
                 'include /zc.configuration\2'),
                (re.compile(r'\\'), '/'),
                ])
            )



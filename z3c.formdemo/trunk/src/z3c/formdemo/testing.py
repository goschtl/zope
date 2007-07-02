##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
import tempfile
import lxml.etree
import os
from zope.rdb import gadflyda
from zope.app.testing.functional import ZCMLLayer

def setUp(test):
    gadfly_dir = tempfile.mkdtemp()
    os.mkdir(os.path.join(gadfly_dir, 'msg'))
    gadflyda.setGadflyRoot(gadfly_dir)

def printElement(browser, xpath, multiple=False, serialize=True):
    result = [serialize and lxml.etree.tounicode(elem) or elem
              for elem in browser.etree.xpath(xpath)]
    if not multiple:
        print result[0]
        return
    for elem in result:
        print elem

FormDemoLayer = ZCMLLayer(
    os.path.join(os.path.split(__file__)[0], 'ftesting.zcml'),
    __name__, 'FormDemoLayer', allow_teardown=True)

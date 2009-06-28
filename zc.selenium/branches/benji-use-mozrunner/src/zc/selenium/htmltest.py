##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
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
"""A simple hookup to make a simple Selenium HTML Table test available for the
Zope-generated test suite.

$Id$
"""
__docformat__ = "reStructuredText"
import os
import zope.interface
from zope.app.component import hooks
from zc.selenium.pytest import ISeleniumTest
from zc.selenium.resource import ResourceBase
from z3c.zrtresource import processor, replace


class HTMLTableSeleniumTest(ResourceBase):
    zope.interface.implementsOnly(ISeleniumTest)

    filename = None

    def __call__(self):
        data = open(self.filename, 'r').read()
        p = processor.ZRTProcessor(data, commands={'replace': replace.Replace})
        self.request.response.setHeader('Content-type', 'text/html')
        return p.process(hooks.getSite(), self.request)

    GET = __call__

def createSeleniumTest(filename):
    return type(os.path.split(filename)[-1],
                (HTMLTableSeleniumTest,), {'filename': filename})


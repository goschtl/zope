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
"""
$Id:$
"""
__docformat__ = "reStructuredText"

import datetime
import zope.interface
import zope.component
from zope.dublincore.interfaces import IZopeDublinCore
from zope.security import checker
from zope.app.testing import setup

import z3c.table.value

class DublinCoreAdapterStub(object):
    """Dublin core adapter stub."""

    zope.interface.implements(IZopeDublinCore)
    zope.component.adapts(zope.interface.Interface)

    __Security_checker__ = checker.Checker(
        {"created": "zope.Public",
         "modified": "zope.Public",
         "title": "zope.Public",
         },
        {"title": "zope.app.dublincore.change"})

    def __init__(self, context):
        pass
    title = 'faux title'
    size = 1024
    created = datetime.datetime(2001, 1, 1, 1, 1, 1)
    modified = datetime.datetime(2002, 2, 2, 2, 2, 2)


def setUpAdapters():
    zope.component.provideAdapter(z3c.table.value.ValuesForContainer)
    zope.component.provideAdapter(z3c.table.value.ValuesForSequence)


def setUp(test):
    test.globs['root'] = setup.placefulSetUp(True)
    zope.component.provideAdapter(DublinCoreAdapterStub)
    setUpAdapters()


def tearDown(test):
    setup.placefulTearDown()

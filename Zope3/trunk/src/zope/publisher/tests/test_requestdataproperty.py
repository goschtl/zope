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
$Id: test_requestdataproperty.py,v 1.2 2002/12/25 14:15:19 jim Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite

from zope.interface.common.tests.basemapping \
     import testIEnumerableMapping, testIReadMapping

from zope.publisher.base \
     import RequestDataProperty, RequestDataGetter, RequestDataMapper

class TestDataGettr(RequestDataGetter): _gettrname = 'getSomething'
class TestDataMapper(RequestDataMapper): _mapname = '_data'

_marker = object()
class Data(object):

    def getSomething(self, name, default=_marker):
        if name.startswith('Z'):
            return "something %s" % name

        if default is not _marker:
            return default

        raise KeyError, name

    something = RequestDataProperty(TestDataGettr)
    somedata = RequestDataProperty(TestDataMapper)

class Test(TestCase):

    def testRequestDataGettr(self):
        testIReadMapping(self, Data().something,
                         {"Zope": "something Zope"}, ["spam"])

    def testRequestDataMapper(self):
        data = Data()
        sample = {'foo': 'Foo', 'bar': 'Bar'}
        data._data = sample
        inst = data.somedata
        testIReadMapping(self, inst, sample, ["spam"])
        testIEnumerableMapping(self, inst, sample)

    def testNoAssign(self):
        data = Data()
        try: data.something = {}
        except AttributeError: pass
        else: raise """Shouldn't be able to assign"""
        try: data.somedata = {}
        except AttributeError: pass
        else: raise """Shouldn't be able to assign"""


def test_suite():
    return makeSuite(Test)

if __name__=='__main__':
    main(defaultTest='test_suite')

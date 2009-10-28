##############################################################################
#
# Copyright (c) 2008 Vanguardistas LLC.
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
import os
import unittest
import doctest
from pprint import pformat
from van.testing.layer import zcml_layer, wsgi_intercept_layer
from zope.component import getUtility
from zope.interface import Interface

try:
    import zope.testbrowser
    have_testbrowser = True
except:
    have_testbrowser = False

MARKER = 'MARKER'
_HERE = os.path.dirname(__file__)

def simple_app(environ, start_response):
    """Simplest possible application object"""
    marker = getUtility(Interface, name=u"test")
    response = pformat(environ) + "\nMarker: %s" % marker
    start_response('200 OK', [('Content-type', 'text/plain'),
                              ('X-Powered-By', 'WSGI'),
                              ('Content-length', len(response)),
                              ])
    return [response]

class ZCMLLayer:
    zcml = os.path.join(_HERE, 'ftesting.zcml')
zcml_layer(ZCMLLayer)
    
class ZCMLExtraLayer:
    zcml_features = ('extra',)
    zcml = os.path.join(_HERE, 'ftesting.zcml')
zcml_layer(ZCMLExtraLayer)

class FunctionalLayer(ZCMLLayer):
    @classmethod
    def make_application(cls):
        return simple_app
wsgi_intercept_layer(FunctionalLayer)

def test_suite():
    ftests = unittest.TestSuite([doctest.DocFileSuite('README.txt')])
    ftests.layer = FunctionalLayer
    extra_tests = unittest.TestSuite([doctest.DocFileSuite('zcml_features.txt')])
    extra_tests.layer = ZCMLExtraLayer
    if have_testbrowser:
        ftests.addTest(doctest.DocFileSuite('testbrowser.txt'))
    return unittest.TestSuite([
            ftests,
            extra_tests,
            doctest.DocTestSuite('van.testing.layer'),
            ])

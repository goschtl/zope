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

MARKER = 'MARKER'
_HERE = os.path.dirname(__file__)

def simple_app(environ, start_response):
    """Simplest possible application object"""
    start_response('200 OK', [('Content-type','text/plain')])
    marker = getUtility(Interface, name=u"test")
    return [pformat(environ), "\nMarker: %s" % marker]

class ZCMLLayer:
    zcml = os.path.join(_HERE, 'ftesting.zcml')
zcml_layer(ZCMLLayer)
    
class FunctionalLayer(ZCMLLayer):
    @classmethod
    def make_application(cls):
        return simple_app
wsgi_intercept_layer(FunctionalLayer)

def test_suite():
    ftest = doctest.DocFileSuite('README.txt')
    ftest.layer = FunctionalLayer
    return unittest.TestSuite([
            ftest,
            doctest.DocTestSuite('van.testing.layer'),
            ])

"""Test harness for zope.html functional tests.

$Id: ntests.py 3259 2005-08-19 16:46:26Z gary $
"""
import os
import unittest

import pytz

import zope.component
import zope.interface.common.idatetime
import zope.publisher.interfaces

from zope.app.testing import functional

import zc.testlayer.ftesting

#### testing framework ####

@zope.component.adapter(zope.publisher.interfaces.IRequest)
@zope.interface.implementer(zope.interface.common.idatetime.ITZInfo)
def requestToTZInfo(request):
    return pytz.timezone('US/Eastern')

#### test setup ####

EditableHtmlLayer = zc.testlayer.ftesting.FTestingLayer(
    os.path.join(os.path.split(__file__)[0], 'ftesting.zcml'),
    __name__, "EditableHtmlLayer")

def test_suite():
    suite = functional.FunctionalDocFileSuite("browser.txt")
    suite.layer = EditableHtmlLayer
    return suite

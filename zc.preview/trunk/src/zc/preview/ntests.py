"""Test harness for zc.preview functional tests.

"""
import os
import unittest

import pytz

import persistent
from zope import component, interface

import zope.interface.common.idatetime
import zope.publisher.interfaces

import zope.testing.module
from zope.app.testing import functional

#### testing framework ####

@component.adapter(zope.publisher.interfaces.IRequest)
@interface.implementer(zope.interface.common.idatetime.ITZInfo)
def requestToTZInfo(request):
    return pytz.timezone('US/Eastern')

#### test setup ####

zope.app.testing.functional.defineLayer('PreviewLayer')

class DemoContentMicrosoftWord(persistent.Persistent):
    """A content type that claims to be application/vnd.ms-word."""

class DemoContentMicrosoftExcel(persistent.Persistent):
    """A content type that claims to be application/vnd.ms-excel."""

class DemoContentMicrosoftPowerPoint(persistent.Persistent):
    """A content type that claims to be application/vnd.ms-powerpoint."""

class DemoContentPdf(persistent.Persistent):
    """A content type that claims to be appliction/pdf."""


def test_text():
    suite = functional.FunctionalDocFileSuite("text.txt")
    suite.layer = PreviewLayer
    return suite

def test_iframe():
    suite = functional.FunctionalDocFileSuite("iframe.txt")
    suite.layer = PreviewLayer
    return suite

def test_image():
    suite = functional.FunctionalDocFileSuite("image.txt")
    suite.layer = PreviewLayer
    return suite


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(test_text())
    suite.addTest(test_iframe())
    suite.addTest(test_image())
    return suite

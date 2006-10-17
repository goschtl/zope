"""Test harness for zope.html.

"""
__docformat__ = "reStructuredText"

import unittest

from zope.testing import doctest

import zope.annotation.attribute
import zope.app.form.browser.tests.test_textareawidget
import zope.app.testing.placelesssetup
import zope.component
import zope.mimetype.types

import zope.html.widget


class FckeditorWidgetTestCase(
    zope.app.form.browser.tests.test_textareawidget.TextAreaWidgetTest):

    _WidgetFactory = zope.html.widget.FckeditorWidget


def setUp(test):
    zope.app.testing.placelesssetup.setUp()
    zope.component.provideAdapter(
        zope.annotation.attribute.AttributeAnnotations)
    # we have to initialize the mimetype handling
    zope.mimetype.types.setup()


def tearDown(test):
    zope.app.testing.placelesssetup.tearDown()


def test_suite():
    return unittest.TestSuite([
        doctest.DocFileSuite(
            "docinfo.txt",
            setUp=setUp,
            tearDown=tearDown),
        doctest.DocFileSuite(
            "widget.txt",
            optionflags=(doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)),
        unittest.makeSuite(FckeditorWidgetTestCase),
        ])

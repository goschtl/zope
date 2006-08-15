"""Test harness for zope.html.

"""
__docformat__ = "reStructuredText"

from zope.testing import doctest

import zope.annotation.attribute
import zope.app.testing.placelesssetup
import zope.component
import zope.mimetype.types


def setUp(test):
    zope.app.testing.placelesssetup.setUp()
    zope.component.provideAdapter(
        zope.annotation.attribute.AttributeAnnotations)
    # we have to initialize the mimetype handling
    zope.mimetype.types.setup()


def tearDown(test):
    zope.app.testing.placelesssetup.tearDown()


def test_suite():
    return doctest.DocFileSuite(
        "docinfo.txt", setUp=setUp, tearDown=tearDown)

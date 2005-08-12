"""Test that nested macro references do the right thing.
"""
__docformat__ = "reStructuredText"

import zope.component
import zope.configuration.xmlconfig

from zope.app.pagetemplate import simpleviewclass
from zope.app.testing import functional


def test_suite():
    return functional.FunctionalDocFileSuite("test_nested.txt")

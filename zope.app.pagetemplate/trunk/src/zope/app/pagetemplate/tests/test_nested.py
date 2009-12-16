"""Test that nested macro references do the right thing.
"""
__docformat__ = "reStructuredText"

import os
from zope.app.testing.functional import ZCMLLayer

PageTemplateLayer = ZCMLLayer(
    os.path.join(os.path.split(__file__)[0], 'ftesting.zcml'),
    __name__, 'PageTemplateLayer', allow_teardown=True)

import zope.app.testing.functional

def test_suite():
    suite = zope.app.testing.functional.FunctionalDocFileSuite(
        "test_nested.txt")
    suite.layer = PageTemplateLayer
    return suite

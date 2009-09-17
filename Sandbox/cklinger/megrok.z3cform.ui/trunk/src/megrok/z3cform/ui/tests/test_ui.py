"""
  >>> from zope.interface import Interface
  >>> from zope.component import getMultiAdapter
  >>> from zope.publisher.browser import TestRequest
  >>> from z3c.template.interfaces import IPageTemplate

  >>> request = TestRequest()
  >>> pt = getMultiAdapter((Interface, request), Interface, name=u"display")
  3
"""

def test_suite():
    from zope.testing import doctest
    from megrok.z3cform.ui.tests import FunctionalLayer
    suite = doctest.DocTestSuite(
          optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS)
    suite.layer = FunctionalLayer
    return suite


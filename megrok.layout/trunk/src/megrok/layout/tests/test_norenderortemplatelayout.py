"""
  >>> grok.testing.grok(__name__)
  Traceback (most recent call last):
  ...
  ConfigurationExecutionError: <class 'martian.error.GrokError'>: View <class 'megrok.layout.tests.test_norenderortemplatelayout.MyLayout'> has no associated template or 'render' method.
  in:
  <BLANKLINE>
"""

import grokcore.component as grok
from grokcore.view import View
from megrok.layout import Layout
from zope.interface import Interface


class MyLayout(Layout):
    grok.context(Interface)


def test_suite():
    from zope.testing import doctest
    from megrok.layout.ftests import FunctionalLayer
    suite = doctest.DocTestSuite(
        optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS
        )
    suite.layer = FunctionalLayer
    return suite

"""
  >>> grok.testing.grok(__name__) 
  Traceback (most recent call last):
  ...
  ConfigurationExecutionError: <class 'martian.error.GrokError'>: Multiple possible ways to render view <class 'megrok.layout.tests.test_renderandtemplate.MyLayout'>. It has both a 'render' method as well as an associated template.
  <BLANKLINE>
"""

import grokcore.component as grok
from grokcore.view import View
from megrok.layout import Layout
from zope.interface import Interface


class MyLayout(Layout):
    grok.context(Interface)

    def render(self):
        return ""

def test_suite():
    from zope.testing import doctest
    from megrok.layout.ftests import FunctionalLayer
    suite = doctest.DocTestSuite(
        optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS
        )
    suite.layer = FunctionalLayer
    return suite

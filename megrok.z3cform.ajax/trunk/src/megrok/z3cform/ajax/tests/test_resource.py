"""
Let's import and init the necessary work environment::

  >>> import grokcore.component as grok
  >>> from zope.testbrowser.testing import Browser

  >>> browser = Browser()
  >>> browser.handleErrors = False

  >>> browser.open('http://localhost/@@base')
  >>> print browser.contents
  <html><head>
    <script ... src="http://localhost/@@/jquery/jquery-1.4.2.js"></script>
    <script ... src="http://localhost/@@/++noop++.../ajaxlib/validation.js"></script>
  </head></html>

"""

import grokcore.view as grok

from megrok.z3cform.ajax import InlineValidation 
from zope.interface import Interface


class Base(grok.View):
    grok.context(Interface)

    def update(self):
        InlineValidation.need()

    def render(self):
        return "<html><head> </head></html>"


def test_suite():
    from zope.testing import doctest
    from megrok.z3cform.ajax.tests import FunctionalLayer
    suite = doctest.DocTestSuite(
          optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS)
    suite.layer = FunctionalLayer
    return suite

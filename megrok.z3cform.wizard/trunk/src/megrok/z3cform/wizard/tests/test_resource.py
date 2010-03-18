"""
Let's import and init the necessary work environment::

  >>> import grokcore.component as grok
  >>> from zope.testbrowser.testing import Browser

  >>> browser = Browser()
  >>> browser.handleErrors = False

  >>> browser.open('http://localhost/@@wizardresource')
  >>> print browser.contents
  <html><head>
    <script ... src="http://localhost/@@/jquery/jquery-1.4.2.js"></script>
    <script ... src="http://localhost/@@/++noop++.../ajaxwizard/z3c.js"></script>
  </head>...</html>

"""

import grokcore.view as grok

from megrok.z3cform.wizard import z3cWizard 
from zope.interface import Interface


class WizardResource(grok.View):
    grok.context(Interface)

    def update(self):
        z3cWizard.need()

    def render(self):
        return "<html><head> </head></html>"


def test_suite():
    from zope.testing import doctest
    from megrok.z3cform.wizard.tests import FunctionalLayer
    suite = doctest.DocTestSuite(
          optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS)
    suite.layer = FunctionalLayer
    return suite

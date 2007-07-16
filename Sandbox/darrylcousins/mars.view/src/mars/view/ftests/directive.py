"""
Test the claimed directives.

  >>> import grok
  >>> grok.grok('mars.view.ftests.directive')

  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser()
  >>> browser.handleErrors = False

"""

import grok
import mars.view


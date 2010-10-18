"""
  >>> grok.testing.grok(__name__)
  Traceback (most recent call last):
  ...
  ConfigurationExecutionError: <class 'martian.error.GrokError'>: View <class 'megrok.layout.tests.errors.norenderortemplatelayout.MyLayout'> has no associated template or 'render' method.
  in:
  <BLANKLINE>
"""

import grokcore.component as grok
from grokcore.view import View
from megrok.layout import Layout
from zope.interface import Interface


class MyLayout(Layout):
    grok.context(Interface)

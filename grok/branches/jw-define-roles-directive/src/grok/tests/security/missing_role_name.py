"""
A role has to have a name to be defined.

  >>> grok.grok(__name__)
  Traceback (most recent call last):
  GrokError: A role needs to have a dotted name for its id.
  Use grok.name to specifiy one.
"""

import grok
import zope.interface

class MissingName(grok.Role):
    pass

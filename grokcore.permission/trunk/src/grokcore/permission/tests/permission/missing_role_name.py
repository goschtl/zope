"""
A role has to have a name to be defined.

  >>> grokcore.permission.testing.grok(__name__)
  Traceback (most recent call last):
  GrokError: A role needs to have a dotted name for its id.
  Use grok.name to specify one.
"""

import zope.interface
import grokcore.permission
import grokcore.permission.testing

class MissingName(grokcore.permission.components.Role):
    pass

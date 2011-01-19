"""
  >>> grok.testing.grok(
  ....    'grokcore.view.tests.inheritance.a_template_b_none_fixture')
  >>> grok.testing.grok(__name__)

"""

import grokcore.view as grok
from grokcore.view.tests.inheritance.a_template_b_none_fixture import A

class B(A):
    pass

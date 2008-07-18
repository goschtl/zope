"""

  >>> from grokcore.view.tests.test_all import grok
  >>> grok(__name__)

  >>> cave = Cave()
  >>> from zope.publisher.browser import TestRequest
  >>> request = TestRequest()
  >>> from zope.component import getMultiAdapter

  >>> view = getMultiAdapter((cave, request), name='piepmatz')
  >>> print view()
  <p>Piep! Piep!</p>

"""

from grokcore.view.tests.components import TestView
from grokcore.view.tests.components import TestModel


class Cave(TestModel):
    pass


class Piepmatz(TestView):
    pass # template in zpt_templates/piepmatz.pt

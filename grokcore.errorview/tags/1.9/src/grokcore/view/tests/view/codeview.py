"""

  >>> grok.testing.grok(__name__)

  >>> from zope.publisher.browser import TestRequest
  >>> from zope.component import getMultiAdapter

  >>> mammoth = Mammoth()

  >>> code_view = getMultiAdapter((mammoth, TestRequest()), name="cavepainting")
  >>> print code_view()
  A cave painting of a mammoth

"""

import grokcore.view as grok

class Mammoth(grok.Context):
    pass

class CavePainting(grok.CodeView):

    def render(self):
        return 'A cave painting of a mammoth'

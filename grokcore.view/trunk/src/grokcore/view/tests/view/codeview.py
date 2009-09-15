"""

  >>> grok.testing.grok(__name__)

  >>> from zope.publisher.browser import TestRequest
  >>> from zope.interface.verify import verifyObject
  >>> from zope.component import getMultiAdapter
  >>> from grokcore.view.interfaces import IGrokCodeView

  >>> mammoth = Mammoth()

  >>> code_view = getMultiAdapter((mammoth, TestRequest()), name="cavepainting")
  >>> print code_view()
  A cave painting of a mammoth

  >>> verifyObject(IGrokCodeView, code_view)
  True

"""

import grokcore.view as grok

class Mammoth(grok.Context):
    pass

class CavePainting(grok.CodeView):

    def render(self, **kwargs):
        return 'A cave painting of a mammoth'

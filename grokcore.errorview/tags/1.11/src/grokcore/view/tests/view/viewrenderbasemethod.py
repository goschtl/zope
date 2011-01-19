"""

  >>> grok.testing.grok(__name__)

  >>> from zope.publisher.browser import TestRequest
  >>> from zope.component import getMultiAdapter

  >>> mammoth = Mammoth()

  >>> view = getMultiAdapter((mammoth, TestRequest()), name="cavepicture")
  >>> print view()
  <b> cave picture </b> 

"""

import grokcore.view as grok

class Mammoth(grok.Context):
    pass

class CavePicture(grok.View):

    def render(self):
        return 'A cave painting of a mammoth'

    render.base_method = True

cavepicture = grok.PageTemplate('<b> cave picture </b>')	

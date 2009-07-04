"""

  >>> grok.testing.grok(__name__)
  Traceback (most recent call last):
  ...
  GrokError: View Class '<class 'grokcore.view.tests.view.viewwithrender.CavePainting'>' has a render method, use CodeView instead

"""

import grokcore.view as grok

class Mammoth(grok.Context):
    pass

class CavePainting(grok.View):

    def render(self):
        return 'A cave painting of a mammoth'

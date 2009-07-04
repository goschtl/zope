"""

  >>> grok.testing.grok(__name__)
  Traceback (most recent call last):
  ...
  GrokError: CodeView Class '<class 'grokcore.view.tests.view.codeviewnorender.CaveTiger'>' without an render method 

"""

import grokcore.view as grok

class Mammoth(grok.Context):
    pass

class CaveTiger(grok.CodeView):
    pass

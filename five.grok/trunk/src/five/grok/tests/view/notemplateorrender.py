"""
Views either need an associated template or a ``render`` method:

  >>> grok.testing.grok(__name__)
  Traceback (most recent call last):
    ...
  ConfigurationExecutionError: martian.error.GrokError: View <class 'five.grok.tests.view.notemplateorrender.CavePainting'>
  has no associated template or 'render' method.
  in:

"""

from five import grok

class Mammoth(grok.Model):
    pass

class CavePainting(grok.View):
    pass

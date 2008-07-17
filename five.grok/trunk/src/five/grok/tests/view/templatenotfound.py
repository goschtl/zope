"""
This should fail because ``grok.template`` points to a non-existing
template:

  >>> grok.testing.grok(__name__)
  Traceback (most recent call last):
    ...
  ConfigurationExecutionError: martian.error.GrokError: View <class 'five.grok.tests.view.templatenotfound.Painting'>
  has no associated template or 'render' method.
  in:
"""
from five import grok

class Mammoth(grok.Model):
    pass

class Painting(grok.View):
    grok.template('cavepainting')

# no cavepainting template here

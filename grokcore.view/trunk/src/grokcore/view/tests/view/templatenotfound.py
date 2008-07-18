"""
This should fail because ``grok.template`` points to a non-existing
template:

  >>> grok.testing.grok(__name__)
  Traceback (most recent call last):
    ...
  ConfigurationExecutionError: martian.error.GrokError: View <class 'grokcore.view.tests.view.templatenotfound.Painting'>
  has no associated template or 'render' method.
  in:
"""
from grokcore.view.tests import grok
import grokcore.view


class Mammoth(grok.Model):
    pass


class Painting(grok.View):
    grokcore.view.template('cavepainting')

# no cavepainting template here

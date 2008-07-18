"""
It is too confusing to have a template that would be implicitly
associated with a view while that view already refers to another
template using grokcore.view.template.  Therefore there is an error:

  >>> grok.testing.grok(__name__)
  Traceback (most recent call last):
    ...
  ConfigurationExecutionError: martian.error.GrokError: Multiple possible templates for view
  <class 'grokcore.view.tests.view.explicitimplicittemplate.Painting'>.
  It uses grok.template('cavepainting'), but there is also a template
  called 'painting'.
  in:

"""
from grokcore.view.tests import grok
import grokcore.view


class Mammoth(grok.Model):
    pass


class Painting(grok.View):
    grokcore.view.template('cavepainting')


cavepainting = grokcore.view.PageTemplate("GROK CAVEPAINT MAMMOTH!")

painting = grokcore.view.PageTemplate("GROK PAINT MAMMOTH!")

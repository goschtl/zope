"""
Inline templates that are not associated with a view class will
provoke an error:

  >>> import warnings
  >>> saved_warn = warnings.warn
  >>> warnings.warn = grok.testing.warn

  >>> grok.testing.grok(__name__)
  From grok.testing's warn():
  ...UserWarning: Found the following unassociated template(s) when grokking
  'grokcore.view.tests.view.inline_unassociated': club. Define view classes inheriting
  from grok.View to enable the template(s)...

  >>> warnings.warn = saved_warn

"""
from grokcore.view.tests import grok
import grokcore.view


class Mammoth(grok.Model):
    pass


club = grokcore.view.PageTemplate("""\
<html><body><h1>GROK CLUB MAMMOTH!</h1></body></html>
""")

"""
A template directory may only contain recognized template files::

  >>> from grokcore.view.testing import warn
  >>> import warnings
  >>> saved_warn = warnings.warn
  >>> warnings.warn = warn

  >>> grok.testing.grok(__name__)
  From grok.testing's warn():
  ... UserWarning: File 'invalid.txt' has an unrecognized extension in
  directory '...dirtemplatesonly_templates'...

  >>> warnings.warn = saved_warn

"""
import grokcore.view as grok

class Mammoth(grok.Context):
    pass

class Index(grok.View):
    pass

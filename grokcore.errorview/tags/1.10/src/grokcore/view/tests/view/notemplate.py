"""
Views need an associated template.

    >>> grok.testing.grok(__name__)
    Traceback (most recent call last):
    ...
    ConfigurationExecutionError: <class 'martian.error.GrokError'>: View <class 'grokcore.view.tests.view.notemplate.CavePainting'> has no associated template.
      in:
    <BLANKLINE>    

"""

import grokcore.view as grok

class Mammoth(grok.Context):
    pass

class CavePainting(grok.View):
    pass

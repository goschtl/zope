"""
A View may only have an associated template.  Not a render-method, for that
you must use CodeView.  Here we check that this also works for templates in a
template-directory:

    >>> grok.testing.grok(__name__)
    Traceback (most recent call last):
    ...
    GrokError: View Class '<class 'grokcore.view.tests.view.dirtemplateandrender.CavePainting'>' has a render method, use CodeView instead

"""
import grokcore.view as grok

class Mammoth(grok.Context):
    pass

class CavePainting(grok.View):
    def render(self):
        pass

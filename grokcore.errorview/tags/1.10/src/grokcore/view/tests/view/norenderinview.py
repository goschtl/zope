"""
Only a template may be specified, not a render() method.  Use CodeView if you
want a render method.

    >>> grok.testing.grok(__name__)
    Traceback (most recent call last):
    ...
    GrokError: View Class '<class 'grokcore.view.tests.view.norenderinview.CavePainting'>' has a render method, use CodeView instead

"""
import grokcore.view as grok

class Mammoth(grok.Context):
    pass

class CavePainting(grok.View):
    def render(self):
        pass

cavepainting = grok.PageTemplate("nothing")

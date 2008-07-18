"""
This should fail:
"""
from grokcore.view.tests import grok

class MultipleNames(grok.View):
    grok.name('mammoth')
    grok.name('bear')

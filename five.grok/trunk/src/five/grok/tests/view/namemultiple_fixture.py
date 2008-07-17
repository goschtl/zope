"""
This should fail:
"""
from five import grok

class MultipleNames(grok.View):
    grok.name('mammoth')
    grok.name('bear')

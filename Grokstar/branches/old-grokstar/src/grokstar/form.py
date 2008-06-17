import grok
from zope.interface import Interface

class GrokstarAddForm(grok.AddForm):
    pass

class GrokstarEditForm(grok.EditForm):
    pass

grok.context(Interface)

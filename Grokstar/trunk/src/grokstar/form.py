import grok
from base import ViewBase

class GrokstarAddForm(grok.AddForm, ViewBase):
    pass

class GrokstarEditForm(grok.EditForm, ViewBase):
    pass

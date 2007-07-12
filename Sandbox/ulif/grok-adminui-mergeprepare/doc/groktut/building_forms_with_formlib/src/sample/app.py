import grok
from zope.schema import TextLine

class Sample(grok.Application, grok.Container):
    text = 'default text'

class Index(grok.View):
    pass

class Edit(grok.EditForm):
    form_fields = grok.Fields(
        text=TextLine(title=u'The text to store:'))

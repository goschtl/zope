import grokcore.view
import megrok.pagetemplate
from browser import HelloWorldEditForm

class FormLayout(megrok.pagetemplate.PageTemplate):
    grokcore.viewlet.view(HelloWorldEditForm)


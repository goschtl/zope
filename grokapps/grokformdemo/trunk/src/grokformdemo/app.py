import grok

from megrok.z3cform.base.components import GrokForm
from megrok.layout import Layout, Page
from zope.interface import Interface
import megrok.pagetemplate 
import grokcore.viewlet

class Grokformdemo(grok.Application, grok.Container):
    pass


class MyLayout(Layout):
    grok.context(Interface)
    grok.name('mylayout')


class Index(Page):
    pass # see app_templates/index.pt



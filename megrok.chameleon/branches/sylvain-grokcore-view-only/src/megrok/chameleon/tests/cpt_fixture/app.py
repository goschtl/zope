from grokcore.component.interfaces import IContext
from zope.app.container.btree import BTreeContainer
from zope.interface import implements
from megrok.chameleon import components

import grokcore.view


class Mammoth(BTreeContainer):
    implements(IContext)

class CavePainting(grokcore.view.View):
    pass

class Food(grokcore.view.View):

    text = "<ME GROK EAT MAMMOTH!>"

    def me_do(self):
        return self.text

class Inline(grokcore.view.View):
    sometext = 'Some Text'

inline = components.ChameleonPageTemplate(
    "<html><body>ME GROK HAS INLINES! ${view.sometext}</body></html>")

class Vars(grokcore.view.View):
    pass

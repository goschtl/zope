from grokcore.component.interfaces import IContext
from zope.app.container.btree import BTreeContainer
from zope.interface import implements
from megrok.chameleon import components

import grokcore.view

class Mammoth(BTreeContainer):
    implements(IContext)

class CavePainting(grokcore.view.View):
    pass

class Static(grokcore.view.View):
    def render(self): return
    pass

class Gatherer(grokcore.view.View):
    pass

class Food(grokcore.view.View):

    text = "ME GROK EAT MAMMOTH!"

    def me_do(self):
        return self.text

class Hunter(grokcore.view.View):

    game = "MAMMOTH!"

class Inline(grokcore.view.View):
    pass

inline = components.ChameleonPageTemplate(
    "<html><body>ME GROK HAS INLINES!</body></html>")

class Fake(grokcore.view.View):
    # A fake view to stop faulty template registry from complaining about
    # missing classes.
    grokcore.view.template('berries')

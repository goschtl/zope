import grokcore.view
from megrok.chameleon import components

class Mammoth(grokcore.view.Context):
    pass

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


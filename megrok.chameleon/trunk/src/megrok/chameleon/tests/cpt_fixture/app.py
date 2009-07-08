import grok
from megrok.chameleon import components

class Mammoth(grok.Application, grok.Container):
    pass

class CavePainting(grok.View):
    pass

class Food(grok.View):
    
    text = "<ME GROK EAT MAMMOTH!>"
    
    def me_do(self):
        return self.text

class Inline(grok.View):
    sometext = 'Some Text'

inline = components.ChameleonPageTemplate(
    "<html><body>ME GROK HAS INLINES! ${view.sometext}</body></html>")

class Vars(grok.View):
    pass

class Expressions(grok.View):
    pass

class MainArea(grok.ViewletManager):
    grok.name('main')

class MainContent(grok.Viewlet):
    grok.view(Expressions)
    grok.viewletmanager(MainArea)
    def render(self):
        return 'Hello from viewlet'

import grok
from zope import interface, schema

class Pebbles(grok.Application, grok.Container):

    def addMammoth(self, name, weight):
        self[name] = Mammoth(name, weight)

    def eatMammoth(self, name):
        del self[name]    
        
class Index(grok.View):
    grok.context(Pebbles)
        
class Eat(grok.View):
    grok.context(Pebbles)
    def render(self, names):
        for name in names:
            self.context.eatMammoth(name)
        self.redirect(self.url('index'))

class IMammoth(interface.Interface):
    name = schema.TextLine(title=u"Name", required=True)
    weight = schema.Int(title=u'Weight', min=0)

class Mammoth(grok.Model):
    interface.implements(IMammoth)
    def __init__(self, name, weight):
        self.name = name
        self.weight = weight

class MammothDetails(grok.View):
    grok.context(Mammoth)
    grok.name('index')
    
class Edit(grok.EditForm):
    grok.context(Mammoth)

class AddMammoth(grok.AddForm):
    grok.context(Pebbles)
    form_fields = grok.AutoFields(Mammoth)

    @grok.action('Add mammoth')
    def add(self, name, weight):
        mammoth = Mammoth(name, weight)
        self.context[name] = mammoth
        self.redirect(self.url(self.context))



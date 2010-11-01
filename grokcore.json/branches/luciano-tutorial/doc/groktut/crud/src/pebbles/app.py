import grok

class Pebbles(grok.Application, grok.Container):

    def addMammoth(self, name, weight):
        self[name] = Mammoth(name, weight)

    def eatMammoth(self, name):
        del self[name]    
        
class Index(grok.View):
    grok.context(Pebbles)

    def update(self, name=None, weight=0):
        if name is None:
            return
        self.context.addMammoth(name, weight)
        self.redirect(self.url('index'))
        
class Eat(grok.View):
    grok.context(Pebbles)
    def render(self, names):
        for name in names:
            self.context.eatMammoth(name)
        self.redirect(self.url('index'))

class Mammoth(grok.Model):
    def __init__(self, name, weight):
        self.name = name
        self.weight = weight

class MammothDetails(grok.View):
    grok.context(Mammoth)
    grok.name('index')


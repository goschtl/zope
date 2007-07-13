import grok

class Pebbles(grok.Application, grok.Container):

    def receive(self, source, quantity):
        self[source] = Entry(source, quantity)
    
        
class Index(grok.View):
    grok.context(Pebbles)

    def update(self, source=None, quantity=0):
        if description is None:
            return
        self.context.receive(source, quantity)
        self.redirect(self.url('index'))


class Gift(grok.Model):
    def __init__(self, source, quantity):
        self.source = source
        self.quantity = quantity

class GiftIndex(grok.View):
    grok.context(Gift)
    grok.name('index')

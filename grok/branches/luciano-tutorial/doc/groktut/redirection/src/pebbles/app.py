import grok

class Pebbles(grok.Application, grok.Container):
    quantity = 0

class Index(grok.View):
    pass # see app_templates/index.pt
    
class Edit(grok.View):
    def update(self, quantity=None):
        if quantity is None:
            return
        self.context.quantity = quantity
        self.redirect(self.url('index'))
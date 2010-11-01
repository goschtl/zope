import grok

class Pebbles(grok.Application, grok.Container):
    def __init__(self):
        super(Pebbles, self).__init__()
        self.gifts = []

    def addGift(self, quantity):
        self.gifts.append(quantity)
        self._p_changed = True
    
class Index(grok.View):
    pass

class Edit(grok.View):
    def update(self, text=None):
        if text is None:
            return
        self.context.addGift(quantity)
        self.redirect(self.url('index'))

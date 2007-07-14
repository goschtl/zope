import grok

class Pebbles(grok.Application, grok.Container):
    def __init__(self):
        super(Pebbles, self).__init__()
        self.mammoths = []
    
class Index(grok.View):
    pass

class Edit(grok.View):
    def update(self, name=None):
        if name is None:
            return
        # this code has a BUG!
        self.context.mammoths.append(name)
        self.redirect(self.url('index'))

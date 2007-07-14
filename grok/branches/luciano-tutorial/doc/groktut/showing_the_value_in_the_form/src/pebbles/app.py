import grok

class Pebbles(grok.Application, grok.Container):
    mammoths = 0

class Index(grok.View):
    pass # see app_templates/index.pt
    
class Edit(grok.View):
    def update(self, number=None):
        if number is None:
            return
        self.context.mammoths = number
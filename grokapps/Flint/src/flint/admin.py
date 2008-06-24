import grok

class FlintAdmin(grok.Container):
    pass

class Index(grok.View):
    grok.context(FlintAdmin)

    def render(self):
        return 'Here is the ManageIndex'
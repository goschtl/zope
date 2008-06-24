import grok
from flint.admin import FlintAdmin

FLINT_ADMIN_NAME = 'flint'

class Flint(grok.Application, grok.Container):

    def __init__(self):
        super(Flint, self).__init__()
        self.flint = self[FLINT_ADMIN_NAME] = FlintAdmin()

class Index(grok.View):
    pass



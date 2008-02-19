import grok
from megrok.simpleauth.directives import setup_authentication_if_it_pleases_you_mr_grok

class SimpleAuthTest(grok.Application, grok.Container):
    setup_authentication_if_it_pleases_you_mr_grok()

class Index(grok.View):
    pass # see app_templates/index.pt
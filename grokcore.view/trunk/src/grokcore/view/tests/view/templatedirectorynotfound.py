"""
If the template directory you specify doesn't exist, you have a comprehensible
error:

  >>> grok.testing.grok(__name__)

"""

import grokcore.view as grok

grok.templatedir('idontexit')

class Mammoth(grok.Context):
    pass

class Food(grok.View):
    pass

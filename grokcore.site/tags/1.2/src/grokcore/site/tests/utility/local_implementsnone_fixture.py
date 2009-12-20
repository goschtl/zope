import grokcore.site
from zope import interface

class Fireplace(object):
    pass

class Cave(grokcore.site.Site):
    grokcore.site.local_utility(Fireplace)

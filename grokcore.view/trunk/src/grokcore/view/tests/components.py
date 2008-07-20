from zope import interface
from grokcore.component.interfaces import IContext
import grokcore.view


class Model(object):
    interface.implements(IContext)


class View(grokcore.view.View):
    pass

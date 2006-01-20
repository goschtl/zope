from zope.interface import Interface,implements
from zope.schema import TextLine,Int
from zope.interface.common.mapping import IReadMapping
#from zorg.table import Action

#class SelectAction(Action):
#    def applyToConfig(self,config):
#        config.selection['priority'] = config.all

class ISimple(Interface):
    name = TextLine(title=u'title')
    priority = Int(title=u'Priority')

class Simple(object):
    implements(ISimple)
    def __init__(self,name,priority):
        self.name,self.priority = name,priority

class Container(dict):
    implements(IReadMapping)
    pass

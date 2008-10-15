
from zope import interface
import martian

class view(martian.Directive):
    scope = martian.CLASS_OR_MODULE
    store = martian.ONCE
    default = interface.Interface
    validate = martian.validateInterfaceOrClass

class viewletmanager(martian.Directive):
    scope = martian.CLASS_OR_MODULE
    store = martian.ONCE
    default = interface.Interface
    validate = martian.validateInterfaceOrClass

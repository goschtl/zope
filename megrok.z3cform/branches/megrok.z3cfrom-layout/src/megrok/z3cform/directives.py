import martian
from martian import validateInterfaceOrClass
from z3c.form import interfaces

class field(martian.Directive):
    scope = martian.CLASS
    store = martian.ONCE
    default = None
    # validate = validateInterfaceOrClass

class mode(martian.Directive):
    scope = martian.CLASS
    store = martian.ONCE
    default = interfaces.INPUT_MODE 
    # validate = validateInterfaceOrClass

class view(martian.Directive):
    scope = martian.CLASS
    store = martian.ONCE
    default = None
    # validate = validateInterfaceOrClass

class widget(martian.Directive):
    scope = martian.CLASS
    store = martian.ONCE
    default = None

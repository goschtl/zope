import martian
from martian import validateInterfaceOrClass

class field(martian.Directive):
    scope = martian.CLASS
    store = martian.ONCE
    default = None
    # validate = validateInterfaceOrClass

class mode(martian.Directive):
    scope = martian.CLASS
    store = martian.ONCE
    default = None
    # validate = validateInterfaceOrClass

class view(martian.Directive):
    scope = martian.CLASS
    store = martian.ONCE
    default = None
    # validate = validateInterfaceOrClass

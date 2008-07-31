from martian import Directive, CLASS, CLASS_OR_MODULE, ONCE

# XXX add proper validation logic

class type(Directive):
    scope = CLASS
    store = ONCE
    default = u''

class key(Directive):
    scope = CLASS
    store = ONCE
    default = u''

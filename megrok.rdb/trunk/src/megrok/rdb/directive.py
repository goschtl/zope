from martian import Directive, CLASS, CLASS_OR_MODULE, ONCE

# XXX add proper validation logic

class key(Directive):
    scope = CLASS
    store = ONCE
    default = u''

class metadata(Directive):
    scope = CLASS_OR_MODULE
    store = ONCE
    default = None

class tablename(Directive):
    scope = CLASS
    store = ONCE
    default = u''

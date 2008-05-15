from martian import Directive, CLASS, ONCE

class key(Directive):
    scope = CLASS
    store = ONCE
    default = u''


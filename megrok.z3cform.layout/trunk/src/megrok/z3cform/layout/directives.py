import martian

class cancellable(martian.Directive):
    scope = martian.CLASS
    store = martian.ONCE
    default = False

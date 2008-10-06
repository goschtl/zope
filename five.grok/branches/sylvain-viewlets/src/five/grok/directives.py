
import martian

class view(martian.Directive):
    scope = martian.CLASS_OR_MODULE
    store = martian.ONCE
    default = None
    validate = martian.validateInterfaceOrClass

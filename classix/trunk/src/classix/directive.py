import martian
        
class parser(martian.Directive):
    scope = martian.CLASS
    store = martian.ONCE
    validate = martian.validateClass
    
def validateTextOrNone(self, value):
    if value is None:
        return value
    return martian.validateText(self, value)

class namespace(martian.Directive):
    scope = martian.CLASS
    store = martian.ONCE
    validate = validateTextOrNone

class name(martian.Directive):
    scope = martian.CLASS
    store = martian.ONCE
    validate = martian.validateText

import martian

class pattern(martian.Directive):
    scope = martian.CLASS
    store = martian.ONCE
    validate = martian.validateText

# these are dummy decorators for now
def factory(object):
    return object

def arguments(object):
    return object


import martian
from zope.publisher.interfaces.browser import IBrowserView


class template(martian.Directive):
    scope = martian.CLASS
    store = martian.ONCE
    validate = martian.validateText


class templatedir(martian.Directive):
    scope = martian.MODULE
    store = martian.ONCE
    validate = martian.validateText


class OneInterfaceOrClassOnClassOrModule(martian.Directive):
    """Convenience base class.  Not for public use."""
    scope = martian.CLASS_OR_MODULE
    store = martian.ONCE
    validate = martian.validateInterfaceOrClass


class layer(OneInterfaceOrClassOnClassOrModule):
    pass


class view(OneInterfaceOrClassOnClassOrModule):
    default = IBrowserView

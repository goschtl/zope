import martian
from grokcore.component.scan import UnambiguousComponentScope
from zope.publisher.interfaces.browser import IBrowserView


class OneInterfaceOrClassOnClassOrModule(martian.Directive):
    """Convenience base class.  Not for public use."""
    scope = martian.CLASS_OR_MODULE
    store = martian.ONCE
    validate = martian.validateInterfaceOrClass


class layer(OneInterfaceOrClassOnClassOrModule):
    pass


class viewletmanager(OneInterfaceOrClassOnClassOrModule):
    scope = UnambiguousComponentScope('viewletmanager')


class view(OneInterfaceOrClassOnClassOrModule):
    default = IBrowserView

import sys

from zope.publisher.interfaces.browser import IBrowserView

import martian
from martian import util
from martian.directive import StoreMultipleTimes
from martian.error import GrokError
from martian.error import GrokImportError

import grokcore.component

from grokcore.view.components import Permission


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


class RequireDirectiveStore(StoreMultipleTimes):

    def get(self, directive, component, default):
        permissions = getattr(component, directive.dotted_name(), default)
        if (permissions is default) or not permissions:
            return default
        if len(permissions) > 1:
            raise GrokError('grok.require was called multiple times in '
                            '%r. It may only be set once for a class.'
                            % component, component)
        return permissions[0]

    def pop(self, locals_, directive):
        return locals_[directive.dotted_name()].pop()


class require(martian.Directive):
    scope = martian.CLASS
    store = RequireDirectiveStore()

    def validate(self, value):
        if util.check_subclass(value, Permission):
            return
        if util.not_unicode_or_ascii(value):
            raise GrokImportError(
                "You can only pass unicode, ASCII, or a subclass "
                "of grok.Permission to the '%s' directive." % self.name)

    def factory(self, value):
        if util.check_subclass(value, Permission):
            return grokcore.component.name.bind().get(value)
        return value

    def __call__(self, func):
        # grok.require can be used both as a class-level directive and
        # as a decorator for methods.  Therefore we return a decorator
        # here, which may be used for methods, or simply ignored when
        # used as a directive.
        frame = sys._getframe(1)
        permission = self.store.pop(frame.f_locals, self)
        self.set(func, [permission])
        return func

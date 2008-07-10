import martian
from martian.directive import StoreMultipleTimes

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
    validate = martian.validateText

    def __call__(self, func):
        # grok.require can be used both as a class-level directive and
        # as a decorator for methods.  Therefore we return a decorator
        # here, which may be used for methods, or simply ignored when
        # used as a directive.
        frame = sys._getframe(1)
        permission = self.store.pop(frame.f_locals, self)
        self.set(func, [permission])
        return func


class layer(martian.Directive):
    scope = martian.CLASS_OR_MODULE
    store = martian.ONCE
    validate = martian.validateInterfaceOrClass


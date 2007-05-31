"""More verbose ComponentLookupError reporting."""

from zope.component.interfaces import ComponentLookupError

from z3c.componentdebug.component import Registrations, all_methods

class VerboseComponentLookupError(ComponentLookupError):

    def __init__(self, objects=False, provided=False, name=False,
                 context=None, methods=all_methods):
        self.registrations = Registrations(objects, provided, name,
                                           context, methods)
        ComponentLookupError.__init__(
            self, '\n'.join(
                (str(self.registrations),
                 str([i for i in self.registrations.byObject()]))))

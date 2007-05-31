"""Component lookup debugging."""

from zope.interface import providedBy
from zope.component import getSiteManager
from zope.app.component import queryNextSiteManager

all_methods=('registeredAdapters',
             'registeredSubscriptionAdapters',
             'registeredHandlers',
             'registeredUtilities')

_marker = object()
def getSiteManagers(context=None):
    """Return an iterator over the chain of site managers."""
    sm = getSiteManager(context)
    while sm is not _marker:
        yield sm
        sm = queryNextSiteManager(sm, _marker)

def getRegistrations(methods, context=None):
    for sm in getSiteManagers(context):
        for method in methods:
            for reg in getattr(sm, method)():
                yield reg

class Registrations(list):

    def __init__(self, objects=False, provided=False, name=False,
                 context=None, methods=all_methods):
        self.methods = methods

        if objects is not False:
            self.objects = objects
            self.order = len(objects)
        if provided is not False:
            self.provided = provided
        if name is not False:
            self.name = name
        if context is not None:
            self.context = context
        
        super(Registrations, self).__init__(
            reg for reg in getRegistrations(self.methods, context)
            if (provided is False or reg.provided is provided)
            and (objects is False or len(reg.required) == self.order)
            and (name is False or reg.name == name))

    def byObjects(self):
        assert hasattr(self, 'objects')
        
        idxs = xrange(self.order)
        for idx in idxs:
            object = self.objects[idx]
            provided = providedBy(object)
            result = {}
            for reg in self:
                required = reg.required[idx]
                for prov in provided:
                    if prov.isOrExtends(required):
                        result[required] = reg
                        break
            yield object, result

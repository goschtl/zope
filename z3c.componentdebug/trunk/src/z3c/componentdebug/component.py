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

def getRegistrations(methods=all_methods, context=None):
    for sm in getSiteManagers(context):
        for method in methods:
            for reg in getattr(sm, method)():
                yield reg

def cmpInterfaces(iface_x, iface_y):
    if iface_x is iface_y:
        return 0
    elif iface_x in iface_y.__iro__:
        return -1
    elif iface_y in iface_x.__iro__:
        return 1
    else:
        return 0

def cmpRegistrations(reg_x, reg_y):
    for idx in xrange(max(len(reg.required) for reg in (reg_x, reg_y))):
        cmp_ = cmpInterfaces(reg_x.required[idx], reg_y.required[idx])
        if cmp_:
            return cmp_
    else:
        return 0

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

        self.sort(cmp=cmpRegistrations, reverse=True)
        if objects is not False:
            def byMatches(reg):
                matches = [
                    reg.required[idx].providedBy(self.objects[idx])
                    for idx in xrange(self.order)]
                return sum(matches), matches
            self.sort(key=byMatches, reverse=True)
            
    def byObject(self):
        assert hasattr(self, 'objects')
        
        idxs = xrange(self.order)
        for idx in idxs:
            object = self.objects[idx]
            results = []
            for reg in self:
                required = reg.required[idx]
                if required.providedBy(object):
                    results.append(reg)
            yield object, results

    def byRegistration(self):
        assert hasattr(self, 'objects')
        for reg in self:
            yield (
                reg,
                [reg.required[idx].providedBy(self.objects[idx])
                 and self.objects[idx] for idx in xrange(self.order)])

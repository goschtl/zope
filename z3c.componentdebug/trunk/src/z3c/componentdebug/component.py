"""Component lookup debugging."""

from zope.interface import providedBy
from zope.component import getSiteManager
from zope.app.component import queryNextSiteManager

_marker = object()
def getSiteManagers(context=None, sm=None):
    """Return an iterator over the chain of site managers."""
    assert None in (context, sm)
    if sm is None:
        sm = getSiteManager(context)
    while sm is not _marker:
        yield sm
        sm = queryNextSiteManager(sm, _marker)

def inspectRequired(regs, objects, iface, name=u''):
    order = len(objects)
    idxs = xrange(order)

    # Only bother with registrations that provide the interface and
    # require the same number of objects, and has the right name
    regs = [reg for reg in regs
            if reg.provided is iface
            and len(reg.required) == order
            and reg.name == name]

    for idx in idxs:
        object = objects[idx]
        provided = providedBy(object)
        result = {}
        for reg in regs:
            req = reg.required[idx]
            for prov in provided:
                if prov.isOrExtends(req):
                    result[req] = reg
                    break
        yield object, result

def getRegistrations(methods, context=None, sm=None):
    for sm_ in getSiteManagers(context, sm):
        for method in methods:
            for reg in getattr(sm_, method)():
                yield reg

adapter_methods=('registeredAdapters',
                 'registeredSubscriptionAdapters',
                 'registeredHandlers')
def inspectRequiredAdapters(objects, iface, name=u'',
                              context=None, sm=None):
    return inspectRequired(
        getRegistrations(adapter_methods, context, sm),
        objects, iface, name)

from zope import interface

from interfaces import IFieldDiff

def diff(source, target, *interfaces):
    if not len(interfaces):
        interfaces = interface.providedBy(source)
        
    results = {}

    for iface in interfaces:
        for name in iface.names():
            field = iface[name]

            try:
                diff = IFieldDiff(field)
            except TypeError:
                continue
                
            a = diff.lines(getattr(source, name, field.default))
            b = diff.lines(getattr(target, name, field.default))

            results[field] = (a, b)

    return results
    

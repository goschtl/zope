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

            source_value = getattr(source, name, field.default)
            target_value = getattr(target, name, field.default)

            if source_value is None or target_value is None:
                continue
            
            a = diff.lines(source_value)
            b = diff.lines(target_value)
                
            results[field] = (a, b)

    return results
    

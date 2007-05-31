"""More verbose ComponentLookupError reporting."""

from zope.component.interfaces import ComponentLookupError

from z3c.componentdebug.component import Registrations, all_methods

class VerboseComponentLookupError(ComponentLookupError):

    def __init__(self, objects=False, provided=False, name=False,
                 context=None, methods=all_methods):
        self.registrations = Registrations(objects, provided, name,
                                           context, methods)

        str_ = 'Lookup failed for...\n\n'
        if objects is not False:
            str_ += 'objects: %s\n' % ', '.join(repr(i) for i in
                                                objects)
        if provided is not False:
            str_ += 'provided: %s\n' % provided
        if name is not False:
            str_ += 'name: %s\n' % name
        if context is not None:
            str_ += 'context: %s\n' % repr(context)

        if objects is not False:
            str_ += '\nRegistrations with matching objects:\n\n'
            for reg, objs in self.registrations.byRegistration():
                str_ += '%s:\n' % repr(reg)
                for idx in xrange(self.registrations.order):
                    obj = objs[idx]
                    str_ += '  - %s%s\n' % (
                        obj is False and 'unmatched: ' or '',
                        repr(objects[idx]))
    
            str_ += '\nObjects with matching registrations:\n\n'
            for obj, regs in self.registrations.byObject():
                if regs:
                    str_ += '%s:\n  - %s\n' % (
                        repr(obj), '\n  - '.join(
                            repr(i) for i in regs))
                else:
                    str_ += '%s: no matches\n' % repr(obj)
        
        ComponentLookupError.__init__(self, str_)        

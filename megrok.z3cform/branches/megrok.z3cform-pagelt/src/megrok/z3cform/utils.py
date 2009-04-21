from z3c.form import field                                                                                        
from zope.interface.interfaces import IInterface
from grokcore.formlib.formlib import most_specialized_interfaces

def get_auto_fields(context):
    """Get the form fields for context.
    """
    # for an interface context, we generate them from that interface
    if IInterface.providedBy(context):
        return field.Fields(context)
    # if we have a non-interface context, we're autogenerating them
    # from any schemas defined by the context
    fields = field.Fields(*most_specialized_interfaces(context))
    # we pull in this field by default, but we don't want it in our form
    fields = fields.omit('__name__')
    return fields

AutoFields = get_auto_fields


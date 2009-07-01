import grok
from z3c.form.form import applyChanges
from zope.lifecycleevent import Attributes

def apply_data_event(form, context, data):
    """ Updates the object with the data and sends an IObjectModifiedEvent
    """
    changes = applyChanges(form, context, data)
    if changes:
	descriptions = []
	for interface, names in changes.items():
	    descriptions.append(Attributes(interface, *names))
	grok.notify(grok.ObjectModifiedEvent(context, *descriptions))
    return changes	

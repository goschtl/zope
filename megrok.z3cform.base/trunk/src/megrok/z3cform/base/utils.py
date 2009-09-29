# -*- coding: utf-8 -*-

from zope.event import notify
from z3c.form.form import applyChanges
from zope.lifecycleevent import Attributes, ObjectModifiedEvent


def apply_data_event(form, context, data):
    """ Updates the object with the data and sends an IObjectModifiedEvent
    """
    changes = applyChanges(form, context, data)
    if changes:
        descriptions = []
        for interface, names in changes.items():
            descriptions.append(Attributes(interface, *names))
        notify(ObjectModifiedEvent(context, *descriptions))
    return changes

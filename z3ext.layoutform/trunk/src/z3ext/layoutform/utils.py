##############################################################################
#
# Copyright (c) 2008 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" 

$Id:  2007-12-12 12:27:02Z fafhrd $
"""
from zope.component import getMultiAdapter
from z3c.form.interfaces import IDataManager


def applyChanges(form, content, data):
    changes = {}
    for name, field in form.fields.items():
        # If the field is not in the data, then go on to the next one
        if name not in data:
            continue

        # Get the datamanager and get the original value
        dm = getMultiAdapter((content, field.field), IDataManager)
        # Only update the data, if it is different
        try:
            value = dm.get()
        except:
            value = object()

        if value != data[name]:
            dm.set(data[name])
            # Record the change using information required later
            changes.setdefault(dm.field.interface, []).append(name)

    return changes

##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Fixup old utility services

$Id: fixup.py,v 1.2 2004/04/15 22:11:14 srichter Exp $
"""

from zope.app import zapi
from zope.app.site.interfaces import IPossibleSite, ISite
from zope.app.utility import LocalUtilityService
from zope.app.annotation.interfaces import IAnnotations
from persistent.dict import PersistentDict
from zope.interface.adapter import Null
from zope.app.registration.registration import NotifyingRegistrationStack
from zope.app.container.interfaces import IContainer
import zope.app.event.function


key = 'zope.app.utility.fixup20040415'

class ImplementorRegistry(object):
    """Temporary replacement of old interface.implementor class
    """

def notify(event):
    db = event.database
    conn = db.open()
    try:
        root = conn.root().get('Application')
        if root is None:
            return # new db
        annotations = IAnnotations(root)
        if key in annotations:
            return

        import sys
        sys.modules['zope.interface.implementor'] = sys.modules[__name__]
        LocalUtilityService.base = zapi.getService(None, 'Utilities')
        fixup(root)
        del sys.modules['zope.interface.implementor']
        del LocalUtilityService.base
        annotations[key] = True
    finally:
        conn.close()

notify = zope.app.event.function.Subscriber(notify)

def fixup(folder):
    if ISite.providedBy(folder):
        sm = folder.getSiteManager()
        if sm is not None:
            for smfolder in sm.values():
                for item in smfolder.values():
                    if isinstance(item, LocalUtilityService):
                        if hasattr(item, '_utilities'):
                            fixup_utility_service(sm, item)

    for item in folder.values():
        if IContainer.providedBy(item):
            fixup(item)

                            
def fixup_utility_service(sm, us):
    stacks = PersistentDict()
    for name, implementor_registry in us._utilities.iteritems():
        for (provided, (registered_provided, stack)
             ) in implementor_registry._reg.iteritems():
            if provided is not registered_provided:
                continue
            newstack = NotifyingRegistrationStack(us)
            newstack.data = stack.data
            stacks[(False, (), name, provided)] = newstack
    del us._utilities
    us.__init__(zapi.getService(None, 'Utilities'))
    us.stacks = PersistentDict({Null: stacks})
    if sm.queryLocalService('Utilities') is us:
        us.notifyActivated()
    get_transaction().commit()

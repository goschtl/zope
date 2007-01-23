##############################################################################
#
# Copyright (c) 2003 Zope Corporation. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Visible Source
# License, Version 1.0 (ZVSL).  A copy of the ZVSL should accompany this
# distribution.
#
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""Sharing adapter

$Id$
"""

import persistent
import persistent.dict

from zope import component, interface, event

from zope.security.management import queryInteraction
from zope.publisher.interfaces import IRequest

from zope.annotation.interfaces import IAnnotations
from zope.app.container.interfaces import IObjectAddedEvent

from zc.sharing import interfaces
from zc.sharing.i18n import _

key = 'zc.sharing.sharing'

class SharingData(persistent.dict.PersistentDict):
    """Sharing Data
    """

class BaseSharing(object):

    component.adapts(interfaces.ISharable)
    interface.implements(interfaces.IBaseSharing)

    def __init__(self, context):
        self.context = context
        self.annotations = IAnnotations(self.context)

    def getPrincipals(self):
        privileges = self.annotations.get(key)
        if privileges:
            return privileges.keys()
        return ()

    def getBinaryPrivileges(self, principal_id):
        privileges = self.annotations.get(key)
        if privileges:
            return privileges.get(principal_id, 0)
        return 0

    def setBinaryPrivileges(self, principal_id, privileges):
        saved = self.annotations.get(key)
        if saved is None:
            self.annotations[key] = saved = SharingData()

        old = saved.get(principal_id, 0)
        if privileges:
            saved[principal_id] = privileges
        else:
            if principal_id in saved:
                del saved[principal_id]

        interaction = queryInteraction()
        if interaction is not None:
            try:
                invalidateCache = interaction.invalidateCache
            except AttributeError:
                pass
            else:
                invalidateCache()

        if old != privileges:
            event.notify(
                interfaces.SharingChanged(
                    self.context, principal_id, old, privileges,
                    )
                )

    def sharedTo(self, id, principal_ids):
        privileges = self.annotations.get(key)
        if privileges:
            bit = 2**id
            for principal_id in principal_ids:
                if bit & privileges.get(principal_id, 0):
                    return True
        return False

class Sharing(object):

    component.adapts(interfaces.ISharable)
    interface.implements(interfaces.ISharing)

    def __init__(self, context):
        self.context = context
        self.base = interfaces.IBaseSharing(context)

    # look transparently through to base for IBaseSharing methods
    def __getattr__(self, name):
        if name in (
            'getPrincipals', 'getBinaryPrivileges', 'setBinaryPrivileges',
            'sharedTo'):
            return getattr(self.base, name)

    # additional ISharing methods
    def removeBinaryPrivileges(self, principal_id, mask):
        privs = self.base.getBinaryPrivileges(principal_id)
        self.base.setBinaryPrivileges(principal_id, (privs | mask) ^ mask)

    def addBinaryPrivileges(self, principal_id, mask):
        privs = self.base.getBinaryPrivileges(principal_id)
        self.base.setBinaryPrivileges(principal_id, privs | mask)

    def getIdPrivilege(self, principal_id, id):
        return self.base.sharedTo(id, (principal_id,))
    
    def setIdPrivilege(self, principal_id, id, value):
        if value:
            return self.addIdPrivileges(principal_id, (id,))
        else:
            return self.removeIdPrivileges(principal_id, (id,))

    def getIdPrivileges(self, principal_id):
        return idsFromSetting(self.base.getBinaryPrivileges(principal_id))

    def setIdPrivileges(self, principal_id, ids):
        return self.base.setBinaryPrivileges(
            principal_id, settingFromIds(ids))

    def addIdPrivileges(self, principal_id, ids):
        return self.addBinaryPrivileges(
            principal_id, settingFromIds(ids))

    def removeIdPrivileges(self, principal_id, ids):
        return self.removeBinaryPrivileges(
            principal_id, settingFromIds(ids))

    def getPrivilege(self, principal_id, title):
        return self.getIdPrivilege(
            principal_id, getIdByTitle(title))

    def setPrivilege(self, principal_id, title, value):
        return self.setIdPrivilege(
            principal_id, getIdByTitle(title), value)

    def getPrivileges(self, principal_id):
        return [getPrivilege(bit)['title'] for bit
                in self.getIdPrivileges(principal_id)]

    def setPrivileges(self, principal_id, titles):
        return self.setIdPrivileges(
            principal_id, (getIdByTitle(title) for title in titles))

    def addPrivileges(self, principal_id, titles):
        return self.addIdPrivileges(
            principal_id, (getIdByTitle(title) for title in titles))

    def removePrivileges(self, principal_id, titles):
        return self.removeIdPrivileges(
            principal_id, (getIdByTitle(title) for title in titles))

octToBit = {
    '0': (),
    '1': (0,),
    '2': (1,),
    '3': (0, 1),
    '4': (2,),
    '5': (0, 2),
    '6': (1, 2),
    '7': (0, 1, 2)
    }
def idsFromSetting(i):
    "given an integer, return a sequence of the bits that are on"
    res = []
    for pos, c in enumerate(oct(i)[-1:0:-1]):
        place = pos*3
        res.extend(place+bit for bit in octToBit[c])
    return res

def settingFromIds(bits):
    "Given any number of bit positions, generate a corresponding integer"
    val = 0
    for bit in bits:
        val |= 1<<bit
    return val

def settingFromTitles(titles):
    return settingFromIds(getIdByTitle(t) for t in titles)

def titlesFromSetting(setting):
    return (getPrivilege(i)['title'] for i in idsFromSetting(setting))

def sharingMask(ob):
    mask = 0
    for bit in interfaces.ISharingPrivileges(ob).privileges:
        mask |= 1 << bit
    privs = interfaces.ISubobjectSharingPrivileges(ob, None)
    if privs is not None:
        for bit in privs.subobjectPrivileges:
            mask |= 1 << bit
    
    return mask


_privileges_by_bit = {}
_privileges_by_title = {}

def definePrivilege(id, title, description='', info=None):
    if title in _privileges_by_title:
        raise ValueError("Duplicate title") # TODO should be catchable in zcml
    if id in _privileges_by_bit:
        raise ValueError("Duplicate id") # is caught in zcml
    _privileges_by_bit[id] = {
        'id': id,
        'title': title,
        'description': description,
        'info': info,
        }
    _privileges_by_title[title] = id
def removePrivilege(id):
    data = _privileges_by_bit.pop(id)
    del _privileges_by_title[data['title']]
def clearPrivileges():
    _privileges_by_bit.clear()
    _privileges_by_title.clear()
getPrivileges = _privileges_by_bit.values
getPrivilege = _privileges_by_bit.get
getIdByTitle = _privileges_by_title.__getitem__

class InitialSharing(object):

    component.adapts(interfaces.ISharable, IObjectAddedEvent)
    interface.implements(interfaces.IInitialSharing)

    def __init__(self, *contexts):
        self.ob, self.event = contexts

    def sharingMask(self):
        return sharingMask(self.ob)

    def share(self):
        ob = self.ob
        event = self.event

        sharing = interfaces.IBaseSharing(ob)
        if tuple(sharing.getPrincipals()):
            return # already shared
        

        mask = self.sharingMask()

        # Get the parent settings:
        parent = event.newParent
        psharing = interfaces.IBaseSharing(parent, None)
        if psharing is not None:
            for p in psharing.getPrincipals():
                sharing.setBinaryPrivileges(
                    p, psharing.getBinaryPrivileges(p) & mask)

        # Share everything with current user, if any
        interactions = queryInteraction()
        if interactions is not None:
            for participation in interactions.participations:
                if IRequest.providedBy(participation):
                    sharing.setBinaryPrivileges(
                        participation.principal.id, mask)

def initialSharing(ob, event):
    adapter = component.getMultiAdapter((ob, event),
                                        interfaces.IInitialSharing)
    adapter.share()

from zope.testing.cleanup import addCleanUp
addCleanUp(clearPrivileges)
del addCleanUp

##############################################################################
#
# Copyright (c) 2004, 2005 Zope Corporation and Contributors.
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
Five event definitions.

May eventually be folded back into Zope 3 proper.

$Id$
"""

import warnings

from zope.event import notify
from zope.interface import implements
from zope.interface import Attribute

from zope.app.event.interfaces import IObjectEvent
from zope.app.container.interfaces import IObjectAddedEvent
from zope.app.container.interfaces import IObjectRemovedEvent

from zope.app.event.objectevent import ObjectEvent
from zope.app.container.contained import ObjectMovedEvent
from zope.app.container.contained import ObjectAddedEvent
from zope.app.container.contained import ObjectRemovedEvent
from zope.app.event.objectevent import ObjectCopiedEvent
from zope.app.container.contained import dispatchToSublocations

from Products.Five.fiveconfigure import isFiveMethod


class IObjectWillBeMovedEvent(IObjectEvent):
    """An object will be moved."""
    oldParent = Attribute("The old location parent for the object.")
    oldName = Attribute("The old location name for the object.")
    newParent = Attribute("The new location parent for the object.")
    newName = Attribute("The new location name for the object.")

class IObjectWillBeAddedEvent(IObjectWillBeMovedEvent):
    """An object will be added to a container."""

class IObjectWillBeRemovedEvent(IObjectWillBeMovedEvent):
    """An object will be removed from a container"""

class IFiveObjectClonedEvent(IObjectEvent):
    """An object has been cloned (a la Zope 2).

    This is for Zope 2 compatibility, subscribers should really use
    IObjectCopiedEvent or IObjectAddedEvent, depending on their use
    cases.

    event.object is the copied object, already added to its container.
    Note that this event is dispatched to all sublocations.
    """


class ObjectWillBeMovedEvent(ObjectEvent):
    """An object will be moved"""
    implements(IObjectWillBeMovedEvent)

    def __init__(self, object, oldParent, oldName, newParent, newName):
        ObjectEvent.__init__(self, object)
        self.oldParent = oldParent
        self.oldName = oldName
        self.newParent = newParent
        self.newName = newName

class ObjectWillBeAddedEvent(ObjectWillBeMovedEvent):
    """An object will be added to a container"""
    implements(IObjectWillBeAddedEvent)

    def __init__(self, object, newParent=None, newName=None):
        #if newParent is None:
        #    newParent = object.__parent__
        #if newName is None:
        #    newName = object.__name__
        ObjectWillBeMovedEvent.__init__(self, object, None, None,
                                        newParent, newName)

class ObjectWillBeRemovedEvent(ObjectWillBeMovedEvent):
    """An object will be removed from a container"""
    implements(IObjectWillBeRemovedEvent)

    def __init__(self, object, oldParent=None, oldName=None):
        #if oldParent is None:
        #    oldParent = object.__parent__
        #if oldName is None:
        #    oldName = object.__name__
        ObjectWillBeMovedEvent.__init__(self, object, oldParent, oldName,
                                        None, None)

class FiveObjectClonedEvent(ObjectEvent):
    implements(IFiveObjectClonedEvent)


##################################################

import sys
from cgi import escape
from zLOG import LOG, ERROR
from Acquisition import aq_base, aq_parent, aq_inner
from App.config import getConfiguration
from App.Dialogs import MessageDialog
from AccessControl import getSecurityManager
from ZODB.POSException import ConflictError
from OFS.ObjectManager import BeforeDeleteException
from OFS import Moniker
from OFS.CopySupport import CopyError # Yuck, a string exception
from OFS.CopySupport import eNoData, eNotFound, eInvalid, eNotSupported
from OFS.CopySupport import cookie_path, sanity_check, _cb_decode
from webdav.Lockable import ResourceLockedError
FIVE_ORIGINAL_PREFIX = '__five_original_'


hasContainerEvents = False
deprecatedManageAddDeleteClasses = []


def hasDeprecatedMethods(ob):
    """Do we need to call the deprecated methods?
    """
    for class_ in deprecatedManageAddDeleteClasses:
        if isinstance(ob, class_):
            return True
    return False

def maybeCallDeprecated(method_name, ob, *args):
    """Call a deprecated method, if the framework doesn't call it already.
    """
    if hasDeprecatedMethods(ob):
        # Already deprecated through zcml
        return
    method = getattr(ob, method_name)
    if isFiveMethod(method):
        # Monkey-patched method
        return
    if deprecatedManageAddDeleteClasses:
        # Not deprecated through zcml and directives fully loaded
        class_ = ob.__class__
        warnings.warn(
            "Calling %s.%s.%s is deprecated when using Five, "
            "instead use event subscribers or "
            "mark the class with <five:deprecatedManageAddDelete/>"
            % (class_.__module__, class_.__name__, method_name),
            DeprecationWarning)
    # Note that calling the method can lead to incorrect behavior
    # but in the most common case that's better than not calling it.
    method(ob, *args)


##################################################
# Adapters and subscribers

from OFS.interfaces import IObjectManager
from zope.app.location.interfaces import ISublocations

class ObjectManagerSublocations(object):
    """Get the sublocations for an ObjectManager.
    """
    #__used_for__ = IObjectManager
    #implements(ISublocations)

    def __init__(self, container):
        self.container = container

    def sublocations(self):
        for ob in self.container.objectValues():
            yield ob
        # XXX also want to provide opaqueItems's values

# The following subscribers should really be defined in ZCML
# but we don't have enough control over subscriber ordering for
# that to work exactly right.
# (Sometimes IItem comes before IObjectManager, sometimes after,
# depending on some of Zope's classes.)
# This code can be simplified when Zope is completely rid of
# manage_afterAdd & co, then IItem wouldn't be relevant anymore and we
# could have a simple subscriber for IObjectManager that directly calls
# dispatchToSublocations.

def dispatchObjectWillBeMovedEvent(ob, event):
    """Multi-subscriber for IItem + IObjectWillBeMovedEvent.
    """
    # First, dispatch to sublocations
    if IObjectManager.providedBy(ob):
        dispatchToSublocations(ob, event)
    # Next, do the manage_beforeDelete dance
    if hasDeprecatedMethods(ob):
        callManageBeforeDelete(ob, event)

def dispatchObjectMovedEvent(ob, event):
    """Multi-subscriber for IItem + IObjectMovedEvent.
    """
    # First, do the manage_afterAdd dance
    if hasDeprecatedMethods(ob):
        callManageAfterAdd(ob, event)
    # Next, dispatch to sublocations
    if IObjectManager.providedBy(ob):
        dispatchToSublocations(ob, event)

def dispatchFiveObjectClonedEvent(ob, event):
    """Multi-subscriber for IItem + IFiveObjectClonedEvent.
    """
    # First, do the manage_afterClone dance
    if hasDeprecatedMethods(ob):
        callManageAfterClone(ob, event)
    # Next, dispatch to sublocations
    if IObjectManager.providedBy(ob):
        dispatchToSublocations(ob, event)


def callManageAfterAdd(ob, event):
    """Compatibility subscriber for manage_afterAdd.
    """
    container = event.newParent
    if container is None:
        # this is a remove
        return
    ob.manage_afterAdd(event.object, container)

def callManageBeforeDelete(ob, event):
    """Compatibility subscriber for manage_beforeDelete.
    """
    container = event.oldParent
    if container is None:
        # this is an add
        return
    try:
        ob.manage_beforeDelete(event.object, container)
    except BeforeDeleteException:
        raise
    except ConflictError:
        raise
    except:
        LOG('Zope', ERROR, '_delObject() threw', error=sys.exc_info())
        # In debug mode when non-Manager, let exceptions propagate.
        if getConfiguration().debug_mode:
            if not getSecurityManager().getUser().has_role('Manager'):
                raise

def callManageAfterClone(ob, event):
    """Compatibility subscriber for manage_afterClone.
    """
    ob.manage_afterClone(event.object)


##################################################
# Monkey patches

_marker = object()

# From ObjectManager / Item
def manage_afterAdd(self, item, container):
    # Don't do recursion anymore, a subscriber does that.
    pass

# From ObjectManager / Item
def manage_beforeDelete(self, item, container):
    # Don't do recursion anymore, a subscriber does that.
    pass

# From ObjectManager / Item
def manage_afterClone(self, item):
    # Don't do recursion anymore, a subscriber does that.
    pass

# From CatalogAware / CatalogPathAware
def CA_manage_afterAdd(self, item, container):
    # Don't do recursion anymore, a subscriber does that.
    self.index_object()

# From CatalogAware / CatalogPathAware
def CA_manage_beforeDelete(self, item, container):
    # Don't do recursion anymore, a subscriber does that.
    self.unindex_object()

# From CatalogAware / CatalogPathAware
def CA_manage_afterClone(self, item):
    # Don't do recursion anymore, a subscriber does that.
    self.index_object()


# From ObjectManager
def _setObject(self, id, object, roles=None, user=None, set_owner=1,
               suppress_events=False):
    """Set an object into this container.

    Also sends IObjectAddedEvent.
    """
    ob = object # better name, keep original function signature
    v = self._checkId(id)
    if v is not None:
        id = v
    t = getattr(ob, 'meta_type', None)

    # If an object by the given id already exists, remove it.
    for object_info in self._objects:
        if object_info['id'] == id:
            self._delObject(id)
            break

    if not suppress_events:
        notify(ObjectWillBeAddedEvent(ob, self, id))

    self._objects = self._objects + ({'id': id, 'meta_type': t},)
    self._setOb(id, ob)
    ob = self._getOb(id)

    if set_owner:
        # TODO: eventify manage_fixupOwnershipAfterAdd
        # This will be called for a copy/clone, or a normal _setObject.
        ob.manage_fixupOwnershipAfterAdd()

    if set_owner:
        # Try to give user the local role "Owner", but only if
        # no local roles have been set on the object yet.
        if getattr(ob, '__ac_local_roles__', _marker) is None:
            user = getSecurityManager().getUser()
            if user is not None:
                userid = user.getId()
                if userid is not None:
                    ob.manage_setLocalRoles(userid, ['Owner'])

    if not suppress_events:
        notify(ObjectAddedEvent(ob, self, id))

    maybeCallDeprecated('manage_afterAdd', ob, self)

    return id


# From BTreeFolder2
def BT_setObject(self, id, object, roles=None, user=None, set_owner=1,
                 suppress_events=False):
    ob = object # better name, keep original function signature
    v = self._checkId(id)
    if v is not None:
        id = v

    # If an object by the given id already exists, remove it.
    if self.has_key(id):
        self._delObject(id)

    if not suppress_events:
        notify(ObjectWillBeAddedEvent(ob, self, id))

    self._setOb(id, ob)
    ob = self._getOb(id)

    if set_owner:
        # TODO: eventify manage_fixupOwnershipAfterAdd
        # This will be called for a copy/clone, or a normal _setObject.
        ob.manage_fixupOwnershipAfterAdd()

    if set_owner:
        # Try to give user the local role "Owner", but only if
        # no local roles have been set on the object yet.
        if getattr(ob, '__ac_local_roles__', _marker) is None:
            user = getSecurityManager().getUser()
            if user is not None:
                userid = user.getId()
                if userid is not None:
                    ob.manage_setLocalRoles(userid, ['Owner'])

    if not suppress_events:
        notify(ObjectAddedEvent(ob, self, id))

    maybeCallDeprecated('manage_afterAdd', ob, self)

    return id


# From ObjectManager
def _delObject(self, id, dp=1, suppress_events=False):
    """Delete an object from this container.

    Also sends IObjectRemovedEvent.
    """
    ob = self._getOb(id)

    maybeCallDeprecated('manage_beforeDelete', ob, self)

    if not suppress_events:
        notify(ObjectWillBeRemovedEvent(ob, self, id))

    self._objects = tuple([i for i in self._objects
                           if i['id'] != id])
    self._delOb(id)

    # Indicate to the object that it has been deleted. This is
    # necessary for object DB mount points. Note that we have to
    # tolerate failure here because the object being deleted could
    # be a Broken object, and it is not possible to set attributes
    # on Broken objects.
    try:
        ob._v__object_deleted__ = 1
    except:
        pass

    if not suppress_events:
        notify(ObjectRemovedEvent(ob, self, id))


# From BTreeFolder2
def BT_delObject(self, id, dp=1, suppress_events=False):
    ob = self._getOb(id)

    maybeCallDeprecated('manage_beforeDelete', ob, self)

    if not suppress_events:
        notify(ObjectWillBeRemovedEvent(ob, self, id))

    self._delOb(id)

    if not suppress_events:
        notify(ObjectRemovedEvent(ob, self, id))

# From CopyContainer
def manage_renameObject(self, id, new_id, REQUEST=None):
    """Rename a particular sub-object.
    """
    try:
        self._checkId(new_id)
    except:
        raise CopyError, MessageDialog(
            title='Invalid Id',
            message=sys.exc_info()[1],
            action ='manage_main')

    ob = self._getOb(id)

    if ob.wl_isLocked():
        raise ResourceLockedError, ('Object "%s" is locked via WebDAV'
                                    % ob.getId())
    if not ob.cb_isMoveable():
        raise CopyError, eNotSupported % escape(id)
    self._verifyObjectPaste(ob)

    try:
        ob._notifyOfCopyTo(self, op=1)
    except ConflictError:
        raise
    except:
        raise CopyError, MessageDialog(
            title="Rename Error",
            message=sys.exc_info()[1],
            action ='manage_main')

    notify(ObjectWillBeMovedEvent(ob, self, id, self, new_id))

    self._delObject(id, suppress_events=True)
    ob = aq_base(ob)
    ob._setId(new_id)

    # Note - because a rename always keeps the same context, we
    # can just leave the ownership info unchanged.
    self._setObject(new_id, ob, set_owner=0, suppress_events=True)
    ob = self._getOb(new_id)

    notify(ObjectMovedEvent(ob, self, id, self, new_id))

    ob._postCopy(self, op=1)

    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)
    return None


# From CopyContainer
def manage_pasteObjects(self, cb_copy_data=None, REQUEST=None):
    """Paste previously copied objects into the current object.

    If calling manage_pasteObjects from python code, pass the result of a
    previous call to manage_cutObjects or manage_copyObjects as the first
    argument.

    Also sends IObjectCopiedEvent or IObjectMovedEvent.
    """
    if cb_copy_data is not None:
        cp = cb_copy_data
    elif REQUEST is not None and REQUEST.has_key('__cp'):
        cp = REQUEST['__cp']
    else:
        cp = None
    if cp is None:
        raise CopyError, eNoData

    try:
        op, mdatas = _cb_decode(cp)
    except:
        raise CopyError, eInvalid

    oblist = []
    app = self.getPhysicalRoot()
    for mdata in mdatas:
        m = Moniker.loadMoniker(mdata)
        try:
            ob = m.bind(app)
        except ConflictError:
            raise
        except:
            raise CopyError, eNotFound
        self._verifyObjectPaste(ob, validate_src=op+1)
        oblist.append(ob)

    result = []
    if op == 0:
        # Copy operation
        for ob in oblist:
            orig_id = ob.getId()
            if not ob.cb_isCopyable():
                raise CopyError, eNotSupported % escape(orig_id)

            try:
                ob._notifyOfCopyTo(self, op=0)
            except ConflictError:
                raise
            except:
                raise CopyError, MessageDialog(
                    title="Copy Error",
                    message=sys.exc_info()[1],
                    action='manage_main')

            id = self._get_id(orig_id)
            result.append({'id': orig_id, 'new_id': id})

            ob = ob._getCopy(self)
            ob._setId(id)
            notify(ObjectCopiedEvent(ob))

            self._setObject(id, ob)
            ob = self._getOb(id)
            ob.wl_clearLocks()

            ob._postCopy(self, op=0)

            maybeCallDeprecated('manage_afterClone', ob)

            notify(FiveObjectClonedEvent(ob))

        if REQUEST is not None:
            return self.manage_main(self, REQUEST, update_menu=1,
                                    cb_dataValid=1)

    elif op == 1:
        # Move operation
        for ob in oblist:
            orig_id = ob.getId()
            if not ob.cb_isMoveable():
                raise CopyError, eNotSupported % escape(orig_id)

            try:
                ob._notifyOfCopyTo(self, op=1)
            except ConflictError:
                raise
            except:
                raise CopyError, MessageDialog(
                    title="Move Error",
                    message=sys.exc_info()[1],
                    action='manage_main')

            if not sanity_check(self, ob):
                raise CopyError, "This object cannot be pasted into itself"

            orig_container = aq_parent(aq_inner(ob))
            if aq_base(orig_container) is aq_base(self):
                id = orig_id
            else:
                id = self._get_id(orig_id)
            result.append({'id': orig_id, 'new_id': id})

            notify(ObjectWillBeMovedEvent(ob, orig_container, orig_id,
                                          self, id))

            # try to make ownership explicit so that it gets carried
            # along to the new location if needed.
            ob.manage_changeOwnershipType(explicit=1)

            orig_container._delObject(orig_id, suppress_events=True)
            ob = aq_base(ob)
            ob._setId(id)

            self._setObject(id, ob, set_owner=0, suppress_events=True)
            ob = self._getOb(id)

            notify(ObjectMovedEvent(ob, orig_container, orig_id, self, id))

            ob._postCopy(self, op=1)
            # try to make ownership implicit if possible
            ob.manage_changeOwnershipType(explicit=0)

        if REQUEST is not None:
            REQUEST['RESPONSE'].setCookie('__cp', 'deleted',
                                path='%s' % cookie_path(REQUEST),
                                expires='Wed, 31-Dec-97 23:59:59 GMT')
            REQUEST['__cp'] = None
            return self.manage_main(self, REQUEST, update_menu=1,
                                    cb_dataValid=0)

    return result

# From CopyContainer
def manage_clone(self, ob, id, REQUEST=None):
    """Clone an object, creating a new object with the given id.
    """
    if not ob.cb_isCopyable():
        raise CopyError, eNotSupported % escape(ob.getId())
    try:
        self._checkId(id)
    except:
        raise CopyError, MessageDialog(
            title='Invalid Id',
            message=sys.exc_info()[1],
            action ='manage_main')

    self._verifyObjectPaste(ob)

    try:
        ob._notifyOfCopyTo(self, op=0)
    except ConflictError:
        raise
    except:
        raise CopyError, MessageDialog(
            title="Clone Error",
            message=sys.exc_info()[1],
            action='manage_main')

    ob = ob._getCopy(self)
    ob._setId(id)
    notify(ObjectCopiedEvent(ob))

    self._setObject(id, ob)
    ob = self._getOb(id)

    ob._postCopy(self, op=0)

    maybeCallDeprecated('manage_afterClone', ob)

    notify(FiveObjectClonedEvent(ob))

    return ob

##################################################
# Fix OFS.Application's creation of some objects.
#
# The application object creates root objects like error_log,
# browser_id_manager, session_data_manager
#
# They all expects their manage_afterAdd to be called, but they are
# created before Five 1.2 is initialized and has had a chance to do its
# patches. So we call manage_afterAddd by hand.
#
# Remove this in Five 1.3, where subscribers and implements()
# will be setup correctly earlier.

def install_errorlog(self):
    app = self.getApp()
    if app._getInitializerFlag('error_log'):
        # do nothing if we've already installed one
        return
    # Install an error_log
    if not hasattr(app, 'error_log'):
        from Products.SiteErrorLog.SiteErrorLog import SiteErrorLog
        error_log = SiteErrorLog()
        app._setObject('error_log', error_log)
        # Added for Five 1.2:
        error_log = app.error_log
        error_log.manage_afterAdd(error_log, app)
        # End added
        app._setInitializerFlag('error_log')
        self.commit('Added site error_log at /error_log')

def install_browser_id_manager(self):
    app = self.getApp()
    if app._getInitializerFlag('browser_id_manager'):
        # do nothing if we've already installed one
        return
    # Ensure that a browser ID manager exists
    if not hasattr(app, 'browser_id_manager'):
        from Products.Sessions.BrowserIdManager import BrowserIdManager
        bid = BrowserIdManager('browser_id_manager', 'Browser Id Manager')
        app._setObject('browser_id_manager', bid)
        # Added for Five 1.2:
        browser_id_manager = app.browser_id_manager
        browser_id_manager.manage_afterAdd(browser_id_manager, app)
        # End added
        app._setInitializerFlag('browser_id_manager')
        self.commit('Added browser_id_manager')

def install_session_data_manager(self):
    app = self.getApp()
    if app._getInitializerFlag('session_data_manager'):
        # do nothing if we've already installed one
        return
    # Ensure that a session data manager exists
    if not hasattr(app, 'session_data_manager'):
        from Products.Sessions.SessionDataManager import SessionDataManager
        sdm = SessionDataManager('session_data_manager',
            title='Session Data Manager',
            path='/temp_folder/session_data',
            requestName='SESSION')
        app._setObject('session_data_manager', sdm)
        # Added for Five 1.2:
        session_data_manager = app.session_data_manager
        session_data_manager.manage_afterAdd(session_data_manager, app)
        # End added
        app._setInitializerFlag('session_data_manager')
        self.commit('Added session_data_manager')

##################################################
# Structured monkey-patching

import Products.Five
from Products.Five import zcml
from Products.Five.fiveconfigure import killMonkey
from zope.testing.cleanup import addCleanUp

_monkied = []

from OFS.SimpleItem import Item
from OFS.ObjectManager import ObjectManager
from OFS.CopySupport import CopyContainer
from OFS.OrderSupport import OrderSupport
from Products.BTreeFolder2.BTreeFolder2 import BTreeFolder2Base
from OFS.Application import AppInitializer
from Products.ZCatalog import CatalogAwareness, CatalogPathAwareness

def doMonkies(transitional, register_cleanup=True):
    """Monkey patch various methods to provide container events.
    """
    global hasContainerEvents
    hasContainerEvents = True

    patchMethod(ObjectManager, '_setObject',
                _setObject)
    patchMethod(ObjectManager, '_delObject',
                _delObject)
    patchMethod(ObjectManager, 'manage_afterAdd',
                manage_afterAdd)
    patchMethod(ObjectManager, 'manage_beforeDelete',
                manage_beforeDelete)
    patchMethod(ObjectManager, 'manage_afterClone',
                manage_afterClone)

    patchMethod(Item, 'manage_afterAdd',
                manage_afterAdd)
    patchMethod(Item, 'manage_beforeDelete',
                manage_beforeDelete)
    patchMethod(Item, 'manage_afterClone',
                manage_afterClone)

    patchMethod(BTreeFolder2Base, '_setObject',
                BT_setObject)
    patchMethod(BTreeFolder2Base, '_delObject',
                BT_delObject)

    patchMethod(CopyContainer, 'manage_renameObject',
                manage_renameObject)
    patchMethod(CopyContainer, 'manage_pasteObjects',
                manage_pasteObjects)
    patchMethod(CopyContainer, 'manage_clone',
                manage_clone)

    patchMethod(OrderSupport, '_old_manage_renameObject',
                manage_renameObject)

    patchMethod(AppInitializer, 'install_errorlog',
                install_errorlog)
    patchMethod(AppInitializer, 'install_browser_id_manager',
                install_browser_id_manager)
    patchMethod(AppInitializer, 'install_session_data_manager',
                install_session_data_manager)

    patchMethod(CatalogAwareness.CatalogAware, 'manage_afterAdd',
                CA_manage_afterAdd)
    patchMethod(CatalogAwareness.CatalogAware, 'manage_beforeDelete',
                CA_manage_beforeDelete)
    patchMethod(CatalogAwareness.CatalogAware, 'manage_afterClone',
                CA_manage_afterClone)
    patchMethod(CatalogPathAwareness.CatalogAware, 'manage_afterAdd',
                CA_manage_afterAdd)
    patchMethod(CatalogPathAwareness.CatalogAware, 'manage_beforeDelete',
                CA_manage_beforeDelete)
    patchMethod(CatalogPathAwareness.CatalogAware, 'manage_afterClone',
                CA_manage_afterClone)

    # XXX remove this for Five 1.3, and put it in configure.zcml
    zcml.load_config('event.zcml', Products.Five)

    if register_cleanup:
        addCleanUp(undoMonkies)

def patchMethod(class_, name, new_method):
    method = getattr(class_, name, None)
    if isFiveMethod(method):
        return
    setattr(class_, FIVE_ORIGINAL_PREFIX + name, method)
    setattr(class_, name, new_method)
    new_method.__five_method__ = True
    _monkied.append((class_, name))

def undoMonkies():
    """Undo monkey patches.
    """
    global hasContainerEvents
    for class_, name in _monkied:
        killMonkey(class_, name, FIVE_ORIGINAL_PREFIX + name)
    hasContainerEvents = False
    deprecatedManageAddDeleteClasses[:] = []

##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Base class for object managers which can be "skinned".

Skinnable object managers inherit attributes from a skin specified in
the browser request.  Skins are stored in a fixed-name subobject.

$Id$
"""

import logging
from thread import get_ident
from warnings import warn

from AccessControl.SecurityInfo import ClassSecurityInfo
from AccessControl.ZopeGuards import guard, guarded_getattr
from AccessControl.SecurityManagement import getSecurityManager
from AccessControl.unauthorized import Unauthorized
from Acquisition import Acquired
from Acquisition import aq_acquire
from Acquisition import aq_base
from Acquisition import aq_inner
from Acquisition import aq_parent
from OFS.interfaces import ITraversable
from zExceptions import NotFound

from Acquisition import aq_base
from App.class_init import InitializeClass
from OFS.ObjectManager import ObjectManager
from ZODB.POSException import ConflictError
from zope.interface import implements
from zope.traversing.interfaces import TraversalError
from zope.traversing.namespace import namespaceLookup
from zope.traversing.namespace import nsParse
from Acquisition.interfaces import IAcquirer
from zope.interface import Interface
from zope.component import queryMultiAdapter
from interfaces import ISkinnableObjectManager

logger = logging.getLogger('CMFCore.Skinnable')


_MARKER = object()  # Create a new marker object.


SKINDATA = {} # mapping thread-id -> (skinobj, skinname, ignore, resolve)

class SkinDataCleanup:
    """Cleanup at the end of the request."""
    def __init__(self, tid):
        self.tid = tid
    def __del__(self):
        tid = self.tid
        # Be extra careful in __del__
        if SKINDATA is not None:
            if SKINDATA.has_key(tid):
                del SKINDATA[tid]


class SkinnableObjectManager(ObjectManager):

    security = ClassSecurityInfo()
    
    implements(ISkinnableObjectManager)

    security.declarePrivate('getSkinsFolderName')
    def getSkinsFolderName(self):
        # Not implemented.
        return None

    def __getattr__(self, name):
        '''
        Looks for the name in an object with wrappers that only reach
        up to the root skins folder.

        This should be fast, flexible, and predictable.
        '''
        if not name.startswith('_') and not name.startswith('aq_'):
            sd = SKINDATA.get(get_ident())
            if sd is not None:
                ob, skinname, ignore, resolve = sd
                if not name in ignore:
                    if name in resolve:
                        return resolve[name]
                    subob = getattr(ob, name, _MARKER)
                    if subob is not _MARKER:
                        # Return it in context of self, forgetting
                        # its location and acting as if it were located
                        # in self.
                        retval = aq_base(subob)
                        resolve[name] = retval
                        return retval
                    else:
                        ignore[name] = 1
        raise AttributeError, name

    security.declarePrivate('getSkin')
    def getSkin(self, name=None):
        """Returns the requested skin.
        """
        skinob = None
        sfn = self.getSkinsFolderName()

        if sfn is not None:
            sf = getattr(self, sfn, None)
            if sf is not None:
               if name is not None:
                   skinob = sf.getSkinByName(name)
               if skinob is None:
                   skinob = sf.getSkinByName(sf.getDefaultSkin())
                   if skinob is None:
                       skinob = sf.getSkinByPath('')
        return skinob

    security.declarePublic('getSkinNameFromRequest')
    def getSkinNameFromRequest(self, REQUEST=None):
        '''Returns the skin name from the Request.'''
        if REQUEST is None:
            return None
        sfn = self.getSkinsFolderName()
        if sfn is not None:
            sf = getattr(self, sfn, None)
            if sf is not None:
                return REQUEST.get(sf.getRequestVarname(), None)

    security.declarePublic('changeSkin')
    def changeSkin(self, skinname, REQUEST=_MARKER):
        '''Change the current skin.

        Can be called manually, allowing the user to change
        skins in the middle of a request.
        '''
        skinobj = self.getSkin(skinname)
        if skinobj is not None:
            tid = get_ident()
            SKINDATA[tid] = (skinobj, skinname, {}, {})
            if REQUEST is _MARKER:
                REQUEST = getattr(self, 'REQUEST', None)
                warn("changeSkin should be called with 'REQUEST' as second "
                     "argument. The BBB code will be removed in CMF 2.3.",
                     DeprecationWarning, stacklevel=2)
            if REQUEST is not None:
                REQUEST._hold(SkinDataCleanup(tid))

    security.declarePublic('getCurrentSkinName')
    def getCurrentSkinName(self):
        '''Return the current skin name.
        '''
        sd = SKINDATA.get(get_ident())
        if sd is not None:
            ob, skinname, ignore, resolve = sd
            if skinname is not None:
                return skinname
        # nothing here, so assume the default skin
        sfn = self.getSkinsFolderName()
        if sfn is not None:
            sf = getattr(self, sfn, None)
            if sf is not None:
                return sf.getDefaultSkin()
        # and if that fails...
        return None

    security.declarePublic('clearCurrentSkin')
    def clearCurrentSkin(self):
        """Clear the current skin."""
        tid = get_ident()
        if SKINDATA.has_key(tid):
            del SKINDATA[tid]

    security.declarePublic('setupCurrentSkin')
    def setupCurrentSkin(self, REQUEST=_MARKER):
        '''
        Sets up skindata so that __getattr__ can find it.

        Can NOT be called manually to change skins in the middle of a
        request! Use changeSkin for that.
        '''
        if REQUEST is _MARKER:
            REQUEST = getattr(self, 'REQUEST', None)
            warn("setupCurrentSkin should be called with 'REQUEST' as "
                 "argument. The BBB code will be removed in CMF 2.3.",
                 DeprecationWarning, stacklevel=2)
        if REQUEST is None:
            # self is not fully wrapped at the moment.  Don't
            # change anything.
            return
        if SKINDATA.has_key(get_ident()):
            # Already set up for this request.
            return
        skinname = self.getSkinNameFromRequest(REQUEST)
        try:
            self.changeSkin(skinname, REQUEST)
        except ConflictError:
            raise
        except:
            # This shouldn't happen, even if the requested skin
            # does not exist.
            logger.exception("Unable to setupCurrentSkin()")

    def _checkId(self, id, allow_dup=0):
        '''
        Override of ObjectManager._checkId().

        Allows the user to create objects with IDs that match the ID of
        a skin object.
        '''
        superCheckId = SkinnableObjectManager.inheritedAttribute('_checkId')
        if not allow_dup:
            # Temporarily disable skindata.
            # Note that this depends heavily on Zope's current thread
            # behavior.
            tid = get_ident()
            sd = SKINDATA.get(tid)
            if sd is not None:
                del SKINDATA[tid]
            try:
                base = getattr(self,  'aq_base', self)
                if not hasattr(base, id):
                    # Cause _checkId to not check for duplication.
                    return superCheckId(self, id, allow_dup=1)
            finally:
                if sd is not None:
                    SKINDATA[tid] = sd
        return superCheckId(self, id, allow_dup)

    def unrestrictedTraverse(self, path, default=_MARKER, restricted=False):
        """Lookup an object by path.

        path -- The path to the object. May be a sequence of strings or a slash
        separated string. If the path begins with an empty path element
        (i.e., an empty string or a slash) then the lookup is performed
        from the application root. Otherwise, the lookup is relative to
        self. Two dots (..) as a path element indicates an upward traversal
        to the acquisition parent.

        default -- If provided, this is the value returned if the path cannot
        be traversed for any reason (i.e., no object exists at that path or
        the object is inaccessible).

        restricted -- If false (default) then no security checking is performed.
        If true, then all of the objects along the path are validated with
        the security machinery. Usually invoked using restrictedTraverse().
        """
        from webdav.NullResource import NullResource
        if not path:
            return self

        next = None

        if isinstance(path, str):
            # Unicode paths are not allowed
            path = path.split('/')
        else:
            path = list(path)

        REQUEST = {'TraversalRequestNameStack': path}
        path.reverse()
        path_pop = path.pop

        if len(path) > 1 and not path[0]:
            # Remove trailing slash
            path_pop(0)

        if restricted:
            validate = getSecurityManager().validate

        if not path[-1]:
            # If the path starts with an empty string, go to the root first.
            path_pop()
            obj = self.getPhysicalRoot()
            if restricted:
                validate(None, None, None, obj) # may raise Unauthorized
        else:
            obj = self

        resource = _MARKER
        try:
            while path:
                name = path_pop()
                __traceback_info__ = path, name

                if name[0] == '_':
                    # Never allowed in a URL.
                    raise NotFound, name

                if name == '..':
                    next = aq_parent(obj)
                    if next is not None:
                        if restricted and not validate(obj, obj, name, next):
                            raise Unauthorized(name)
                        obj = next
                        continue

                bobo_traverse = getattr(obj, '__bobo_traverse__', None)
                try:
                    if name and name[:1] in '@+' and name != '+' and nsParse(name)[1]:
                        # Process URI segment parameters.
                        ns, nm = nsParse(name)
                        try:
                            next = namespaceLookup(
                                ns, nm, obj, aq_acquire(self, 'REQUEST'))
                            if IAcquirer.providedBy(next):
                                next = next.__of__(obj)
                            if restricted and not validate(
                                obj, obj, name, next):
                                raise Unauthorized(name)
                        except TraversalError:
                            raise AttributeError(name)

                    elif bobo_traverse is not None:
                        next = bobo_traverse(REQUEST, name)
                        if restricted:
                            if aq_base(next) is not next:
                                # The object is wrapped, so the acquisition
                                # context is the container.
                                container = aq_parent(aq_inner(next))
                            elif getattr(next, 'im_self', None) is not None:
                                # Bound method, the bound instance
                                # is the container
                                container = next.im_self
                            elif getattr(aq_base(obj), name, _MARKER) is next:
                                # Unwrapped direct attribute of the object so
                                # object is the container
                                container = obj
                            else:
                                # Can't determine container
                                container = None
                            # If next is a simple unwrapped property, its
                            # parentage is indeterminate, but it may have
                            # been acquired safely. In this case validate
                            # will raise an error, and we can explicitly
                            # check that our value was acquired safely.
                            try:
                                ok = validate(obj, container, name, next)
                            except Unauthorized:
                                ok = False
                            if not ok:
                                if (container is not None or
                                    guarded_getattr(obj, name, _MARKER)
                                        is not next):
                                    raise Unauthorized(name)
                    else:
                        try:
                            next = obj.__getattribute__(name)
                        except AttributeError:
                            # this is not a direct object
                            pass
                        else:
                            try:
                                next = next.aq_base.__of__(obj)
                            except (AttributeError, TypeError):
                                pass # We can't aq wrap whatever this is
                            if restricted:
                                guard(obj, next)
                        if next is None:
                            # Go to the case below which handles views and 
                            # acquired attributes.
                            raise NotFound(name)

                except (AttributeError, NotFound, KeyError), e:
                    # Try to look for a view
                    next = queryMultiAdapter((obj, aq_acquire(self, 'REQUEST')),
                                             Interface, name)

                    if next is not None:
                        if IAcquirer.providedBy(next):
                            next = next.__of__(obj)
                        if restricted and not validate(obj, obj, name, next):
                            raise Unauthorized(name)
                    elif bobo_traverse is not None:
                        # Attribute lookup should not be done after
                        # __bobo_traverse__:
                        raise e
                    else:
                        # No view, try acquired attributes
                        try:
                            if restricted:
                                next = guarded_getattr(obj, name, _MARKER)
                            else:
                                next = getattr(obj, name, _MARKER)
                        except AttributeError:
                            raise e
                        if next is None:
                            # If we have a NullResource from earlier use it.
                            next = resource
                            if next is _MARKER:
                                # Nothing found re-raise error
                                raise e
                        if next is None:
                            try:
                                next = obj[name]
                                # The item lookup may return a NullResource,
                                # if this is the case we save it and return it
                                # if all other lookups fail.
                                if isinstance(next, NullResource):
                                    resource = next
                                    raise KeyError(name)
                            except AttributeError:
                                # Raise NotFound for easier debugging
                                # instead of AttributeError: __getitem__
                                raise NotFound(name)
                            if restricted and not validate(
                                obj, obj, None, next):
                                raise Unauthorized(name)

                obj = next

            return obj

        except ConflictError:
            raise
        except:
            if default is not _MARKER:
                return default
            else:
                raise

InitializeClass(SkinnableObjectManager)

##############################################################################
#
# Copyright (c) 2000-2003 Zope Corporation and Contributors.
# Copyright (c) 2004 Five Contributors.
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
"""Five interfaces

$Id$
"""
from zope.interface import Interface, Attribute
from zope.schema import Bool, BytesLine, Tuple

class IManageable(Interface):
    """Something that is manageable in the ZMI"""

    def manage(URL1):
	"""Show management screen"""

    def manage_afterAdd(item, container):
	"""Gets called after being added to a container"""

    def manage_beforeDelete(item, container):
	"""Gets called before being deleted"""

    def manage_afterClone(item):
	"""Gets called after being cloned"""

    def manage_editedDialog(REQUEST, **args):
	"""Show an 'edited' dialog"""

    def filtered_manage_options(REQUEST=None):
	""" """

    def manage_workspace():
        """Dispatch to first interface in manage_options"""

    def tabs_path_default(REQUEST):
	""" """

    def tabs_path_info(script, path,):
	""" """

    def class_manage_path(self):
	""" """

    manage_options = Tuple(
	title=u"Manage options",
	)

    manage_tabs = Attribute("""Management tabs""")

class IFTPAccess(Interface):
    """Provide support for FTP access"""

    def manage_FTPstat(REQUEST):
	"""FTP stat, used for directory listings"""

    def manage_FTPlist(REQUEST):
        """Directory listing for FTP. In the case of non-Foldoid objects, the
        listing should contain one object, the object itself."""

    def manage_FTPget(REQUEST):
	"""Send data to FTP clients"""

class IWriteLock(Interface):
    """This represents the basic protocol needed to support the write lock
    machinery.

    It must be able to answer the questions:

     o Is the object locked?

     o Is the lock owned by the current user?

     o What lock tokens are associated with the current object?

     o What is their state (how long until they're supposed to time out?,
       what is their depth?  what type are they?

    And it must be able to do the following:

     o Grant a write lock on the object to a specified user.

       - *If lock depth is infinite, this must also grant locks on **all**
         subobjects, or fail altogether*

     o Revoke a lock on the object.

       - *If lock depth is infinite, this must also revoke locks on all
         subobjects*

    **All methods in the WriteLock interface that deal with checking valid
    locks MUST check the timeout values on the lockitem (ie, by calling
    'lockitem.isValid()'), and DELETE the lock if it is no longer valid**
    """

    def wl_lockItems(killinvalids=0):
        """ Returns (key, value) pairs of locktoken, lock.

        if 'killinvalids' is true, invalid locks (locks whose timeout
        has been exceeded) will be deleted"""

    def wl_lockValues(killinvalids=0):
        """ Returns a sequence of locks.  if 'killinvalids' is true,
        invalid locks will be deleted"""

    def wl_lockTokens(killinvalids=0):
        """ Returns a sequence of lock tokens.  if 'killinvalids' is true,
        invalid locks will be deleted"""

    def wl_hasLock(token, killinvalids=0):
        """ Returns true if the lock identified by the token is attached
        to the object. """

    def wl_isLocked():
        """ Returns true if 'self' is locked at all.  If invalid locks
        still exist, they should be deleted."""

    def wl_setLock(locktoken, lock):
        """ Store the LockItem, 'lock'.  The locktoken will be used to fetch
        and delete the lock.  If the lock exists, this MUST
        overwrite it if all of the values except for the 'timeout' on the
        old and new lock are the same. """

    def wl_getLock(locktoken):
        """ Returns the locktoken identified by the locktokenuri """

    def wl_delLock(locktoken):
        """ Deletes the locktoken identified by the locktokenuri """

    def wl_clearLocks():
        """ Deletes ALL DAV locks on the object - should only be called
        by lock management machinery. """

class IDAVResource(IWriteLock):
    """Provide basic WebDAV support for non-collection objects."""

    __dav_resource__ = Bool(
	title=u"Is DAV resource"
	)

    __http_methods__ = Tuple(
	title=u"HTTP methods",
	description=u"Sequence of valid HTTP methods"
	)

    def dav__init(request, response):
	"""
        Init expected HTTP 1.1 / WebDAV headers which are not
        currently set by the base response object automagically.
        
        Note we set an borg-specific header for ie5 :( Also, we sniff
        for a ZServer response object, because we don't want to write
        duplicate headers (since ZS writes Date and Connection
        itself)."""

    def dav__validate(object, methodname, REQUEST):
	""" """

    def dav__simpleifhandler(request, response, method='PUT',
                             col=0, url=None, refresh=0):
	""" """

    def HEAD(EQUEST, RESPONSE):
        """Retrieve resource information without a response body."""

    def PUT(REQUEST, RESPONSE):
        """Replace the GET response entity of an existing resource.
        Because this is often object-dependent, objects which handle
        PUT should override the default PUT implementation with an
        object-specific implementation. By default, PUT requests
        fail with a 405 (Method Not Allowed)."""

    def OPTIONS(REQUEST, RESPONSE):
        """Retrieve communication options."""

    def TRACE(REQUEST, RESPONSE):
        """Return the HTTP message received back to the client as the
        entity-body of a 200 (OK) response. This will often usually
        be intercepted by the web server in use. If not, the TRACE
        request will fail with a 405 (Method Not Allowed), since it
        is not often possible to reproduce the HTTP request verbatim
        from within the Zope environment."""

    def DELETE(REQUEST, RESPONSE):
        """Delete a resource. For non-collection resources, DELETE may
        return either 200 or 204 (No Content) to indicate success."""

    def PROPFIND(REQUEST, RESPONSE):
        """Retrieve properties defined on the resource."""

    def PROPPATCH(self, REQUEST, RESPONSE):
        """Set and/or remove properties defined on the resource."""

    def MKCOL(REQUEST, RESPONSE):
        """Create a new collection resource. If called on an existing
        resource, MKCOL must fail with 405 (Method Not Allowed)."""

    def COPY(REQUEST, RESPONSE):
        """Create a duplicate of the source resource whose state
        and behavior match that of the source resource as closely
        as possible. Though we may later try to make a copy appear
        seamless across namespaces (e.g. from Zope to Apache), COPY
        is currently only supported within the Zope namespace."""

    def MOVE(REQUEST, RESPONSE):
        """Move a resource to a new location. Though we may later try to
        make a move appear seamless across namespaces (e.g. from Zope
        to Apache), MOVE is currently only supported within the Zope
        namespace."""

    def LOCK(REQUEST, RESPONSE):
        """Lock a resource"""

    def UNLOCK(REQUEST, RESPONSE):
        """Remove an existing lock on a resource."""

    def manage_DAVget():
        """Gets the document source"""

    def listDAVObjects():
	""" """

class ICopySource(Interface):
    """Interface for objects which allow themselves to be copied."""

    def _canCopy(op=0):
        """Called to make sure this object is copyable. The op var
        is 0 for a copy, 1 for a move."""

    def _notifyOfCopyTo(container, op=0):
        """Overide this to be pickly about where you go! If you dont
        want to go there, raise an exception. The op variable is
        0 for a copy, 1 for a move."""

    def _getCopy(container):
	"""
        Commit a subtransaction to:
        1) Make sure the data about to be exported is current
        2) Ensure self._p_jar and container._p_jar are set even if
           either one is a new object
        """

    def _postCopy(self, container, op=0):
	"""Called after the copy is finished to accomodate special cases.
	The op var is 0 for a copy, 1 for a move."""

    def _setId(self, id):
        """Called to set the new id of a copied object."""

    def cb_isCopyable(self):
        """Is object copyable? Returns 0 or 1"""

    def cb_isMoveable(self):
        """Is object moveable? Returns 0 or 1"""

    def cb_userHasCopyOrMovePermission(self):
	""" """

class ITraversable(Interface):

    def absolute_url(relative=0):
        """Return the absolute URL of the object.

        This a canonical URL based on the object's physical
        containment path.  It is affected by the virtual host
        configuration, if any, and can be used by external
        agents, such as a browser, to address the object.

        If the relative argument is provided, with a true value, then
        the value of virtual_url_path() is returned.

        Some Products incorrectly use '/'+absolute_url(1) as an
        absolute-path reference.  This breaks in certain virtual
        hosting situations, and should be changed to use
        absolute_url_path() instead.
        """

    def absolute_url_path():
        """Return the path portion of the absolute URL of the object.

        This includes the leading slash, and can be used as an
        'absolute-path reference' as defined in RFC 2396.
        """

    def virtual_url_path():
        """Return a URL for the object, relative to the site root.

        If a virtual host is configured, the URL is a path relative to
        the virtual host's root object.  Otherwise, it is the physical
        path.  In either case, the URL does not begin with a slash.
        """

    def getPhysicalPath():
        '''Returns a path (an immutable sequence of strings)
        that can be used to access this object again
        later, for example in a copy/paste operation.  getPhysicalRoot()
        and getPhysicalPath() are designed to operate together.
        '''

    def unrestrictedTraverse(path, default=None, restricted=0):
        """Lookup an object by path,
        
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

    def restrictedTraverse(path, default=None):
        """Trusted code traversal code, always enforces security"""

class IOwned(Interface):

    manage_owner = Attribute("""Manage owner view""")

    def owner_info():
        """Get ownership info for display"""

    def getOwner(info=0):
        """Get the owner

        If a true argument is provided, then only the owner path and id are
        returned. Otherwise, the owner object is returned.
        """

    def getOwnerTuple():
        """Return a tuple, (userdb_path, user_id) for the owner.

        o Ownership can be acquired, but only from the containment path.

        o If unowned, return None.
        """

    def getWrappedOwner():
        """Get the owner, modestly wrapped in the user folder.

        o If the object is not owned, return None.

        o If the owner's user database doesn't exist, return Nobody.

        o If the owner ID does not exist in the user database, return Nobody.
        """

    def changeOwnership(user, recursive=0):
        """Change the ownership to the given user.  If 'recursive' is
        true then also take ownership of all sub-objects, otherwise
        sub-objects retain their ownership information."""

    def userCanTakeOwnership(self):
	""" """

    def manage_takeOwnership(REQUEST, RESPONSE, recursive=0):
        """Take ownership (responsibility) for an object. If 'recursive'
        is true, then also take ownership of all sub-objects.
        """

    def manage_changeOwnershipType(explicit=1, RESPONSE=None, REQUEST=None):
        """Change the type (implicit or explicit) of ownership.
        """

    def _deleteOwnershipAfterAdd(self):
	""" """

    def manage_fixupOwnershipAfterAdd(self):
	""" """

class IUndoSupport(Interface):

    manage_UndoForm = Attribute("""Manage Undo form""")

    def get_request_var_or_attr(name, default):
	""" """

    def undoable_transactions(first_transaction=None,
                              last_transaction=None,
                              PrincipiaUndoBatchSize=None):
	""" """

    def manage_undo_transactions(transaction_info=(), REQUEST=None):
        """ """

class IRoleManager(Interface):
    """XXX"""

class ISimpleItem(IManageable, IFTPAccess, IDAVResource, ICopySource,
		  ITraversable, IOwned, IUndoSupport, IRoleManager):
    """Not-so-simple item"""

    __name__ = BytesLine(
	title=u"Name"
	)

    isPrincipiaFolderish = Bool(
	title=u"Is a folderish object",
	description=u"Should be false for simple items",
	)

    title = BytesLine(
	title=u"Title"
	)

    meta_type = BytesLine(
	title=u"Meta type",
	description=u"The object's Zope2 meta type",
	)

    icon = BytesLine(
	title=u"Icon",
	description=u"Name of icon, relative to SOFTWARE_URL",
	)

    def getId():
        """Return the id of the object as a string.

        This method should be used in preference to accessing an id
        attribute of an object directly. The getId method is public.
        """

    def _setId(id):
	"""Set the id"""

    def title_or_id():
        """Returns the title if it is not blank and the id otherwise."""

    def title_and_id():
	"""Returns the title if it is not blank and the id otherwise.  If the
        title is not blank, then the id is included in parens."""

    def raise_standardErrorMessage(client=None, REQUEST={},
				   error_type=None, error_value=None, tb=None,
				   error_tb=None, error_message='',
				   tagSearch=None, error_log_url=''):
	"""Raise standard error message"""

    def getPhysicalPath():
        """Returns a path (an immutable sequence of strings) that can be used
        to access this object again later, for example in a copy/paste
        operation."""

class ICopyContainer(Interface):
    """XXX"""

class IObjectManager(ICopyContainer): #XXX more
    """XXX
    """

class IPersistentExtra(Interface):

    def bobobase_modification_time():
	""" """

    def locked_in_version():
        """Was the object modified in any version?"""

    def modified_in_version():
        """Was the object modified in this version?"""

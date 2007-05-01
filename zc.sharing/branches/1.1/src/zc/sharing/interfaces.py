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
"""Z4I Security Policy (Sharing) APIs.

$Id$
"""

from zope import interface, schema
import zope.annotation.interfaces
import zope.lifecycleevent.interfaces
import zope.lifecycleevent

class ISharable(zope.annotation.interfaces.IAttributeAnnotatable):
    """Sharable content

    Sharable can be adapted to ISharing.
    """

class IBaseSharing(ISharable):

    def getPrincipals():
        """Return the principal ids for the principals that have privileges

        The return value is an iterable.
        """

    def getBinaryPrivileges(principal_id):
        """Get the principal's privileges

        An integer privileges value is returned.
        """

    def setBinaryPrivileges(principal_id, privileges):
        """Set the principal's privileges to the privileges passed

        The privileges argument is an integer.
        """

    def sharedTo(id, principal_ids):
        """Test whether the collection of principals have a privilege.
        
        privileges are identified with a bit position

        Return a boolean value indicating whether the privilege has been
        shared to any of the principals given by the principal_ids.

        The principal_ids argument is an iterable of principal ids.
        """

class ISharing(IBaseSharing):

    def removeBinaryPrivileges(principal_id, mask):
        "Remove the privileges in the bit mask for principal_id"

    def addBinaryPrivileges(principal_id, mask):
        "Add the privileges in the bit mask for principal_id"
    
    def getIdPrivilege(principal_id, id):
        """Test whether the privilege is shared to a principal

        Return a boolean value indicating whether the privilege has been
        shared to the principal_id.
        """

    def setIdPrivilege(principal_id, id, value):
        """set the privilege for the principal.
        
        Leaves all other privileges alone.
        """

    def getIdPrivileges(principal_id):
        """Return a sequence of the bit positions for the given principal
        """

    def setIdPrivileges(principal_id, ids):
        "Set the principals privileges to those specified by the bit positions"

    def addIdPrivileges(principal_id, ids):
        """Add privileges, specified by bit positions, for principal.  
        
        If principal already has privilege, it is silently ignored"""

    def removeIdPrivileges(principal_id, ids):
        """Remove privileges, specified by bit positions, for principal.  
        
        If principal already does not have privilege, it is silently ignored
        """

    def getPrivilege(principal_id, title):
        """Test whether the privilege is shared to a principal

        Return a boolean value indicating whether the privilege has been
        shared to the principal_id.
        """

    def setPrivilege(principal_id, title, value):
        """set the privilege for the principal.
        
        Leaves all other privileges alone.
        """

    def getPrivileges(principal_id):
        "Return a sequence of the sharing titles for the principal_id"

    def setPrivileges(principal_id, titles):
        "Set the principals privileges to those specified by the titles"

    def addPrivileges(principal_id, titles):
        """Add privileges, specified by titles, for principal.
        
        If principal already has privilege, it is silently ignored"""

    def removePrivileges(principal_id, titles):
        """Remove privileges, specified by titles, for principal.
        
        If principal already does not have privilege, it is silently ignored
        """

class ISharingPrivileges(interface.Interface):

    privileges = schema.Tuple(
        title=u"Ids of privileges used by a content type",
        value_type=schema.Int(),
        )

class ISubobjectSharingPrivileges(interface.Interface):

    subobjectPrivileges = schema.Tuple(
        title=u"Ids of privileges used by subobjects of a content type",
        value_type=schema.Int(),
        )

class IInitialSharing(interface.Interface):
    """Adapter to set sharing for newly added objects
    """

    def share():
        """Set the initial sharing for a sharable object
        """

class ISharingMacro(interface.Interface):
    """Sharing macros provide pluggable rules for creating sharing settings.

    They are registered as named adapters for a context and a request.
    """

    def share(sharing):
        """Modify the settings for a sharing object.
        
        Return a boolean True if the macro changed sharing, False otherwise.
        """

    order = schema.Int(title=u"Order in which item should be displayed")

    title = schema.TextLine(title=u'title', description=
        u'''The display title of the sharing macro.
        Will typically be a zope.i18n.Message.  If None, the registered
        adapter name will be used.''', required=False)

class ISharingEvent(zope.lifecycleevent.interfaces.IObjectModifiedEvent):
    "An event fired by the sharing package"

class ISharingChanged(ISharingEvent):
    """Sharing settings were changed for an object
    """

    principal_id = schema.TextLine(
        title=u"The id of the principal who's sharing has changed",
        )

    old = schema.Int(title=u"Old settings")

    new = schema.Int(title=u"Old settings")

class SharingChanged(zope.lifecycleevent.ObjectModifiedEvent):

    interface.implements(ISharingChanged)

    def __init__(self, object, principal_id, old, new):
        zope.lifecycleevent.ObjectModifiedEvent.__init__(self, object)
        self.principal_id = principal_id
        self.old = old
        self.new = new

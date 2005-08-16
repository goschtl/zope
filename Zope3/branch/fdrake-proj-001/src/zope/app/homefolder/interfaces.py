##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Home Folder Interfaces

$Id$
"""
__docformat__ = "reStructuredText"

from zope.interface import Interface
from zope.schema import Field, Bool, Choice
from zope.app.i18n import ZopeMessageIDFactory as _

class IHomeFolder(Interface):
    """Describes the home directory of a principal."""

    homeFolder = Field(
        title=_("Home Folder"),
        description=_("The principal's home folder; if none has been "
                      "defined, this attribute will be `None`."))


class IHomeFolderManager(Interface):
    """Home Folder Manager

    This utility manages the assignments of home folders to principals. It
    will create and expect all 
    """

    homeFolderBase = Field(
        title=_("Base Folder"),
        description=_("The Base Folder for the Principal Home Folder."),
        required=True)

    createHomeFolder = Bool(
        title=_("Create Home Folder"),
        description=_("Whether home folders should be created upon adding a assignment, if missing."),
        required=True,
        default=True)
        
    autoCreateAssignment = Bool(
        title=_("Auto create assignment"),
        description=_("Whether assignment and folder should be created when "
                      "calling getHomeFolder, if not existing."),
        required=True,
        default=False)
            
    homeFolderRole = Choice(
        title=_("Local Home Folder Role"),
        description=_("The local role that the user will have in "
                      "its home folder. This role is only set on folders "
                      "that are created by the manager."),
        vocabulary="Role Ids",
        default=u'zope.Manager'
        )

    def assignHomeFolder(principalId, folderName=None, create=None):
        """Assigns a particular folder as the home folder of a principal.

        If the `folderName` is `None`, then the principal id will be used as
        the folder name.

        If `createHomeFolder` or `create` is set to `True`, the method is also
        responsible for creating the folder. During creation, the principal
        should get manager rights inside the folder. If `create` is
        specifically set to `False`, then the folder is never created even if
        `createHomeFolder` is `True`.
        """

    def unassignHomeFolder(principalId, delete=False):
        """Remove a home folder assignment.
        
        If `delete` is `True`, then delete the home folder including all of
        its content.
        """

    def getHomeFolder(principalId):
        """Get the home folder instance of the specified principal.

        If a assignment does not exist and `autoCreateAssignment` is set to
        `True`, then create the assignment and the homefolder. The homefolder 
        will always be created regardless of the value of createHomeFolder.
        The folder will be given the same name like the principalId.
        
        During creation, the principal should get the rights specified in 
        homeFolderRole inside the folder.

        If the home folder does not exist and `autoCreateAssignment` is set to
        `False`, then return `None`.
        """

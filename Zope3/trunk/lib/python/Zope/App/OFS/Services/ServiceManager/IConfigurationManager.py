##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""
$Id: IConfigurationManager.py,v 1.4 2002/12/12 11:32:32 mgedmin Exp $
"""

from Zope.App.OFS.Container.IContainer  import IContainerNamesContainer
from Interface import Interface

class IOrderedContainer(Interface):
    """Container with items that can be rearranged.
    """

    # Yes, maybe this should be in the container package, but, we are
    # likely to come up with a better general ordering interface, so
    # we'll leave this one here for now.

    def moveTop(names):
        """Move the objects corresponding to the given names to the top
        """

    def moveUp(names):
        """Move the objects corresponding to the given names up
        """

    def moveBottom(names):
        """Move the objects corresponding to the given names to the bottom
        """

    def moveDown(names):
        """Move the objects corresponding to the given names down
        """

class IConfigurationManager(IContainerNamesContainer, IOrderedContainer):
    """Manage Configurations
    """

__doc__ = IConfigurationManager.__doc__ + __doc__


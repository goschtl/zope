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
$Id: IConfigurationManager.py,v 1.2 2002/11/30 18:39:16 jim Exp $
"""

from Zope.App.OFS.Container.IContainer  import IContainerNamesContainer

class IConfigurationManager(IContainerNamesContainer):
    """Manage Configuration Directives
    """

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

__doc__ = IConfigurationManager.__doc__ + __doc__


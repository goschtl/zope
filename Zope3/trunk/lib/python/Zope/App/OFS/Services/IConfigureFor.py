##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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

$Id: IConfigureFor.py,v 1.2 2002/11/30 18:35:55 jim Exp $
"""

from Interface import Interface

class IConfigureFor(Interface):
    """Services that configure component for interfaces

    This interface is used to find out if there is configuration for a given
    interface.

    Services that implements this interface must provide a view named "ConfigurationFor"
    that displays the configuration for a given interface. For browser views the interface
    will be given in a form variable named "forInterface".
    """
    def hasConfigurationFor(interface):
        """Check for configuration information
        
        Return a Boolean indicating wether there is configuration information for
        the given interface.
        """
    
    

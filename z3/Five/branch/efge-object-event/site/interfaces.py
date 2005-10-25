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
"""Five interfaces

$Id: interfaces.py 18584 2005-10-14 17:13:27Z regebro $
"""
from zope.app.utility.interfaces import ILocalUtilityService

class IFiveUtilityService(ILocalUtilityService):
    """Extends ILocalUtilityService with a method to register utilities"""
    
    def registerUtility(self, interface, utility, name=''):
        """Registers a utility in the local context"""
        # I think you are *really* supposed to:
        # 1. Check if there is a "registrations" object for utilities.
        # 2. If not create one.
        # 3. Get it.
        # 4. Create a registration object for the utility.
        # 5. Register the registration object in the registrations.
        # But that is quite complex, and Jim sais he wants to change that
        # anyway, and in any case the way you would normally do this in Zope3
        # and Five would probably differ anyway, so, here is this new 
        # Five-only, easy to use method!

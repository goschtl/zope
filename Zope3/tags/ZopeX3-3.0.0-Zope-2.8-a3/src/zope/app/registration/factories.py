##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""A collection of factory functions for various registration classes.

See method factory() in class ComponentRegistrationAdapter in file
registration.py.

The functions here may create invalid objects; a subsequent setBody()
call to the adapter's setBody() method will make the object valid.

$Id$
"""

def CacheRegistration():
    from zope.app.services.cache import CacheRegistration
    return CacheRegistration("", "") # name, componentPath

def ConnectionRegistration():
    from zope.app.services.connection import ConnectionRegistration
    return ConnectionRegistration("", "") # name, componentPath

def ServiceRegistration():
    from zope.app.site.service import ServiceRegistration
    return ServiceRegistration("", "") # name, componentPath

def UtilityRegistration():
    from zope.app.services.utility import UtilityRegistration
    return UtilityRegistration("", None, "") # name, interface, componentPath

##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""A collection of factory functions for various configuration classes.

See method factory() in class ComponentConfigurationAdapter in file
configuration.py.

The functions here may create invalid objects; a subsequent setBody()
call to the adapter's setBody() method will make the object valid.

$Id: factories.py,v 1.2 2003/06/16 16:47:51 gvanrossum Exp $
"""

def CacheConfiguration():
    from zope.app.services.cache import CacheConfiguration
    return CacheConfiguration("", "") # name, componentPath

def ConnectionConfiguration():
    from zope.app.services.connection import ConnectionConfiguration
    return ConnectionConfiguration("", "") # name, componentPath

def ServiceConfiguration():
    from zope.app.services.service import ServiceConfiguration
    return ServiceConfiguration("", "") # name, componentPath

def UtilityConfiguration():
    from zope.app.services.utility import UtilityConfiguration
    return UtilityConfiguration("", None, "") # name, interface, componentPath

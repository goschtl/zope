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
"""Zope-specific HTTP interfaces

$Id$
"""
__docformat__ = 'restructuredtext'

from zope.interface import Interface, Attribute
import zope.deferredimport

zope.deferredimport.deprecatedFrom(
    "This import has moved to zope.publisher.interfaces.http. "
    "This import will stop working in the future.",
    'zope.publisher.interfaces.http',
    'IHTTPException',
    )

class INullResource(Interface):
    """Placeholder objects for new container items to be created via PUT
    """

    container = Attribute("The container of the future resource")
    name = Attribute("The name of the object to be created.")


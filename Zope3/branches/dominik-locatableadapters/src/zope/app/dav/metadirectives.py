##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""'dav' ZCML namespace schemas

$Id$
"""
__docformat__ = 'restructuredtext'

from zope.configuration.fields import GlobalInterface
from zope.interface import Interface
from zope.schema import URI

class IProvideInterfaceDirective(Interface):
    """This directive assigns a new interface to a component. This interface
    will be available via WebDAV for this particular component."""

    for_ = URI(
        title=u"Namespace",
        description=u"Namespace under which this interface will be available"\
                    u" via DAV.",
        required=True)

    interface = GlobalInterface(
        title=u"Interface",
        description=u"Specifies an interface/schema for DAV.",
        required=True)

##############################################################################
#
# Copyright (c) 2005, 2006 Zope Corporation and Contributors.
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

"""
$Id$
"""

__docformat__ = 'restructuredtext'

from zope.app.component.contentdirective import ClassDirective
from zope.app.component.metaconfigure import adapter

from zope.generic.configuration.adapter import ConfigurationAdapterClass



def configurationAdapterDirective(_context, keyface, provides, class_=None, writePermission=None, readPermission=None):
    """Provide a generic configuration adatper."""

    # we will provide a generic adapter class
    if class_ is None:
        class_ = ConfigurationAdapterClass(provides)

    # register class
    class_directive = ClassDirective(_context, class_)
    if writePermission:
        class_directive.require(_context, permission=writePermission, set_schema=[keyface])

    if readPermission:
        class_directive.require(_context, permission=readPermission, interface=[keyface])

    # register adapter
    adapter(_context, factory=[class_], provides=provides, 
            for_=[keyface], permission=None, name='', trusted=True, 
            locate=False)

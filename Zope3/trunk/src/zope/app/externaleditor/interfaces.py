##############################################################################
# Copyright (c) 2003 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
##############################################################################
"""
$Id: interfaces.py,v 1.1 2004/02/27 14:23:16 philikon Exp $
"""
from zope.interface import Interface

class IExternallyEditable(Interface):
    """Just a marker interface to signal to Zope
    that this object can be edited externally using
    Casey Duncan's External Editor.

    For an object to be externally editable there
    are three requirements:

    1. It needs to declare that it implements this interface
       to signal the presentation service that a External Edit
       action should be available.

    2. It needs to have an adapter for the interface
       ``zope.app.interfaces.file.IReadFile``.

    3. It needs to have a ``PUT`` view which receive the content
       back from the External Editor client and update the
       object, optimally using an adapter to the interface
       ``zope.app.interfaces.file.IWriteFile`` (but not
       necessarily).
    """

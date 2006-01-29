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
""" Register class directive.

$Id$
"""
__docformat__ = 'restructuredtext'

from zope.app.fssync.fsregistry import provideSynchronizer

def registerFSRegistry(_context, class_=None, factory=None):
    """`registerFSRegistry` method to register Class and Serializer factory
    associated with it.
    """
    _context.action(
        discriminator=('adapter', class_),
        callable=provideSynchronizer,
        args=(class_, factory) )

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

from zope.annotation.interfaces import IAttributeAnnotatable

from zope.generic.configuration.api import IAttributeConfigurable
from zope.generic.face import IFace
from zope.generic.face import IProvidesAttributeFaced



class ITypedContent(IFace, IAttributeConfigurable, IAttributeAnnotatable):
    """Content that provides the declared key interface."""



class IDirectlyTypedContent(ITypedContent, IProvidesAttributeFaced):
    """Content that  directly provides the declared key interface."""

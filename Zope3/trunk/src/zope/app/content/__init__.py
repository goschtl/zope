##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
$Id: __init__.py,v 1.5 2004/03/02 18:16:12 philikon Exp $
"""
from zope.app.content.interfaces import IContentType
from zope.interface.declarations import providedBy

def queryContentType(object):
    """returns object content type

    >>> from zope.interface import Interface, implements, directlyProvides
    >>> class I(Interface):
    ...     pass
    >>> directlyProvides(I, IContentType)
    >>> class C:
    ...     implements(I)
    >>> obj = C()
    >>> c1_ctype = queryContentType(obj)
    >>> c1_ctype.__name__
    'I'
    >>> class I1(I):
    ...     pass
    >>> class I2(I1):
    ...     pass
    >>> class I3(Interface):
    ...     pass
    >>> class C1:
    ...     implements(I1)
    >>> obj1 = C1()
    >>> c1_ctype = queryContentType(obj1)
    >>> c1_ctype.__name__
    'I'
    >>> class C2:
    ...     implements(I2)
    >>> obj2 = C2()
    >>> c2_ctype = queryContentType(obj2)
    >>> c2_ctype.__name__
    'I'
    >>> class C3:
    ...     implements(I3)
    >>> obj3 = C3()

    If Interface doesn't provide IContentType, queryContentType returns None.
    
    >>> c3_ctype = queryContentType(obj3)
    >>> c3_ctype
    >>> class I4(I):
    ...     pass
    >>> directlyProvides(I4, IContentType)
    >>> class C4:
    ...     implements(I4)
    >>> obj4 = C4()
    >>> c4_ctype = queryContentType(obj4)
    >>> c4_ctype.__name__
    'I4'

    """
    
    object_iro = providedBy(object).__iro__
    for iface in object_iro:
        if IContentType.isImplementedBy(iface):
            return iface
        
    return None
    




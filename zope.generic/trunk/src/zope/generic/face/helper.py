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

from zope.dottedname.resolve import resolve
from zope.generic.face import IUndefinedContext
from zope.generic.face import IUndefinedKeyface
from zope.testing import cleanup



def toDottedName(component):
    if component is None:
        return 'None'
    return component.__module__ + '.' + component.__name__


# cache
__name_to_component = {}

# clean cache for test purposes
def _clear():
    __name_to_component.clear()

cleanup.addCleanUp(_clear)
del _clear

def toInterface(dottedname):
    try:
        return __name_to_component[dottedname]
    except KeyError:
        return __name_to_component.setdefault(dottedname, resolve(dottedname))


def unicodeDictToStrDict(data):
    strDict = {}
    [strDict.__setitem__(str(key), value) for key, value in data.items()]
    return strDict



def toDescription(component, label=None, hint=None):
    """Use the __doc__ attribute for label and hint.

    This function can be used to generate the label an hint of an description.

    No doc string provided:

        >>> class A:
        ...     pass

        >>> label, hint = api.toDescription(A)
        >>> label
        u''
        >>> hint
        u''

    Single line:

        >>> class B:
        ...    '''Test label.   
        ...    '''

        >>> label, hint = api.toDescription(B)
        >>> label
        u'Test label.'
        >>> hint
        u''

    Multi line:

        >>> class C:
        ...    '''Test label.   
        ...
        ...    Test hint, bla bla .  
        ...    bla bla bla:  
        ...         - bla, bla, bla.   '''

        >>> label, hint = api.toDescription(C)
        >>> label
        u'Test label.'
        >>> hint
        u'Test hint, bla bla .\\\\nbla bla bla:\\\\n- bla, bla, bla.'

    You can overwrite the underlying doc string providing your own
    label or hint:

        >>> label, hint = api.toDescription(C, label=u'My label')
        >>> label
        u'My label'
        >>> hint
        u'Test hint, bla bla .\\\\nbla bla bla:\\\\n- bla, bla, bla.'

        >>> label, hint = api.toDescription(C, hint=u'My hint')
        >>> label
        u'Test label.'
        >>> hint
        u'My hint'

    """
    if label and hint:
        return (label, hint)

    elif label:
        doc = getattr(component, '__doc__', None)
        if doc:
            lines = doc.splitlines()
            if lines and lines > 2:
                return (label, u'\\n'.join([line.strip() for line in lines[2:]]))

        return (label, u'')

    elif hint:
        doc = getattr(component, '__doc__', None)
        if doc:
            lines = doc.splitlines()
            if lines:
                return (unicode(lines[0].strip()), hint)

        return (u'')

    else:
        doc = getattr(component, '__doc__', None)
        if doc:
            lines = doc.splitlines()
            if lines:
                if lines > 2:
                    return (unicode(lines[0].strip()), u'\\n'.join([line.strip() for line in lines[2:]]))

                else:
                    return (unicode(lines[0].strip()), u'')

        return (u'', u'')



def toFaceTuple(identifier, keyface=IUndefinedKeyface, conface=IUndefinedContext):
    """Resolve 'keyface@conface' to (keyface, conface).

        >>> from zope.interface import Interface
        
        >>> class IK(Interface):
        ...     pass
        
        >>> class IC(Interface):
        ...     pass

    Example 1:
        
        >>> api.toFaceTuple(api.toDottedName(IK))
        (<InterfaceClass example.IK>, <....IUndefinedContext>)

    Example 2:
        
        >>> api.toFaceTuple('wrong')
        (<....IUndefinedKeyface>, <....IUndefinedContext>)

    Example 3:
        
        >>> api.toFaceTuple(api.toDottedName(IK) + '@' + api.toDottedName(IC))
        (<InterfaceClass example.IK>, <InterfaceClass example.IC>)

    Example 4:
        
        >>> api.toFaceTuple('@' + api.toDottedName(IC))
        (<....IUndefinedKeyface>, <InterfaceClass example.IC>)

    Example 5:
        
        >>> api.toFaceTuple(api.toDottedName(IK) + '@')
        (<InterfaceClass example.IK>, <....IUndefinedContext>)

    Example 6:
        
        >>> api.toFaceTuple('@')
        (<....IUndefinedKeyface>, <....IUndefinedContext>)
  
    """
    
    parts = identifier.split('@')
    
    if len(parts) == 1:
        try:
            return (toInterface(parts[0]), conface)

        except:
            return (keyface, conface)

    else:
        try:
            keyface = toInterface(parts[0])
        
        except:
            keyface = IUndefinedKeyface
        
        try:
            return (keyface, toInterface(parts[1]))
        
        except:
            return (keyface, conface)


##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Wrapping/proxy coordination

Specifically, coordinate use of context wrappers and security proxies.

Revision information:
$Id: context.py,v 1.2 2003/06/01 17:23:34 jim Exp $
"""

from zope.interface import moduleProvides
from zope.security.proxy import Proxy, getChecker
from zope.context.wrapper import getdictcreate
from zope.context.wrapper import getcontext
from zope.context.wrapper import Wrapper
from zope.security.checker import defineChecker, selectChecker, BasicTypes
from zope.proxy import queryProxy, getProxiedObject
from zope.app.interfaces.context import IContextWrapper
from pickle import PicklingError
from zope.proxy import getProxiedObject
from zope.interface import providedBy
from zope.interface.declarations import getObjectSpecification
from zope.interface.declarations import ObjectSpecification
from zope.interface.declarations import ObjectSpecificationDescriptor

moduleProvides(IContextWrapper)
__all__ = tuple(IContextWrapper)

def ContextWrapper(_ob, _parent, **kw):
    
    if type(_ob) in BasicTypes:
        # Don't wrap basic objects
        return _ob

    wrapper = queryProxy(_ob, Wrapper, kw)
    if wrapper is not kw: # using kw as marker
        if _parent is getcontext(wrapper):
            # This would be a redundant wrapper. We'll just use the
            # one we've got.

            # But we want tp make sure we have the same data
            if kw:
                dict = getdictcreate(wrapper)
                dict.update(kw)
            return _ob

    if type(_ob) is Proxy:
        # insert into proxies
        checker = getChecker(_ob)
        _ob = getProxiedObject(_ob)
        _ob = Proxy(Wrapper(_ob, _parent, **kw), checker)
    else:
        _ob = Wrapper(_ob, _parent, **kw)

    return _ob

# XXX Do I actually need these?
def _contextWrapperChecker(ob):
    return selectChecker(getProxiedObject(ob))
defineChecker(Wrapper, _contextWrapperChecker)

def getItem(collection, name):
    return ContextWrapper(collection[name], collection, name=name)

def getAttr(collection, name):
    return ContextWrapper(getattr(collection, name), collection, name=name)

def queryItem(collection, name, default=None):
    return ContextWrapper(collection.get(name, default),
                          collection, name=name)

def queryAttr(collection, name, default=None):
    return ContextWrapper(getattr(collection, name, default),
                          collection, name=name)

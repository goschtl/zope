##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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

from zope.interface import implements

from z3c.resource import interfaces
from z3c.proxy.container import ContainerLocationProxy



class ResourceLocationProxy(ContainerLocationProxy):
    """Proxy a resource container.

    The specific resource container implementation of a traversable component
    can be proxied.

    Now we create our resource test implementation. We take a container that
    implements ResourceTraversable:
    
        >>> from z3c.resource.testing import ResourceTraversableContainer
        >>> resourcetraversable = ResourceTraversableContainer()

    Inside this resource traversabel we put our resource container:

        >>> from z3c.resource.testing import TestResourceContainer
        >>> resourcetraversable['pc'] = pc = TestResourceContainer()

    Now we proxy our prototyped resource container implementation. The
    resourcetraversable will be the parent of the proxied resource container and
    that should be named to '@@':

        >>> pcproxy = ResourceLocationProxy(pc, resourcetraversable)
        >>> pcproxy.__name__ == u'@@'
        True
        >>> pcproxy.__parent__ is resourcetraversable
        True

    Containment put into the resource container appears in the
    resource location proxy:

        >>> from z3c.resource.testing import TestResourceItem
        >>> pc['x'] = x = TestResourceItem()

        >>> x1 = pcproxy['x']
        >>> from zope.proxy import isProxy
        >>> isProxy(x1)
        True
        >>> x1 == x
        True

    Containment put into the resource location proxy appears in 
    the resource container:

        >>> pcproxy['y'] = y = TestResourceItem()
        >>> pc['y'] is y
        True

        >>> y1 = pcproxy['y']
        >>> isProxy(y1)
        True
        >>> y1 == y
        True

    Finaly we check all other methods of the proxy:

        >>> 'x' in pcproxy
        True
        >>> pcproxy.has_key('x')
        1
        >>> keys = [key for key in pcproxy.keys()]; keys.sort(); keys
        [u'x', u'y']
        >>> items = [item for item in pcproxy.items()]; items.sort()
        >>> items == [(u'x', x), (u'y', y)]
        True
        >>> pcproxy.get('x') == x
        True
        >>> iterator = iter(pcproxy)
        >>> iterator.next() in pcproxy
        True
        >>> iterator.next() in pcproxy
        True
        >>> iterator.next()     
        Traceback (most recent call last):
        ...
        StopIteration
        >>> values = pcproxy.values(); values.sort();
        >>> x in values, y in values
        (True, True)
        >>> len(pcproxy)
        2
        >>> del pcproxy['x']
        >>> 'x' in pcproxy
        False

    """

    implements(interfaces.IResourceLocationProxy)

    def __init__(self, context, parent):
        # preconditions
        if not interfaces.IResourceContainer.providedBy(context):
            raise ValueError(
                'Parameter context: IResourceContainer required.')

        if not interfaces.IResourceTraversable.providedBy(parent):
            raise ValueError(
                'Parameter parent: IResourceTraversable required.')

        # essentails
        super(ResourceLocationProxy, self).__init__(context)
        self.__name__ = u'@@'
        self.__parent__ = parent

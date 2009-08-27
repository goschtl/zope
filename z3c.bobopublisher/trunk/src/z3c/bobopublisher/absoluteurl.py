##############################################################################
#
# Copyright (c) 2009 Fabio Tranchitella <fabio@tranchitella.it>
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

from urllib import quote, unquote

from z3c.bobopublisher.interfaces import IAbsoluteURL, IRequest

from zope.component import adapts, getMultiAdapter
from zope.interface import implements, Interface
from zope.location.interfaces import ILocation, ILocationInfo, IRoot


class AbsoluteURL(object):
    """AbsoluteURL adapter

    Verify the class:

        >>> from zope.interface.verify import verifyClass
        >>> verifyClass(IAbsoluteURL, AbsoluteURL)
        True

    Create a testing environment for the adapter:

        >>> from webob import Request
        >>> request = Request.blank('http://localhost/test')

        >>> from zope.interface import implements
        >>> from zope.location.interfaces import IRoot, ILocation

        >>> class Root(object):
        ...     implements(IRoot, ILocation)
        ...     __name__ = u'root'
        ...     __parent__ = None

        >>> class SubItem(object):
        ...     implements(ILocation)
        ...     def __init__(self, name, parent):
        ...         self.__name__ = name
        ...         self.__parent__ = parent

        >>> root = Root()
        >>> a = SubItem(u'\xe1', root)
        >>> b = SubItem(u'b', a)

        >>> from zope.component import provideAdapter
        >>> from zope.location.traversing import LocationPhysicallyLocatable
        >>> provideAdapter(LocationPhysicallyLocatable)

        >>> from zope.interface import Interface
        >>> provideAdapter(AbsoluteURL, (Interface, Interface), IAbsoluteURL)

    Verify the object:

        >>> from zope.interface.verify import verifyObject
        >>> obj = AbsoluteURL(b, request)
        >>> verifyObject(IAbsoluteURL, obj)
        True

    Check the behaviour of the adapter:

        >>> str(obj)
        'http://localhost/%C3%A1/b'

        >>> obj()
        'http://localhost/%C3%A1/b'

        >>> unicode(obj)
        u'http://localhost/\\xe1/b'

        >>> breadcrumbs = obj.breadcrumbs()
        >>> breadcrumbs[0]
        {'url': 'http://localhost', 'name': u'root'}
        >>> breadcrumbs[1]
        {'url': 'http://localhost/%C3%A1', 'name': u'\\xe1'}
        >>> breadcrumbs[2]
        {'url': 'http://localhost/%C3%A1/b', 'name': u'b'}

    """

    implements(IAbsoluteURL)
    adapts(Interface, IRequest)

    _safe = '/@+'

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __str__(self):
        path = ILocationInfo(self.context).getPath()
        if path == '/':
            path = ''
        return '%s%s' % (self.request.application_url,
            quote(path.encode('utf-8'), self._safe))

    def __unicode__(self):
        return unquote(str(self)).decode('utf-8')

    def __call__(self):
        return str(self)

    def breadcrumbs(self):
        parts = []
        object = self.context
        while not IRoot.providedBy(object):
            object = ILocation(object)
            adapter = getMultiAdapter((object, self.request), IAbsoluteURL)
            parts.append({'name': object.__name__, 'url': str(adapter)})
            object = object.__parent__
        if ILocation.providedBy(object):
            adapter = getMultiAdapter((object, self.request), IAbsoluteURL)
            parts.append({'name': object.__name__, 'url': str(adapter)})
        parts.reverse()
        return parts

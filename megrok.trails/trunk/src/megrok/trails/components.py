##############################################################################
#
# Copyright (c) 2007-2008 Zope Corporation and Contributors.
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

"""megrok.trails components"""

import grok
import urllib
from zope.interface import implements
from zope.component import provideAdapter, queryMultiAdapter
from zope.traversing.browser.interfaces import IAbsoluteURL
from zope.publisher.interfaces.http import IHTTPRequest
from zope.publisher.browser import BrowserView

#

_safe = '@+' # Characters that we don't want to have quoted

class TrailAbsoluteURLFactory(object):
    """Factory that allows Trails to provide AbsoluteURLs.

    The goal is that each time the programmer creates a Trail, an
    adapter will be registered that allows the objects at the end of
    the Trail to have the URL described by the Trail's arguments.

    For example, if one creates a Trail('/person/:name', Person) and,
    later, a page template calls view.url(person), then an adapter
    should be available for IAbsoluteURL that will construct the URL
    '/person/Edward' or whatever.

    Therefore, the code below calls this *class* like:

        TrailAbsoluteURLFactory(trail)

    in order to return an *instance* of this class that the Zope
    multi-adapter component logic will later call like:

        instance(obj, request)

    at which point we will return an actual instance of
    TrailAbsoluteURL, on which we have installed the actual Trail
    instance that it will need in order to compute its response.

    """
    def __init__(self, trail):
        self.trail = trail

    def __call__(self, *args):
        t = TrailAbsoluteURL(*args)
        t.trail = self.trail
        return t

class TrailAbsoluteURL(BrowserView):
    """Return the Absolute URL of an object for which a Trail is defined."""
    implements(IAbsoluteURL)

    def __unicode__(self):
        return urllib.unquote(self.__str__()).decode('utf-8')

    def __str__(self):
        return self.trail.url(self.context, self.request)
        #url += '/' + urllib.quote(name.encode('utf-8'), _safe)

    __call__ = __str__

    def breadcrumbs(self):
        url = self()
        return ({ 'name': url.strip('/'), 'url': url},)


class Trail(object):
    """The URL pattern defined for a particular class.

    One can imagine many different ways of implementing Trails;
    this simple one allows patterns like '/account/:username'
    to result in URLs like '/account/brandon'.

    """
    def __init__(self, spec, constructor, cls=None):
        """Create a Trail to an object.

        Calls should look like one of:

        Trail('/account/:username', Account) # if Account(3) returns it
        Trail('/account/:username', lookup_account, Account)

        """
        self.spec = spec
        self.parts = spec.strip('/').split('/')
        if cls is None:
            cls = constructor
        self.constructor = constructor
        self.cls = cls
        tf = TrailAbsoluteURLFactory(self)
        provideAdapter(tf, (cls, IHTTPRequest), IAbsoluteURL)
        provideAdapter(tf, (cls, IHTTPRequest), IAbsoluteURL,
                       name = 'absolute_url')

    def match(self, namelist):
        """Determine whether this Trail matches a URL.

        Given a list of names like ['archive', '2007', 'October']
        which represent a URL like '.../archive/2007/October',
        determine whether they match this particular Trail.

        If there is no match, return None.

        If there is a match, then return an instance the class
        we were given during instantiation, supplying its constructor
        with the arguments taken from the URL.

        """
        parts = self.parts
        if len(namelist) != len(parts):
            return False
        result = {}
        for name, part in zip(namelist, self.parts):
            if part.startswith(':'):
                result[part[1:]] = name
            elif part != name:
                return None
        return self.constructor(**result)

    def url(self, obj, request):
        """Return the URL of an object as defined by this Trail.

        Given an instance of the class for which this Trail was defined,
        return its URL as a string.

        """
        def subst(part, obj):
            if part.startswith(':'):
                return str(getattr(obj, part[1:]))
            return part

        parts = [ subst(part, obj) for part in self.parts ]
        return grok.url(request, grok.getSite()) + '/' + '/'.join(parts)


class TrailHead(grok.Traverser):
    """Dispatch URLs to a collection of trails.

    In order to use Trails, create a subclass of TrailHead, and
    declare as its context the class on which you want URLs built.
    You yourself must provide the machinery for users to navigate to
    that class; then Trails will take over and accept subsequent URL
    components until a Trail is matched.

    When creating a subclass of TrailHead, provide it with a class
    variable named ``trails`` that lists one or more Trail objects.

    """
    grok.baseclass()

    def traverse(self, name):
        namelist = [ name ]
        for trail in self.trails:
            m = trail.match(namelist)
            if m:
                return m
        view = queryMultiAdapter((self.context, self.request), name=name)
        if view is not None:
            return view
        return TrailFork(self.trails, namelist)


class TrailFork(grok.Model):
    """A fork in the trail.

    A TrailFork represents a point at which some URL components have
    been collected past a TrailHead, but they have not yet matched one
    of that TrailHead's Trails.  This Traverser accepts the next URL
    component past the TrailFork and determines whether we have yet
    matched any of the Trails of this TrailHead.

    """
    def __init__(self, trails, namelist):
        self.trails = trails
        self.namelist = namelist

    def traverse(self, name):
        namelist = list(self.namelist)
        namelist.append(name)
        for trail in self.trails:
            m = trail.match(namelist)
            if m:
                return m
        return TrailFork(self.trails, namelist)

##############################################################################
#
# Copyright (c) 2006-2007 Zope Corporation and Contributors.
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
from zope.component import provideAdapter
from zope.traversing.browser.interfaces import IAbsoluteURL
from zope.publisher.interfaces.http import IHTTPRequest
from zope.publisher.browser import BrowserView


class TrailRegistry(object):
    """Remembers which Trails have been defined for which classes.

    When Zope tries to determine the URL of an object
    and asks our TrailAbsoluteURL adapter for its opinion,
    it consults an instance of this registry which stores,
    for each class for which a Trail has been defined,
    the corresponding Trail.

    """
    def __init__(self):
        self.classes = {}

    def register(self, pattern):
        self.classes[pattern.cls] = pattern

    def __getitem__(self, key):
        return self.classes[key]

# At the moment, we keep a single global registry here in the module.
# Someday we might wish to make this a local utility inside of each
# Grok site, so that different sites can return different URLs for the
# same sorts of object.
    
_registry = TrailRegistry()


_safe = '@+' # Characters that we don't want to have quoted

class TrailAbsoluteURL(BrowserView):
    """Return the Absolute URL of an object for which a Trail is defined."""

    def __unicode__(self):
        return urllib.unquote(self.__str__()).decode('utf-8')

    def __str__(self):
        cls = type(self.context)
        pattern = _registry[cls]
        return pattern.url(self.context, self.request)
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
    def __init__(self, spec, cls):
        """Create a Trail to an object.

        Calls should look like: Trail('/account/:username', Account)

        """
        self.spec = spec
        self.parts = spec.strip('/').split('/')
        self.cls = cls
        _registry.register(self)
        provideAdapter(TrailAbsoluteURL, (cls, IHTTPRequest), IAbsoluteURL)

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
        return self.cls(**result)

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


class _Dummy(object):
    """Dummy class.

    We cannot define a subclass of grok.Traverser without the
    Traverser grokker getting all upset about its needing to declare a
    context, so this Dummy class servers as the context for the
    TrailHead class.  Each time users actually subclass TrailHead
    themselves, they will define their own context.
    """

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
    grok.context(_Dummy)

    def traverse(self, name):
        namelist = [ name ]
        for trail in self.trails:
            m = trail.match(namelist)
            if m:
                return m
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

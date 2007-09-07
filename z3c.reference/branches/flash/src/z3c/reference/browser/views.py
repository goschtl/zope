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

import urllib

from zope import component
from zope.traversing.browser import absoluteURL
from zope.traversing.interfaces import IContainmentRoot
from zope.traversing.browser.interfaces import IAbsoluteURL
from zope.traversing.browser.absoluteurl import AbsoluteURL
from zope.app.intid.interfaces import IIntIds

from z3c.reference import interfaces

noImage = '/@@/z3c.reference.resources/noimage.jpg'


class ViewReferenceAbsoluteURL(AbsoluteURL):

    """adapts a view reference to IAbsoluteURL

    >>> from z3c.reference.reference import ViewReference
    >>> from zope.publisher.browser import TestRequest
    >>> ref = ViewReference(view=u'http://www.zope.org/')
    >>> request = TestRequest()
    >>> view = ViewReferenceAbsoluteURL(ref, request)
    >>> view
    <z3c.reference.browser.views.ViewReferenceAbsoluteURL ...>
    >>> view()
    'http://www.zope.org/'

    >>> ref = ViewReference(target=site)
    >>> view = ViewReferenceAbsoluteURL(ref, request)
    >>> view()
    'http://127.0.0.1'

    >>> ref = ViewReference(target=site, view=u'index.html?x=1&y=2')
    >>> view = ViewReferenceAbsoluteURL(ref,request)
    >>> view()
    'http://127.0.0.1/index.html?x=1&y=2'
    """

    def __init__(self, context, request):
        self.context = context.target
        self.view = context.view
        self.request = request

    def __str__(self):
        if self.context is not None:
            if self.context.__name__ or IContainmentRoot.providedBy(
                self.context):
                view = component.getMultiAdapter((self.context, self.request),
                                                 IAbsoluteURL)
                try:
                    url = view()
                except TypeError:
                    return noImage
                if self.view is not None:
                    url = '%s/%s' % (url, self.view.encode('utf8'))
                return url
            else:
                # the target ist lost TODO:
                return noImage
        elif self.view is not None:
            return self.view.encode('utf8')

        raise TypeError("Can't get absolute url of reference,"
                        "because there is no target or view "
                        "specified.")
    __call__=__str__
    def breadcrumbs(self):
        if self.context is not None:
            view = component.getMultiAdapter((self.context, self.request),
                                             IAbsoluteURL)
            return view.breadcrumbs()
        raise TypeError("Can't get breadcrumbs of external reference")


class ViewReferenceEditor(object):
    """View reference editor offering search and edit form setup.
    The following objects are used:
    context = view reference
    target = referenced object

    """
    name = u''
    settingNameStr = u''
    viewStr = u''
    targetStr = u''
    titleStr = u''
    descriptionStr = u''

    def __call__(self):
        """Setup JS variables."""
        self.name = self.request.get('name', u'')
        self.settingNameStr = self.request.get('settingName', u'')
        self.viewStr = self.request.get('view', u'')
        self.targetStr = self.request.get('target', u'')
        self.titleStr = self.request.get('title', u'')
        self.descriptionStr = self.request.get('description', u'')
        return super(ViewReferenceEditor, self).__call__()


class ViewReferenceEditorSearchDispatcher(object):

    """Return the IViewReferenceEditorSearch form for given setting
    name"""

    settingNameStr = u''
    viewStr = u''
    targetStr = u''
    titleStr = u''
    descriptionStr = u''

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        self.settingNameStr = self.request.get('settingName', u'')
        if self.settingNameStr:
            view = component.queryMultiAdapter((self.context, self.request),
                interfaces.IViewReferenceEditorSearch, name=self.settingNameStr)
            if view is not None:
                return view()
        return u''


class ViewReferenceEditorDispatcher(object):

    """Return the edit IViewReferenceEditor for the target context
    and setting"""

    settingNameStr = u''
    viewStr = u''
    targetStr = u''
    titleStr = u''
    descriptionStr = u''

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        self.settingNameStr = self.request.get('settingName', u'')
        self.targetStr = self.request.get('target', u'')
        self.viewStr = self.request.get('view', u'')
        self.titleStr = self.request.get('title', u'')
        self.descriptionStr = self.request.get('description', u'')
        if not self.targetStr:
            return u''
        intids = component.getUtility(IIntIds)
        obj = intids.queryObject(int(self.targetStr))
        if obj is not None and self.settingNameStr is not None:
            view = component.queryMultiAdapter((obj, self.request),
                interfaces.IViewReferenceEditor, name=self.settingNameStr)
            if view is not None:
                return view()
        return u''

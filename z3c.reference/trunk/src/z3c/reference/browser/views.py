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
from zope import interface
from zope.traversing.browser import absoluteURL
from zope.traversing.interfaces import IContainmentRoot
from zope.traversing.browser.interfaces import IAbsoluteURL
from zope.traversing.browser.absoluteurl import AbsoluteURL
from zope.app.intid.interfaces import IIntIds
from zope.app.form.browser.widget import renderElement
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.dublincore.interfaces import IZopeDublinCore
from zope.app.keyreference.interfaces import NotYet
from zc import resourcelibrary

from lovely.relation.dataproperty import DataRelationship

from z3c.reference import interfaces

noImage = '/@@/z3c.reference.resources/noimage.jpg'


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
        resourcelibrary.need('z3c.reference.popup')
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
        return u'Error: unable to load view for %s' % self.settingNameStr


def getEditorView(target, request, settingName):
    return component.getMultiAdapter(
        (target, request),
        interfaces.IViewReferenceEditor, name=settingName)


def getOpenerView(ref, request, settingName):

    def _adapter(o, name=u''):
        return component.queryMultiAdapter(
            (o, request),
            interfaces.IViewReferenceOpener, name=name)
    view = None
    if ref is None:
        # we provide a default relationship instance
        ref = DataRelationship(None, None)
        target = None
    else:
        target = ref.target
    if target is not None:
        view = _adapter(target, settingName)
        if view is None:
            view = _adapter(target)
    if view is None:
        view = _adapter(ref, settingName)
        if view is None:
            view = _adapter(ref)
    return view


class DefaultViewReferenceOpener(object):
    interface.implements(interfaces.IViewReferenceOpener)

    __call__ = ViewPageTemplateFile('opener.pt')

    prefix = ''

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def target(self):
        try:
            target = self.context.target
        except NotYet:
            return None
        return target

    @property
    def title(self):
        if self.target is not None:
            return IZopeDublinCore(self.context).title
        return u'Undefined'

    @property
    def spanTitleId(self):
        return self.prefix + '.title'


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
            view = getEditorView(obj, self.request, self.settingNameStr)
            return view()
        return u''


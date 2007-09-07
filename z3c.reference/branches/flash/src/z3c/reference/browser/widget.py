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

import urlparse, cgi, urllib
from xml.dom.minidom import parse, parseString

import zope.component
from zope.traversing.browser import absoluteURL
from zope.traversing.interfaces import TraversalError
from zope.cachedescriptors.property import Lazy

from zope.app.intid.interfaces import IIntIds
from zope.app.form.browser.widget import SimpleInputWidget
from zope.app.form.browser.textwidgets import TextWidget
from zope.app.component import hooks
from zope.app.form.browser.widget import renderElement

from zc import resourcelibrary
from z3c.reference import interfaces
from z3c.reference.reference import ViewReference,ImageReference

untitled = u'No Link defined'
undefined = u'Undefined'

emptyViewReference = None
emptyImageReference = ImageReference(
    view=u'/@@/z3c.reference.resources/noimage.jpg')

def getText(nodelist):
    rc = ""
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc = rc + node.data
    return rc


class ViewReferenceWidget(TextWidget):
    """renders an "a" tag with the title and href attributes."""

    tag = u'input'
    type = u'text'
    cssClass = u'popupwindow'
    extra =  u'rel="window"'
    refTag = u'a'
    refTagOnClick=""
    _emptyReference = emptyViewReference
    referenceExplorerViewName = 'viewReferenceEditor.html'

    def __init__(self, *args):
        resourcelibrary.need('z3c.reference')
        super(ViewReferenceWidget, self).__init__(*args)

    @property
    def referenceEditorURL(self):
        """Returns the refrence explorer url."""
        return absoluteURL(self.context.context, self.request) + '/%s?%s' % (
            self.referenceExplorerViewName, 
            urllib.urlencode({'settingName': self.context.settingName,
                             'target': self.targetValue,
                             'view': self.viewValue,
                             'name': self.name}))

    @property
    def viewValue(self):
        """Returns the reference view string."""
        current = self._getCurrentValue()
        if current and current.view:
            return current.view or u''
        else:
            return u''

    @property
    def targetValue(self):
        """Returns the target intid."""
        target = u''
        current = self._getCurrentValue()
        if current and current.target:
                intIds = component.getUtility(IIntIds)
                target = intIds.getId(current.target)
        return target

    @property
    def titleValue(self):
        """Returns the reference title."""
        current = self._getCurrentValue()
        if current and current.title:
            return current.title or u''
        else:
            return u''

    @property
    def descriptionValue(self):
        """Returns the reference description."""
        current = self._getCurrentValue()
        if current and current.description:
            return current.description or u''
        else:
            return u''

    def __call__(self):
        resourcelibrary.need('z3c.reference')
        if self._renderedValueSet():
            ref = self._data
        else:
            ref = self.context.default
        if not ref:
            try:
                ref = self.context.get(self.context.context)
            except:
                ref = None
        if ref is None:
            ref = self._emptyReference
        contents = undefined
        targetName = self.name + '.target'
        viewName = self.name + '.view'
        titleName = self.name + '.title'
        descriptionName = self.name + '.description'
        intidInput = renderElement(u'input',
                             type='hidden',
                             name=targetName,
                             id=targetName,
                             value=self.targetValue,
                             extra=self.extra)
        viewInput = renderElement(u'input',
                             type='hidden',
                             name=viewName,
                             id=viewName,
                             value=self.viewValue,
                             extra=self.extra)
        titleInput = renderElement(u'input',
                             type='hidden',
                             name=titleName,
                             id=titleName,
                             value=self.titleValue,
                             extra=self.extra)
        descriptionInput = renderElement(u'input',
                             type='hidden',
                             name=descriptionName,
                             id=descriptionName,
                             value=self.descriptionValue,
                             extra=self.extra)
        linkTag = renderElement(self.refTag,
                            href = self.referenceEditorURL,
                            name=self.name,
                            id=self.name + '.tag',
                            title=contents,
                            onclick=self.refTagOnClick,
                            cssClass = self.cssClass,
                            contents=contents,
                            style=self.style,
                            extra=self.extra)
        return linkTag + viewInput + intidInput + titleInput + descriptionInput

    def _getFormValue(self):
        res = super(ViewReferenceWidget,self)._getFormValue()
        return res

    def _toFormValue(self, value):
        if value == self.context.missing_value:
            return self._missing
        try:
            url = absoluteURL(value,self.request)
        except TypeError:
            return self._missing
        return url
    
    def _toFieldValue(self, input):
        if input == self._missing:
            return self.context.missing_value

        # get the existing reference
        if hasattr(self.context.context, self.context.__name__):
            ref = getattr(self.context.context, self.context.__name__)
        # get a allready set reference
        elif interfaces.IViewReference.providedBy(self._data):
            ref = self._data
        else:
            ref = ViewReference()
        # form field ids
        targetName = self.name + '.target'
        viewName = self.name + '.view'
        titleName = self.name + '.title'
        descriptionName = self.name + '.description'
        
        # get target obj str
        intid = self.request.get(targetName)
        if intid is None:
            return self.context.missing_value
        intIds = zope.component.getUtility(IIntIds)
        obj = intIds.queryObject(int(intid))
        if obj is None:
            return self.context.missing_value
        ref.target = obj

        # write view str
        viewStr = self.request.get(viewName)
        if viewStr is None:
            return self.context.missing_value
        ref.view = unicode(viewStr)

        # write title str
        titleStr = self.request.get(titleName)
        if titleStr is None:
            return self.context.missing_value
        ref.title = unicode(titleStr)

        # write description str
        descriptionStr = self.request.get(descriptionName)
        if descriptionStr is None:
            return self.context.missing_value
        ref.description = unicode(descriptionStr)

        return ref


class ObjectReferenceWidget(ViewReferenceWidget):
    
    @Lazy
    def extra(self):
        iface = self.context.refSchema
        name = u'%s.%s' % (iface.__module__,iface.__name__)
        return u'z3c:explorerLink="@@explorer.html?link=1&schema=%s"' % \
               name


class ImageReferenceWidget(ViewReferenceWidget):

    """renders an "a" tag with the title and href attributes

    if no target

    >>> from zope.publisher.browser import TestRequest
    >>> from z3c.reference.schema import ImageReferenceField
    >>> from zope.app.folder import Folder
    >>> f = Folder()
    >>> site['folder'] = f
    >>> field = ImageReferenceField(title=(u'Title of Field'),
    ...     __name__='ref',size=(10,10))
    >>> request = TestRequest()
    >>> w = ImageReferenceWidget(field,request)
    >>> print w()
    <input .../><img ...height="10" id="field.ref.tag" .../>
    
    """


    
    refTag = u'img'
    _emptyReference = emptyImageReference
    extra = u''

    
    def __call__(self):
        hidden = super(ViewReferenceWidget,self).__call__()
        if self._renderedValueSet():
            ref = self._data
        else:
            ref = self.context.default
        if not ref:
            try:
                ref = self.context.get(self.context.context)
            except:
                ref = None
        if ref is None:            
            ref = self._emptyReference
            url = absoluteURL(ref, self.request)
        else:
            # return uid instead of absoluteURL cuz of umlaut problems
            url = str(absoluteURL(ref.target,self.request)) + '/' + ref.view
        if ref.target is not None:
            title = getattr(ref.target,'title',None) or \
                       ref.target.__name__
        else:
            title = untitled
        width,height = self.context.size
        kwords = dict(src=url,
                      name=self.name,
                      id=self.name + '.tag',
                      title=title,
                      alt=title,
                      width=width,
                      height=height,
                      onclick=self.refTagOnClick,
                      style=self.style,
                      extra=self.extra)
        tag = renderElement(self.refTag,**kwords)
        return hidden + tag


    def _toFormValue(self, value):
        if value == self.context.missing_value:
            return self._missing
        try:
            # return uid instead of absoluteURL cuz of umlaut problems
            url = str(absoluteURL(value.target,self.request)) + '/' + value.view
        except TypeError:
            return self._missing
        return url

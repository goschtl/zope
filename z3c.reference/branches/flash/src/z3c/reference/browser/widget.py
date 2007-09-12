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
from zope.publisher.browser import TestRequest
from zope.app.intid.interfaces import IIntIds
from zope.app.form.browser.widget import SimpleInputWidget
from zope.app.form.browser.textwidgets import TextWidget
from zope.app.component import hooks
from zope.app.form.browser.widget import renderElement
from zope.app.form.browser.textwidgets import BytesWidget
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.event import notify
from zope.lifecycleevent import ObjectCreatedEvent
from zc import resourcelibrary
from z3c.reference import interfaces
from z3c.reference.reference import ViewReference,ImageReference
from views import getEditorView, getOpenerView
from serialize import serializeForm
from zope.formlib import form
from zope.security.proxy import removeSecurityProxy

untitled = u'No Link defined'
undefined = u'Undefined'

emptyViewReference = None
emptyImageReference = ImageReference(
    view='/@@/z3c.reference.resources/noimage.jpg')

def getText(nodelist):
    rc = ""
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc = rc + node.data
    return rc

class ViewReferenceWidget(TextWidget):
    """renders an "a" tag with the title and href attributes."""

    template = ViewPageTemplateFile('widget.pt')

    tag = u'input'
    type = u'text'
    cssClass = u'popupwindow'
    extra =  u'rel="window"'
    refTag = u'a'
    refTagOnClick=""
    _emptyReference = emptyViewReference
    referenceExplorerViewName = 'viewReferenceEditor.html'

    def __init__(self, *args):
        resourcelibrary.need('z3c.reference.parent')
        super(ViewReferenceWidget, self).__init__(*args)

    @property
    def referenceEditorURL(self):
        """Returns the refrence explorer url."""
        return absoluteURL(self.context.context, self.request) + '/%s?%s' % (
            self.referenceExplorerViewName,
            urllib.urlencode({'settingName' : self.context.settingName,
                              'target' : self.targetValue,
                              'name': self.name}))

    @property
    def formDataValue(self):
        ref = self._getCurrentValue()
        if ref is None or ref.target is None:
            return ''
        klass = getEditorView(ref.target, self.request,
                              self.context.settingName).__class__
        r = TestRequest()
        view = klass(ref, r)
        view = ApplyForm(ref, r, view.form_fields)
        view.update()
        html = ''
        for widget in view.widgets:
            v = widget()
            html += v
        qs = serializeForm(html)
        return qs

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
            intIds = zope.component.getUtility(IIntIds)
            target = intIds.getId(current.target)
        return target

    @property
    def refIdName(self):
        return self.name +  u'.refId'

    @property
    def refIdValue(self):
        """Returns the target intid."""
        refId = u''
        current = self._getCurrentValue()
        if current:
            intIds = zope.component.getUtility(IIntIds)
            refId = intIds.getId(current)
        return refId

    @property
    def titleValue(self):
        """Returns the reference title."""
        current = self._getCurrentValue()
        if current and current.title:
            return current.title or u''
        else:
            return u''


    def __call__(self):

        resourcelibrary.need('z3c.reference.parent')
        if self._renderedValueSet():
            ref = self._data
        else:
            ref = self.context.default
        if not ref:
            try:
                ref = self.context.get(self.context.context)
            except:
                ref = None
        openerView = getOpenerView(ref, self.request,
                                   self.context.settingName)
        contents = openerView()
        if ref is None:
            ref = ViewReference()

        targetName = self.name + '.target'
        formDataName = self.name + '.formData'
        intidInput = renderElement(u'input',
                                   type='hidden',
                                   name=targetName,
                                   id=targetName,
                                   value=self.targetValue,
                                   extra=self.extra)
        refIdInput = renderElement(u'input',
                                   type='hidden',
                                   name=self.refIdName,
                                   id=self.refIdName,
                                   value=self.refIdValue,
                                   extra=self.extra)
        formDataInput = renderElement(u'input',
                                      type='hidden',
                                      name=formDataName,
                                      id=formDataName,
                                      value=self.formDataValue,
                                      extra=self.extra)
        linkTag = renderElement(self.refTag,
                                href = self.referenceEditorURL,
                                name=self.name,
                                id=self.name + '.tag',
                                onclick=self.refTagOnClick,
                                cssClass = self.cssClass,
                                contents=contents,
                                style=self.style,
                                extra=self.extra)
        return self.template(linkTag=linkTag, intidInput=intidInput, 
            formDataInput=formDataInput, refIdInput=refIdInput)

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

    def hasInput(self):
        return not not self.request.form.get(self.name + '.target')

    def _toFieldValue(self, input):

        if input == self._missing:
            return self.context.missing_value

        # XXX this does not work with lists
        refId = self.request.form.get(self.refIdName)
        intIds = zope.component.getUtility(IIntIds)
        if refId:
            ref = intIds.getObject(int(refId))

        else:
            ref = ViewReference()
            ref.__parent__ = removeSecurityProxy(self.context.context)
            #notify(ObjectCreatedEvent(ref))

        # form field ids
        formDataName = self.name + '.formData'
        targetName = self.name + '.target'

        # get target obj str
        intid = self.request.get(targetName)
        if intid is None:
            return self.context.missing_value

        obj = intIds.queryObject(int(intid))
        if obj is None:
            return self.context.missing_value
        ref.target = obj

        # apply the form data
        formData = self.request.get(formDataName)
        if not formData:
            return ref
        data = cgi.parse_qs(str(formData))
        for k, v in data.items():
            if type(v) is type([]) and len(v)==1:
                data[k] = v[0].decode('utf8')

        data['form.actions.apply'] = u''
        r = TestRequest(form=data)
        klass = getEditorView(ref.target, self.request,
                              self.context.settingName).__class__
        view = klass(ref, r)
        view = ApplyForm(ref, r, view.form_fields)
        view.update()
        return ref

class ApplyForm(form.EditForm):

    def __init__(self, context, request, form_fields):
        self.form_fields = form_fields
        super(ApplyForm, self).__init__(context, request)

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


class CropImageWidget(BytesWidget):
    """widget for cropping images"""

    template = ViewPageTemplateFile('crop-image-widget.pt')
    keepAspect = False
    cropWidth = 50
    cropHeight = 50
    
    def url(self):
        return absoluteURL(self.context.context, self.request)
    
    def inputField(self):
        return super(CropImageWidget, self).__call__()

    def escapedName(self):
        return self.name.replace('.', r'\.')
    
    def __call__(self, *args, **kw):
        resourcelibrary.need('z3c.javascript.swfobject')
        return self.template(*args, **kw)
        

        

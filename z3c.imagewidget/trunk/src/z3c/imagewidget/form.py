##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
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
"""Image Widget Forms

$Id$
"""
__docformat__ = "reStructuredText"
from zope.formlib import form
from zope.publisher.browser import BrowserPage
from zope.traversing.browser.absoluteurl import absoluteURL
from zope.app.component import hooks
from zope.app.file.interfaces import IImage
from zope.app.file.image import Image
from zope.app.i18n import ZopeMessageFactory as _
from zope.app.pagetemplate import ViewPageTemplateFile

from z3c.sessionwidget.widget import SESSION_KEY


def _resize(data, w, h):
    # do nothing if we have no size constraints
    if w is None and h is None:
        return data
    img = Image(data)
    # if we can get no content type do nothing
    if not img.contentType:
        return data
    # defer this import, so we have no hard dependency at runtime
    from z3c.image.proc.browser import getMaxSize
    iw, ih = size = img.getImageSize()
    width = w or iw
    height = h or ih
    new_size = getMaxSize(size, (width, height))
    # if we have no changes return the value
    if new_size == size:
        return img
    from z3c.image.proc.interfaces import IProcessableImage
    pimg = IProcessableImage(img)
    pimg.resize(new_size)
    processed = pimg.process()
    data = processed.data
    if type(data) != str:
        f = data
        data = f.read()
        f.close()
    return data

class AddImageForm(form.AddFormBase):
    """Add an image.

    This view expects the session widget as context.
    """

    label = _('Add Image')
    prefix = 'imageForm'
    form_fields = form.Fields(IImage).select('data')
    template = ViewPageTemplateFile('add.pt')

    def createAndAdd(self, data):
        imagedata = data.get('data')
        if imagedata:
            imagedata = _resize(imagedata,
                                self.context.width,
                                self.context.height)
            image = Image(imagedata)
            self.context.session['data'] = image
            #self.context.setRenderedValue(image)
            self.context.session['changed'] = True


class EditImageForm(form.EditFormBase):
    """Edit an image

    This view uses the image as context.
    """

    label = u''
    prefix = 'imageForm'
    form_fields = form.Fields(IImage).select('data')
    actions = form.Actions()
    template = ViewPageTemplateFile('edit.pt')

    # We need the widget, so we have a link back to sanity
    widget = None

    @form.action(_("Update image"))
    def handle_edit_action(self, action, data):
        if data['data'] == '':
            self.widget.session['data'] = None
        else:
            data['data'] = _resize(data['data'],
                                   self.widget.width,
                                   self.widget.height)
            if form.applyChanges(
                self.context, self.form_fields, data, self.adapters):
                self.status = _('Image updated.')
        self.widget.session['changed'] = True

    @property
    def imageURL(self):
        baseURL = absoluteURL(hooks.getSite(), self.request)
        return baseURL + '/++session++%s/%s/++item++data/' %(
            SESSION_KEY, self.widget.name)


class ImageSessionWidgetForm(BrowserPage):
    """A form for the session widget to upload images.

    This form adapts the session widget (context) and the request.
    """

    def update(self):
        image = self.context.session['data']
        if not image:
            # show the add form and call update
            self.imageForm = AddImageForm(self.context, self.request)
            self.imageForm.update()
            if self.context.session['data']:
                # after adding a image show the edit form and return
                image = self.context.session['data']
                self.imageForm = EditImageForm(image, self.request)
                self.imageForm.widget = self.context
                self.imageForm.update()

        else:
            # show the edit form and call update
            self.imageForm = EditImageForm(image, self.request)
            self.imageForm.widget = self.context
            self.imageForm.update()
            if not self.context.session['data']:
                self.imageForm = AddImageForm(self.context, self.request)
                self.imageForm.update()


    def render(self):
        return self.imageForm()

    def __call__(self):
        self.update()
        return self.render()

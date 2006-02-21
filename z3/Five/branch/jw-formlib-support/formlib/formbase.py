##############################################################################
#
# Copyright (c) 2004, 2005 Zope Corporation and Contributors.
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
"""Five baseclasses for zope.formlib.form
"""
from datetime import datetime
import Acquisition

from zope import interface
import zope.event
import zope.app.event.objectevent
from zope.app.i18n import ZopeMessageFactory as _
from zope.formlib import interfaces, form, namedtemplate

from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from Products.Five.browser.decode import processInputs, setPageEncoding

class FiveFormlibMixin(Acquisition.Explicit):

    # Overrides the formlib.form.FormBase.template attributes implemented 
    # using NamedTemplates. NamedTemplates using ViewPageTemplateFile (like
    # formlib does by default) cannot work in Zope2.
    
    # XXX Maybe we need to have Five-compatible NamedTemplates?
    
    template = ZopeTwoPageTemplateFile('pageform.pt')
    
    # Overrides formlib.form.FormBase.update. Make sure user input is
    # decoded first and the page encoding is set before proceeding.
    
    def update(self):
        processInputs(self.request)
        setPageEncoding(self.request)
        super(FiveFormlibMixin, self).update()

class FormBase(FiveFormlibMixin, form.FormBase):
    pass
    
class EditFormBase(FiveFormlibMixin, form.EditFormBase):

    # Overrides formlib.form.EditFormBase.handle_edit_action, to remove
    # dependecy on request.locale
    
    @form.action(_("Apply"), condition=form.haveInputWidgets)
    def handle_edit_action(self, action, data):
        if form.applyChanges(
            self.context, self.form_fields, data, self.adapters):
            
            zope.event.notify(
                zope.app.event.objectevent.ObjectModifiedEvent(self.context)
                )
            # XXX: Needs locale support. See also Five.form.EditView.
            self.status = _(
                "Updated on ${date_time}", 
                mapping={'date_time': str(datetime.utcnow())}
                )
        else:
            self.status = _('No changes')
    
class DisplayFormBase(FiveFormlibMixin, form.DisplayFormBase):
    pass

class AddFormBase(FiveFormlibMixin, form.AddFormBase):
    pass
    
class PageForm(FormBase):

    interface.implements(interfaces.IPageForm)

Form = PageForm

class PageEditForm(EditFormBase):

    interface.implements(interfaces.IPageForm)

EditForm = PageEditForm

class PageDisplayForm(DisplayFormBase):

    interface.implements(interfaces.IPageForm)

DisplayForm = PageDisplayForm

class PageAddForm(AddFormBase):

    interface.implements(interfaces.IPageForm)

AddForm = PageAddForm

class SubPageForm(FormBase):

    template = ZopeTwoPageTemplateFile('subpageform.pt')
    
    interface.implements(interfaces.ISubPageForm)

class SubPageEditForm(EditFormBase):

    template = ZopeTwoPageTemplateFile('subpageform.pt')
    
    interface.implements(interfaces.ISubPageForm)

class SubPageDisplayForm(DisplayFormBase):

    template = ZopeTwoPageTemplateFile('subpageform.pt')
    
    interface.implements(interfaces.ISubPageForm)

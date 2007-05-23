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
$Id: __init__.py 69382 2006-08-09 13:26:53Z rogerineichen $
"""
__docformat__ = "reStructuredText"

import zope.interface
import zope.component
from zope.traversing.browser import absoluteURL
from z3c.configurator import configurator
from z3c.form import form
from z3c.form import field
from z3c.pagelet import browser
from z3c.template.interfaces import ILayoutTemplate
from z3c.website.i18n import MessageFactory as _
from z3c.website import interfaces
from z3c.website import session


class SampleAddForm(form.AddForm):
    """Reusable add form for standard ISample implementations.
    
    You must only define the getFactory method in your add form if you are not
    enhanced the ISample interface for your sample object.
    """

    label = _('You must define a own label in the sample add form.')

    contentName = None
    data = None

    # define your content class as a factory with a empty constructor
    # Note if you use a enhanced ISample interface you can still use this add 
    # form and provide the additional attributes in the edit form
    factory = None

    fields = field.Fields(
        zope.schema.TextLine(
            __name__='__name__',
            title=_(u"Name"),
            required=True))

    fields += field.Fields(interfaces.ISample).select('title', 'description',
        'keyword')

    def getFactory(self):
        raise NotImplementedError("Sub class must implement getFactory.")

    def create(self, data):
        self.data = data
        # get form data
        self.contentName = data.get('__name__', u'')

        # Create site
        obj = self.factory()
        obj.title = data.get('title', u'')
        obj.description = data.get('description', u'')
        obj.keyword = data.get('keyword', u'')
        return obj

    def add(self, obj):
        
        # Add the site
        if self.context.get(self.contentName) is not None:
            self.status = _('Page with that name already exist.')
            self._finished_add = False
            return None
        self.context[self.contentName] = obj

        # Configure the new obj
        configurator.configure(obj, self.data)

        self._finished_add = True
        return obj

    def nextURL(self):
        obj = self.context[self.contentName]
        return absoluteURL(obj, self.request) + '/edit.html'

    def __call__(self):
        self.update()
        layout = zope.component.getMultiAdapter((self, self.request),
            ILayoutTemplate)
        return layout(self)


class SampleMetaEditPagelet(form.EditForm):
    """Content edit page."""

    fields = field.Fields(interfaces.ISample).select('title', 'description',
        'keyword', 'headline', 'summary', 'author')

    def __call__(self):
        self.update()
        layout = zope.component.getMultiAdapter((self, self.request),
            ILayoutTemplate)
        return layout(self)


# Note, the ISample content edit form is located in the jquery.demo.resteditor
# because we use the JQuery based reSTructuredText Editor widget


class SessionDataEditForm(form.EditForm):
    """Sample edit form supporting storing content object in a session."""

    def getContentFactory(self):
        return session.SessionData

    def getContent(self):
        return session.getSessionData(self)

    def __call__(self):
        self.update()
        layout = zope.component.getMultiAdapter((self, self.request),
            ILayoutTemplate)
        return layout(self)

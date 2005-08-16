##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""Presentation component views.

$Id$
"""
__docformat__ = "reStructuredText"
from zope.app import zapi

class PageFolderDefaultConfiguration(object):
    "Make sure to update all page template registrations, when info changed"

    def changed(self):
        """Apply changes to existing configurations"""

        folder = self.context
        if folder.apply:
            folder.applyDefaults()


class Source(object):
    """Set the content type of the rendered template code."""
    def __call__(self):
        self.request.response.setHeader('content-type',
                                        self.context.contentType)
        return self.context.source


class PageRegistrationView(object):
    """Helper class for the page edit form."""

    def update(self):
        super(PageRegistrationView, self).update()
        if "UPDATE_SUBMIT" in self.request:
            self.context.validate()

class PageRegistrationDetails(object):

    def required(self):
        required = self.context.required
        return required.__module__ + '.' + required.__name__

    def name(self):
        return self.context.name or '<no name>'

    def template(self):
        url = zapi.getMultiAdapter(
            (self.context.template, self.request), name='absolute_url')
        name = zapi.name(self.context.template)
        return {'url': url, 'name': name}
    
